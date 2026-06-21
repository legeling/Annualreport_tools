# 实现文档

## 技术栈

- 桌面框架：Tauri
- 后端能力：Rust commands
- 前端：Vite + TypeScript
- PDF 转文本：MVP 阶段复用 Python 脚本
- 文本分析：MVP 阶段复用 Python 脚本，后续可迁移到 Rust

## 当前状态

项目已经整理为标准目录：

```text
/Users/lingxiaotian/development/personal/Annualreport_tools/desktop
```

当前已完成：

- 移除旧中文嵌套目录。
- 统一项目名为 `annualreport-desktop`。
- 创建桌面工作台前端原型。
- 建立 `docs/` 文档目录。

当前未完成：

- Excel 解析尚未接入。
- 本地持久化尚未接入。
- PDF 下载尚未接入。
- PDF 打开和预览尚未接入。
- Python 转换与分析脚本尚未接入。

## 模块划分

### 前端模块

1. `reports`
   - 查询年报列表
   - 应用筛选条件
   - 管理选中记录

2. `documents`
   - 管理导入的 Excel 文件
   - 管理 PDF 保存目录
   - 管理 TXT 和分析输出目录

3. `downloads`
   - 展示下载状态
   - 控制下载任务
   - 处理失败重试

4. `analysis`
   - 触发 PDF 转文本
   - 触发关键词分析
   - 打开分析结果

### Rust command 规划

建议第一批 Tauri commands：

```rust
import_report_excel(path: String) -> Result<ImportSummary, String>
list_reports(filter: ReportFilter) -> Result<Vec<ReportRecord>, String>
open_report_url(url: String) -> Result<(), String>
download_report_pdf(record_id: String) -> Result<DownloadResult, String>
open_local_pdf(path: String) -> Result<(), String>
convert_pdf_to_text(record_id: String) -> Result<ConvertResult, String>
run_keyword_analysis(record_id: String) -> Result<AnalysisResult, String>
open_output_dir(path: String) -> Result<(), String>
```

## 数据存储方案

MVP 可以先使用应用数据目录中的 JSON 文件：

```text
app-data/
├── library.json
├── reports.json
├── downloads/
├── texts/
└── analysis/
```

后续数据量变大后再迁移到 SQLite。

## Excel 导入策略

Rust 侧可选方案：

- `calamine`：读取 xlsx/xls，适合直接在 Rust 里解析。
- Python 脚本：继续复用现有 `openpyxl` 流程，Rust 只负责调用。

建议 MVP 先用 Rust 的 `calamine`，减少 Python 环境依赖；PDF 转文本和文本分析再复用 Python。

## PDF 下载策略

- 默认单任务下载。
- 批量任务并发数限制为 1 到 2。
- 对失败任务记录错误原因。
- 不实现高并发爬虫和日期遍历采集。

## PDF 预览策略

MVP：

- 调用系统默认阅读器打开本地 PDF。
- 对未下载记录提供打开远程链接。

后续版本：

- 使用 WebView 加载本地 PDF 文件。
- 增加页码、缩放、搜索等控件。

## Python 脚本集成策略

保留 Python 脚本作为处理后端：

- PDF 转 TXT
- 关键词统计
- Excel 导出

Rust 侧通过 `std::process::Command` 调用，并捕获 stdout/stderr。需要在界面中展示任务状态和错误信息。

## 开发顺序

1. 建立前端类型和静态数据模型。
2. 实现 Excel 导入 command。
3. 实现本地 JSON 持久化。
4. 接入真实列表查询和筛选。
5. 实现打开远程链接、本地 PDF。
6. 实现单个 PDF 下载。
7. 接入 PDF 转文本。
8. 接入关键词分析。
9. 增加下载队列和任务日志。
10. 打包测试。

## 验证命令

```bash
npm run build
cd src-tauri && cargo check
```

开发预览：

```bash
npm run dev
```
