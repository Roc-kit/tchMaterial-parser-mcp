# Architecture

## Goal

本仓库是上游 tchMaterial-parser 的 MCP wrapper，而不是长期 fork。

核心原则：

1. 上游源码保持独立。
2. MCP 对外接口保持稳定。
3. 上游变化集中由 adapter 层吸收。
4. 更新上游时尽量只产生一个 submodule 指针变化。

## Dependency direction

    AI client
       |
    MCP server
       |
    MCP tools / schemas
       |
    adapters.py
       |
    upstream/tchMaterial-parser
       |
    国家中小学智慧教育平台

server.py、tools.py、schemas.py 不应直接依赖上游内部模块。

所有类似下面的引用应集中在 adapters.py：

    from tchmaterial_parser.api import parse
    from tchmaterial_parser.catalog import ResourceHelper

这样上游函数重命名、参数变化或返回结构变化时，只需要修复兼容层。

## Upstream ownership

upstream/tchMaterial-parser/ 是 Git submodule。它的所有权属于上游项目，本仓库只固定一个已验证 commit。

默认不在 submodule 内维护私有 patch。

