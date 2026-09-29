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

## 初始化

    ./scripts/setup.sh

脚本会初始化 submodule、创建 .venv、安装 MCP SDK 和本项目，并运行测试。
同时会以 editable 模式安装当前 submodule，因此 MCP 使用的就是外层仓库固定的上游 commit。

启动本地 stdio MCP Server：

    ./scripts/run-mcp.sh

该命令正常启动后不会打印业务输出，而是等待 MCP Host 通过 stdin/stdout 通信。

运行不下载文件的在线冒烟测试：

    ./scripts/smoke-live.sh

## 上游更新

    ./scripts/update-upstream.sh

脚本会把 submodule 更新到官方 main 最新提交，然后运行上游兼容性测试。外层仓库最终只记录新的 submodule commit 指针。

## 下载目录

默认下载到：

    ~/Downloads/tchMaterial-parser

可以通过环境变量修改：

    TCHMATERIAL_MCP_DOWNLOAD_DIR=/path/to/materials

download_material 不接受任意输出目录参数，避免模型把文件写到未授权的系统位置。

## Codex

本地 stdio 启动命令为：

    /home/cislunar/App/tchMaterial-parser-mcp/scripts/run-mcp.sh

推荐给下载 tool 配置较长超时时间，因为大体积 PDF 可能超过普通 MCP tool 的默认超时。

详细约束见：

- docs/architecture.md
- docs/upstream-maintenance.md
- docs/mcp-tools.md
- THIRD_PARTY_NOTICES.md

## 当前状态

第一版已提供 search_materials、get_material、resolve_material、download_material 四个 MCP Tool，并使用官方 MCP Python SDK v2 的 stdio transport。

