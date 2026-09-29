"""Compatibility boundary between MCP code and the upstream project.

All direct imports and assumptions about tchmaterial_parser live here.
MCP tools depend on this module instead of upstream internals.
"""

from __future__ import annotations

import os
import re
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from requests import RequestException

from .schemas import DownloadedResource, MaterialSummary, ResolvedResource
from .settings import download_directory


def _load_bundled_upstream() -> None:
    """Make the checked-out submodule importable without modifying it."""

    project_root = Path(__file__).resolve().parents[2]
    upstream_src = project_root / "upstream" / "tchMaterial-parser" / "src"
    if upstream_src.is_dir() and str(upstream_src) not in sys.path:
        sys.path.insert(0, str(upstream_src))


_load_bundled_upstream()

from tchmaterial_parser import config as upstream_config  # noqa: E402
from tchmaterial_parser.api import ResourceInfo, parse as upstream_parse  # noqa: E402
from tchmaterial_parser.bookmarks import add_bookmarks  # noqa: E402
from tchmaterial_parser.catalog import (  # noqa: E402
    ResourceHelper,
    count_resource_items,
    filter_resource_items,
)
from tchmaterial_parser.network import (  # noqa: E402
    REQUEST_TIMEOUT,
    request_headers,
    session,
)


_catalog_lock = threading.Lock()
_catalog_tree: dict[str, dict] | None = None
_catalog_by_id: dict[str, MaterialSummary] = {}

_TAG_FIELDS = {
    "zxxxd": "stage",
    "zxxxk": "subject",
    "zxxbb": "edition",
    "zxxnj": "grade",
    "zxxcc": "volume",
}

_PRIVATE_DOWNLOAD_HOSTS = tuple(f"r{index}-ndr-private.ykt.cbern.com.cn" for index in range(1, 4))
_DOWNLOAD_RETRY_DELAYS = (1.0, 3.0)
_INVALID_FILENAME_REPLACEMENTS = str.maketrans(
    {
        "<": "＜",
        ">": "＞",
        ":": "：",
        '"': "＂",
        "/": "／",
        "\\": "＼",
        "|": "｜",
        "?": "？",
        "*": "＊",
    }
)
_CONTROL_FILENAME_CHARS = re.compile(r"[\x00-\x1f]")
_WINDOWS_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}
)


def _iter_leaf_resources(
    items: dict[str, dict],
    parent_path: str = "",
    parent_names: tuple[str, ...] = (),
) -> Iterator[tuple[str, dict, tuple[str, ...]]]:
    for option_id, option_data in items.items():
        item_path = f"{parent_path}:{option_id}" if parent_path else option_id
        display_name = option_data.get("display_name") or option_data.get("title") or option_id
        path_names = (*parent_names, display_name)
        children = option_data.get("children") or {}
        if children:
            yield from _iter_leaf_resources(children, item_path, path_names)
        else:
            yield item_path, option_data, path_names


def _build_resource_url(item_path: str, resource_data: dict) -> str:
    resource_type = resource_data.get("resource_type_code") or "assets_document"
    content_id = resource_data.get("content_id") or item_path.split(":")[-1]
    root_id = item_path.split(":")[0]
    if resource_type == "teachingmaterials":
        prepare_path = "/prepare" if root_id == "__internal_prepare_lesson" else ""
        tag_path = "%2F".join(item_path.split(":")[1:])
        return f"https://basic.smartedu.cn/syncClassroom{prepare_path}?defaultTag={tag_path}"
    return (
        "https://basic.smartedu.cn/tchMaterial/detail"
        f"?contentType={resource_type}&contentId={content_id}"
        "&catalogType=tchMaterial&subCatalog=tchMaterial"
    )


def _material_summary(item_path: str, data: dict, path_names: tuple[str, ...]) -> MaterialSummary:
    tags: dict[str, str] = {}
    for tag in data.get("tag_list") or []:
        field = _TAG_FIELDS.get(tag.get("tag_dimension_id"))
        value = tag.get("tag_name")
        if field and value and field not in tags:
            tags[field] = value

    return {
        "resource_id": data.get("id") or item_path.split(":")[-1],
        "title": data.get("display_name") or data.get("title") or data.get("name") or item_path.split(":")[-1],
        "path": list(path_names),
        "stage": tags.get("stage"),
        "subject": tags.get("subject"),
        "edition": tags.get("edition"),
        "grade": tags.get("grade"),
        "volume": tags.get("volume"),
        "resource_type": data.get("resource_type_code") or "assets_document",
        "source_url": _build_resource_url(item_path, data),
    }


