# Upstream maintenance

## 更新

优先运行：

    ./scripts/update-upstream.sh

脚本会：

1. 初始化 submodule；
2. fetch 官方 main；
3. 将 submodule 切到最新 origin/main commit；
4. 运行兼容性测试。

更新后检查：

    git diff --submodule=log
    git status

正常情况下，上游更新本身只应表现为 submodule SHA 从 old commit 变为 new commit。

如果测试失败：

1. 先检查上游 API/结构变化；
2. 优先修改 src/tchmaterial_parser_mcp/adapters.py；
3. 必要时调整 MCP 内部 schema；
4. 不直接修改 submodule 来修兼容问题。

## 回滚

外层仓库记录了 submodule commit，因此可以通过恢复外层 commit 或指定旧 SHA 回到已验证版本：

    git checkout <outer-commit>
    git submodule update --init --recursive

