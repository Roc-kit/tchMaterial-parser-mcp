"""MCP tool implementations."""

from __future__ import annotations

from . import adapters


def search_materials(query: str, limit: int = 20, refresh: bool = False) -> dict[str, object]:
    """搜索国家中小学智慧教育平台电子教材。

    query 支持用空格组合学段、学科、版本、年级、册次或标题关键词，例如
    “小学 数学 人教版 五年级 上册”。limit 最大为 100。refresh=true 会重新
    获取官方教材目录。
    """

    return adapters.search_materials(query=query, limit=limit, refresh=refresh)


def get_material(resource_id: str) -> dict[str, object]:
    """根据 search_materials 返回的 resource_id 获取教材详情和官方页面 URL。"""

    return adapters.get_material(resource_id)


def resolve_material(resource_id_or_url: str, include_bookmarks: bool = False) -> dict[str, object]:
    """解析教材 ID 或 basic.smartedu.cn 教材页面 URL。

    返回实际可下载资源、文件格式、版本和分类目录，并给出 pdf_count、
    non_pdf_count、has_related_resources。include_bookmarks=true 时还会解析
    PDF 章节目录，但会产生额外网络请求。
    """

    return adapters.resolve_material(resource_id_or_url, include_bookmarks=include_bookmarks)


def download_material(
    resource_id_or_url: str,
    add_pdf_bookmarks: bool = True,
    skip_existing: bool = True,
    pdf_only: bool = True,
) -> dict[str, object]:
    """下载教材 ID 或教材页面对应的资源到服务端固定下载目录。

    下载根目录由 TCHMATERIAL_MCP_DOWNLOAD_DIR 配置；未配置时使用
    ~/Downloads/tchMaterial-parser。模型不能通过此工具指定任意系统路径。
    默认只下载 PDF。若用户没有明确说明是否需要配套音频/其他关联资源，
    在调用本工具前应先调用 resolve_material；当 has_related_resources=true 时，
    先询问用户“只下载 PDF，还是连配套资源一起下载？”。用户未特别要求时，
    保持 pdf_only=true。只有用户明确要求配套资源时才设置 pdf_only=false。
    默认给 PDF 添加可解析到的章节书签，并跳过已经完整存在的同名文件。
    """

    return adapters.download_material(
        resource_id_or_url,
        add_pdf_bookmarks=add_pdf_bookmarks,
        skip_existing=skip_existing,
        pdf_only=pdf_only,
    )