def _get_catalog(refresh: bool = False) -> dict[str, dict]:
    global _catalog_tree, _catalog_by_id

    with _catalog_lock:
        if _catalog_tree is None or refresh:
            tree = ResourceHelper().fetch_resource_list()
            index: dict[str, MaterialSummary] = {}
            for item_path, data, path_names in _iter_leaf_resources(tree):
                summary = _material_summary(item_path, data, path_names)
                index[summary["resource_id"]] = summary
            _catalog_tree = tree
            _catalog_by_id = index
        return _catalog_tree


def search_materials(query: str, limit: int = 20, refresh: bool = False) -> dict[str, object]:
    """Search the upstream material catalog using its native path filter."""

    limit = max(1, min(int(limit), 100))
    tree = _get_catalog(refresh=refresh)
    filtered = filter_resource_items(tree, query.strip())
    total = count_resource_items(filtered)
    materials: list[MaterialSummary] = []

    for item_path, data, path_names in _iter_leaf_resources(filtered):
        materials.append(_material_summary(item_path, data, path_names))
        if len(materials) >= limit:
            break

    return {
        "query": query,
        "total": total,
        "returned": len(materials),
        "materials": materials,
    }


def get_material(resource_id: str) -> MaterialSummary:
    """Return one catalog material by its stable upstream resource ID."""

    _get_catalog()
    material = _catalog_by_id.get(resource_id)
    if material is None:
        raise ValueError(f"未找到教材资源 ID：{resource_id}")
    return material


def _source_url(resource_id_or_url: str) -> str:
    value = resource_id_or_url.strip()
    if value.startswith(("http://", "https://")):
        parts = urlsplit(value)
        if parts.hostname != "basic.smartedu.cn":
            raise ValueError("仅支持 basic.smartedu.cn 的资源页面 URL")
        return value
    return get_material(value)["source_url"]


def _load_saved_credentials() -> None:
    """Reuse credentials saved by the upstream desktop application."""

    upstream_config.load_access_token(upstream_config.load_config())


def resolve_material(resource_id_or_url: str, include_bookmarks: bool = False) -> dict[str, object]:
    """Resolve a catalog ID or SmartEdu page URL into downloadable resources."""

    _load_saved_credentials()
    source_url = _source_url(resource_id_or_url)
    resources = upstream_parse(source_url, include_bookmarks)
    if not resources:
        raise ValueError("资源解析失败，或该页面没有可下载资源")

    resolved: list[ResolvedResource] = [
        {
            "title": resource.title,
            "file_format": resource.file_format,
            "edition": resource.edition,
            "relative_dir": list(resource.relative_dir),
            "download_url": resource.url,
            "chapters": resource.chapters,
        }
        for resource in resources
    ]
    return {
        "source_url": source_url,
        "resource_count": len(resolved),
        "resources": resolved,
    }


def _sanitize_filename(filename: str) -> str:
    filename = _CONTROL_FILENAME_CHARS.sub("_", filename.translate(_INVALID_FILENAME_REPLACEMENTS))
    filename = filename.rstrip(" .")
    if filename in ("", ".", ".."):
        return "download"

    stem, extension = os.path.splitext(filename)
    if stem.upper() in _WINDOWS_RESERVED_NAMES:
        return f"_{stem}{extension}"
    return filename


def _filename_key(path: Path) -> str:
    return os.path.normcase(str(path)).casefold()


def _allocate_download_paths(
    resources: list[ResourceInfo],
    root: Path,
    skip_existing: bool,
) -> list[Path]:
    reserved: set[str] = set()
    paths: list[Path] = []

    for resource in resources:
        filename = _sanitize_filename(f"{resource.title or 'download'}.{resource.file_format}")
        subdirectory = root.joinpath(*(_sanitize_filename(part) for part in resource.relative_dir))
        candidate = subdirectory / filename
        stem = candidate.with_suffix("")
        extension = candidate.suffix
        sequence = 2

        while (
            _filename_key(candidate) in reserved
            or Path(f"{candidate}.tmp").exists()
            or (candidate.exists() and not skip_existing)
        ):
            candidate = Path(f"{stem} ({sequence}){extension}")
            sequence += 1

        reserved.add(_filename_key(candidate))
        paths.append(candidate)

    return paths


