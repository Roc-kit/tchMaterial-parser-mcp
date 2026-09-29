from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_PACKAGE = ROOT / "upstream" / "tchMaterial-parser" / "src" / "tchmaterial_parser"


def _top_level_symbols(path: Path) -> tuple[set[str], dict[str, set[str]]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions: set[str] = set()
    classes: dict[str, set[str]] = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
        elif isinstance(node, ast.ClassDef):
            methods = {
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            classes[node.name] = methods

    return functions, classes


def test_upstream_submodule_is_present() -> None:
    assert (UPSTREAM_PACKAGE / "api.py").is_file()
    assert (UPSTREAM_PACKAGE / "catalog.py").is_file()
    assert (UPSTREAM_PACKAGE / "auth.py").is_file()


def test_parse_api_contract_still_exists() -> None:
    functions, _ = _top_level_symbols(UPSTREAM_PACKAGE / "api.py")
    assert "parse" in functions


def test_catalog_api_contract_still_exists() -> None:
    functions, classes = _top_level_symbols(UPSTREAM_PACKAGE / "catalog.py")
    assert "filter_resource_items" in functions
    assert "count_resource_items" in functions
    assert "ResourceHelper" in classes
    assert "fetch_book_list" in classes["ResourceHelper"]
    assert "fetch_resource_list" in classes["ResourceHelper"]


def test_auth_api_contract_still_exists() -> None:
    functions, _ = _top_level_symbols(UPSTREAM_PACKAGE / "auth.py")
    assert "parse_token_input" in functions

