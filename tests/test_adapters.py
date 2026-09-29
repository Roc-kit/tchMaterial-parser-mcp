from pathlib import Path

from tchmaterial_parser.api import ResourceInfo

from tchmaterial_parser_mcp import adapters


def test_material_summary_exposes_stable_fields() -> None:
    data = {
        "id": "book-1",
        "display_name": "数学五年级上册",
        "resource_type_code": "assets_document",
        "tag_list": [
            {"tag_dimension_id": "zxxxd", "tag_name": "小学"},
            {"tag_dimension_id": "zxxxk", "tag_name": "数学"},
            {"tag_dimension_id": "zxxbb", "tag_name": "人教版"},
            {"tag_dimension_id": "zxxnj", "tag_name": "五年级"},
            {"tag_dimension_id": "zxxcc", "tag_name": "上册"},
        ],
    }

    summary = adapters._material_summary("root:book-1", data, ("电子教材", "小学", "数学", "数学五年级上册"))

    assert summary["resource_id"] == "book-1"
    assert summary["stage"] == "小学"
    assert summary["subject"] == "数学"
    assert summary["edition"] == "人教版"
    assert summary["grade"] == "五年级"
    assert summary["volume"] == "上册"
    assert "contentId=book-1" in summary["source_url"]


def test_source_url_rejects_non_smartedu_host() -> None:
    try:
        adapters._source_url("https://example.com/tchMaterial/detail?contentId=x")
    except ValueError as exc:
        assert "basic.smartedu.cn" in str(exc)
    else:
        raise AssertionError("non-SmartEdu URL should be rejected")


def test_allocate_paths_stays_under_download_root(tmp_path: Path) -> None:
    resource = ResourceInfo(
        title="../数学/五年级",
        url="https://example.invalid/file.pdf",
        file_format="pdf",
        chapters=[],
        edition="人教版",
        relative_dir=("小学", "数学", "人教版"),
    )

    path = adapters._allocate_download_paths([resource], tmp_path, skip_existing=True)[0]

    assert path.is_relative_to(tmp_path)
    assert path.parent == tmp_path / "小学" / "数学" / "人教版"
    assert "/" not in path.name


def test_download_one_writes_atomically(monkeypatch, tmp_path: Path) -> None:
    class FakeResponse:
        ok = True
        status_code = 200
        headers = {"Content-Length": "6"}

        def iter_content(self, chunk_size: int):
            assert chunk_size > 0
            yield b"abc"
            yield b"def"

        def close(self) -> None:
            pass

    monkeypatch.setattr(adapters, "_request_download", lambda _url: (FakeResponse(), 1))
    resource = ResourceInfo("示例", "https://example.invalid/a.pdf", "pdf", [], None, ())
    target = tmp_path / "示例.pdf"

    size = adapters._download_one(resource, target)

    assert size == 6
    assert target.read_bytes() == b"abcdef"
    assert not Path(f"{target}.tmp").exists()


def test_download_material_filters_related_audio_by_default(monkeypatch, tmp_path: Path) -> None:
    resources = [
        ResourceInfo("教材", "https://example.invalid/book.pdf", "pdf", [], None, ()),
        ResourceInfo("配套听力", "https://example.invalid/audio.mp3", "mp3", [], None, ()),
    ]
    monkeypatch.setattr(adapters, "_source_url", lambda _value: "https://basic.smartedu.cn/example")
    monkeypatch.setattr(adapters, "_load_saved_credentials", lambda: None)
    monkeypatch.setattr(adapters, "upstream_parse", lambda _url, _bookmarks: resources)
    monkeypatch.setattr(adapters, "download_directory", lambda: tmp_path)
    monkeypatch.setattr(adapters, "_download_one", lambda resource, path: 123)

    result = adapters.download_material("book-1")

    assert len(result["files"]) == 1
    assert result["files"][0]["file_format"] == "pdf"


def test_resolve_material_reports_related_resources(monkeypatch) -> None:
    resources = [
        ResourceInfo("教材", "https://example.invalid/book.pdf", "pdf", [], None, ()),
        ResourceInfo("配套听力", "https://example.invalid/audio.mp3", "mp3", [], None, ()),
    ]
    monkeypatch.setattr(adapters, "_load_saved_credentials", lambda: None)
    monkeypatch.setattr(adapters, "_source_url", lambda _value: "https://basic.smartedu.cn/example")
    monkeypatch.setattr(adapters, "upstream_parse", lambda _url, _bookmarks: resources)

    result = adapters.resolve_material("book-1")

    assert result["pdf_count"] == 1
    assert result["non_pdf_count"] == 1
    assert result["has_related_resources"] is True
    assert result["file_formats"] == ["mp3", "pdf"]

