# MCP Tools

本文件记录 MCP 对外 tool 契约。对外参数一旦投入使用，应尽量保持向后兼容；上游变化由 adapter 层处理。

## search_materials

搜索电子教材目录。

参数：

- query: 必填。可组合学段、学科、版本、年级、册次、标题关键词。
- limit: 默认 20，范围限制为 1-100。
- refresh: 默认 false。true 时重新读取官方资源目录。

返回 total、returned 和 materials。每个教材包含 resource_id、标题、分类路径、学段、学科、版本、年级、册次和官方页面 URL。

示例查询：

    小学 数学 人教版 五年级 上册

## get_material

根据 search_materials 返回的 resource_id 获取一个教材的目录元数据。

参数：

- resource_id: 必填。

此 tool 不下载文件。

## resolve_material

把 resource_id 或 basic.smartedu.cn 教材页面 URL 解析成实际资源。

参数：

- resource_id_or_url: 必填。
- include_bookmarks: 默认 false。true 时额外解析 PDF 章节书签。

返回文件标题、格式、版本、分类目录、下载 URL 和章节信息。

## download_material

解析并下载教材页面关联的所有资源。

参数：

- resource_id_or_url: 必填。
- add_pdf_bookmarks: 默认 true。
- skip_existing: 默认 true。

下载根目录由服务端环境变量 TCHMATERIAL_MCP_DOWNLOAD_DIR 控制；默认使用 ~/Downloads/tchMaterial-parser。tool 本身没有任意 output_dir 参数。

返回每个文件的 status：

- downloaded
- skipped
- failed

同时返回本地 path、文件大小和失败原因。Access Token 不会作为 tool 输出返回。

## 凭据

MCP Server 复用 tchMaterial-parser 桌面程序已经保存的本地登录凭据。每次解析或下载前重新读取本机配置，不要求模型传 Token。