def _download_mirror_urls(url: str) -> list[str]:
    parts = urlsplit(url)
    hostname = parts.hostname or ""
    if hostname not in _PRIVATE_DOWNLOAD_HOSTS:
        return [url]
    hosts = [hostname, *(host for host in _PRIVATE_DOWNLOAD_HOSTS if host != hostname)]
    return [urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment)) for host in hosts]


def _redact_access_token(text: str) -> str:
    return re.sub(r"([?&]accessToken=)[^&\s'\"]+", r"\1<redacted>", text, flags=re.IGNORECASE)


def _request_download(url: str):
    last_response = None
    last_exception: RequestException | None = None
    attempted = 0

    for candidate in _download_mirror_urls(url):
        attempted += 1
        retry = 0
        while True:
            try:
                response = session.get(
                    candidate,
                    headers=request_headers(candidate),
                    stream=True,
                    timeout=REQUEST_TIMEOUT,
                )
            except RequestException as exc:
                last_exception = exc
                break

            if last_response is not None:
                last_response.close()
            last_response = response

            if response.ok:
                return response, attempted
            if response.status_code in (401, 403):
                return response, attempted
            if response.status_code == 400 and retry < len(_DOWNLOAD_RETRY_DELAYS):
                time.sleep(_DOWNLOAD_RETRY_DELAYS[retry])
                retry += 1
                continue
            if response.status_code == 400:
                return response, attempted
            break

    if last_response is not None:
        return last_response, attempted
    if last_exception is not None:
        raise RuntimeError(_redact_access_token(str(last_exception))) from None
    raise RuntimeError("没有可用的下载地址")


def _download_error(response, attempted: int) -> str:
    reason = f"服务器返回 HTTP 状态码 {response.status_code}"
    if response.status_code in (401, 403):
        if upstream_config.access_token:
            reason += "，Access Token 可能已过期或无效"
        else:
            reason += "，该资源需要有效的 Access Token"
    elif response.status_code == 400:
        reason += "，私有资源暂时无法访问；可稍后重试，持续失败时请重新设置 Token"
    if attempted > 1:
        reason += f"，已尝试 {attempted} 个下载镜像"
    return reason


def _download_one(resource: ResourceInfo, path: Path) -> int:
    temp_path = Path(f"{path}.tmp")
    response = None
    try:
        response, attempted = _request_download(resource.url)
        if not response.ok:
            raise RuntimeError(_download_error(response, attempted))

        expected = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        with temp_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=262144):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)

        if expected > 0 and downloaded != expected:
            raise RuntimeError(f"文件下载不完整：期望 {expected} 字节，实际 {downloaded} 字节")

        if resource.chapters and resource.file_format.casefold() == "pdf":
            add_bookmarks(str(temp_path), resource.chapters)

        os.replace(temp_path, path)
        return downloaded
    except Exception:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    finally:
        if response is not None:
            response.close()


def download_material(
    resource_id_or_url: str,
    add_pdf_bookmarks: bool = True,
    skip_existing: bool = True,
) -> dict[str, object]:
    """Resolve and download all files associated with one material page."""

    _load_saved_credentials()
    source_url = _source_url(resource_id_or_url)
    resources = upstream_parse(source_url, add_pdf_bookmarks)
    if not resources:
        raise ValueError("资源解析失败，或该页面没有可下载资源")

    root = download_directory()
    root.mkdir(parents=True, exist_ok=True)
    paths = _allocate_download_paths(resources, root, skip_existing=skip_existing)
    results: list[DownloadedResource] = []

    for resource, path in zip(resources, paths):
        if skip_existing and path.exists():
            results.append(
                {
                    "title": resource.title,
                    "file_format": resource.file_format,
                    "status": "skipped",
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "error": None,
                }
            )
            continue

        try:
            downloaded = _download_one(resource, path)
            results.append(
                {
                    "title": resource.title,
                    "file_format": resource.file_format,
                    "status": "downloaded",
                    "path": str(path),
                    "bytes": downloaded,
                    "error": None,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "title": resource.title,
                    "file_format": resource.file_format,
                    "status": "failed",
                    "path": str(path),
                    "bytes": 0,
                    "error": _redact_access_token(str(exc)),
                }
            )

    return {
        "source_url": source_url,
        "download_root": str(root),
        "downloaded": sum(item["status"] == "downloaded" for item in results),
        "skipped": sum(item["status"] == "skipped" for item in results),
        "failed": sum(item["status"] == "failed" for item in results),
        "files": results,
    }

