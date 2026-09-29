from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "tchmaterial_parser_mcp"


def test_only_adapter_may_import_upstream_package() -> None:
    violations: list[str] = []

    for path in PACKAGE.glob("*.py"):
        if path.name == "adapters.py":
            continue
        source = path.read_text(encoding="utf-8")
        if "from tchmaterial_parser." in source or "import tchmaterial_parser." in source:
            violations.append(path.name)

    assert not violations, f"Direct upstream imports must stay in adapters.py: {violations}"

