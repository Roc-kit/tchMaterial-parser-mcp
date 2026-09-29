from tchmaterial_parser_mcp import adapters, tools


def test_search_tool_delegates_to_adapter(monkeypatch) -> None:
    expected = {"query": "数学", "total": 0, "returned": 0, "materials": []}
    monkeypatch.setattr(adapters, "search_materials", lambda query, limit, refresh: expected)

    assert tools.search_materials("数学", limit=5, refresh=True) == expected


def test_download_tool_has_no_output_directory_parameter() -> None:
    annotations = tools.download_material.__annotations__
    assert "output_dir" not in annotations

