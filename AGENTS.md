# tchMaterial-parser-mcp Agent Guide

本仓库是 tchMaterial-parser 的 MCP 适配项目。核心目标是长期跟随上游更新，同时把本仓库维护的代码与上游源码严格隔离。

## 目录边界

- upstream/tchMaterial-parser/ 是 happycola233/tchMaterial-parser 的 Git submodule。
- 原则上禁止直接修改 upstream/tchMaterial-parser/ 中的源码。
- MCP 实现统一放在 src/tchmaterial_parser_mcp/。
- 上游 API 的兼容处理统一放在 src/tchmaterial_parser_mcp/adapters.py，MCP tool 不要直接依赖上游内部实现。
- MCP 相关测试统一放在本仓库 tests/。
- 文档统一放在本仓库 docs/。

如果确实必须修改上游源码，应先说明为什么无法在适配层解决，并将该改动视为独立 upstream patch，而不是混入普通 MCP 开发。

## 上游更新规则

1. 更新前确认外层工作区没有未处理的改动。
2. 只更新 submodule 指针，不复制或 vendor 上游源码。
3. 上游更新后先运行兼容性测试。
4. 如果兼容性测试失败，优先修改 adapters.py，不要直接修改上游。
5. 外层提交应清楚记录更新到的上游 commit。

推荐使用 scripts/update-upstream.sh。

## 开发规则

- Python 最低版本保持与上游一致：Python 3.10+。
- MCP 对外 tool/schema 尽量保持稳定；上游变化由 adapter 层吸收。
- 不把 Access Token、Cookie、账号凭据或下载鉴权信息返回给模型。
- 不在 Git 中提交明文 Token 或本机私密配置。
- MCP 下载类工具应返回结构化结果和本地路径，不把大体积文件内容直接塞进 tool result。
- 修改 MCP tool 的参数或返回结构时，同步更新 docs/mcp-tools.md 和测试。
- 修改完成后至少运行 python3 -m pytest（进入虚拟环境后可使用 python -m pytest）。

## Git

- main 保存可工作的 MCP 版本与已验证的上游 submodule 指针。
- 不把上游 Git 历史 squash/copy 到外层仓库。
- 未经明确要求不要 push 到远程仓库。
- commit message 使用 Conventional Commits。

