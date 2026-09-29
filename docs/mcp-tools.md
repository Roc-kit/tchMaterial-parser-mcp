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

返回文件标题、格式、版本、分类目录、下载 URL 和章节信息，同时返回：

- pdf_count：PDF 数量。
- non_pdf_count：非 PDF 关联资源数量。
- has_related_resources：是否存在 MP3 等关联资源。
- file_formats：当前页面包含的文件格式。

## download_material

解析并下载教材页面关联的所有资源。

参数：

- resource_id_or_url: 必填。
- add_pdf_bookmarks: 默认 true。
- skip_existing: 默认 true。
- pdf_only: 默认 true。只下载 PDF；显式设为 false 才会下载关联音频等其他资源。

下载根目录由服务端环境变量 TCHMATERIAL_MCP_DOWNLOAD_DIR 控制；默认使用 ~/Downloads/tchMaterial-parser。tool 本身没有任意 output_dir 参数。

英语教材页面通常还关联大量 MP3。推荐交互流程：

1. 用户提出下载教材。
2. AI 先调用 resolve_material。
3. 如果 has_related_resources=false，直接按 PDF 下载。
4. 如果 has_related_resources=true，且用户尚未说明是否需要配套资源，先询问：
   “只下载 PDF，还是连配套音频等资源一起下载？”
5. 用户未特别要求时，使用默认 pdf_only=true。

因此默认行为仍然是只下载教材 PDF，不会自动把几十个 MP3 一并下载。

返回每个文件的 status：

- downloaded
- skipped
- failed

同时返回本地 path、文件大小和失败原因。Access Token 不会作为 tool 输出返回。

## 凭据

MCP Server 复用 tchMaterial-parser 桌面程序已经保存的本地登录凭据。每次解析或下载前重新读取本机配置，不要求模型传 Token。

