from tchmaterial_parser_mcp import adapters, tools


def test_search_tool_delegates_to_adapter(monkeypatch) -> None:
    expected = {"query": "数学", "total": 0, "returned": 0, "materials": []}
    monkeypatch.setattr(adapters, "search_materials", lambda query, limit, refresh: expected)

    assert tools.search_materials("数学", limit=5, refresh=True) == expected


def test_download_tool_has_no_output_directory_parameter() -> None:
    annotations = tools.download_material.__annotations__
    assert "output_dir" not in annotations


def test_download_tool_defaults_to_pdf_only(monkeypatch) -> None:
    captured = {}

    def fake_download(resource_id_or_url, add_pdf_bookmarks, skip_existing, pdf_only):
        captured.update(
            resource_id_or_url=resource_id_or_url,
            add_pdf_bookmarks=add_pdf_bookmarks,
            skip_existing=skip_existing,
            pdf_only=pdf_only,
        )
        return {"files": []}

    monkeypatch.setattr(adapters, "download_material", fake_download)

    tools.download_material("book-1")

    assert captured["pdf_only"] is True

