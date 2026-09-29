# tchMaterial-parser-mcp

为 happycola233/tchMaterial-parser 提供 MCP（Model Context Protocol）适配层，使 AI 客户端可以调用教材搜索、解析与下载等能力。

本项目采用 wrapper repository + Git submodule 结构。上游 tchMaterial-parser 保持独立，不把 MCP 逻辑侵入上游源码。

## 目录

    tchMaterial-parser-mcp/
    ├── upstream/
    │   └── tchMaterial-parser/       # 官方仓库 Git submodule
    ├── src/
    │   └── tchmaterial_parser_mcp/
    │       ├── adapters.py           # 上游兼容边界
    │       ├── schemas.py            # MCP 稳定数据结构
    │       ├── tools.py              # MCP tools
    │       └── server.py             # MCP server
    ├── tests/
    ├── docs/
    └── scripts/

## 克隆

    git clone --recurse-submodules <this-repository-url>
    cd tchMaterial-parser-mcp

如果已经普通 clone：

    git submodule update --init --recursive

## 开发环境

当前环境推荐使用 uv：

    uv venv .venv
    source .venv/bin/activate
    uv pip install --python .venv/bin/python -e ./upstream/tchMaterial-parser
    uv pip install --python .venv/bin/python -e ".[dev]"

也可以使用标准 venv：

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e ./upstream/tchMaterial-parser
    python -m pip install -e ".[dev]"

## 上游更新

    ./scripts/update-upstream.sh

脚本会把 submodule 更新到官方 main 最新提交，然后运行上游兼容性测试。外层仓库最终只记录新的 submodule commit 指针。

详细约束见：

- docs/architecture.md
- docs/upstream-maintenance.md
- docs/mcp-tools.md

## 当前状态

仓库基础结构、Git submodule 和上游兼容边界已经建立。MCP tool 的具体实现将在此结构上继续开发。

