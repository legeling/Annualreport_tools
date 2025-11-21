# Annualreport_tools · 年报工具集（中文）

> 本仓库 README 默认展示英文版，中文说明请参阅此文档；若需要英文内容，可访问 [docs/README.en.md](./README.en.md)。

## 免责声明
- 本项目仅供学习交流，请勿将脚本用于任何违法违规的商业或批量爬虫用途。
- 若无必要，请优先使用已整理好的网盘年报数据，避免频繁访问巨潮资讯服务器，尊重源站资源与相关监管要求。
- 使用本脚本所产生的行为与风险，由使用者自行承担。

## 核心能力
1. 巨潮资讯年报爬虫：按板块、行业拆分请求，稳定抓取深沪交易所公告。
2. 鲁棒 PDF 下载器：自动重试、MIME 校验、文件完整性检测，拒绝空文件与 HTML 异常页。
3. 批量转码工具链：将 PDF 批量转换为 UTF-8 TXT，可选删除源文件节省磁盘。
4. 多进程词频分析：自动利用多核 CPU，显著缩短成千上万 TXT 的统计时间。
5. 通用文本分析脚本：拖入任何 TXT 目录即可生成 Excel 词频仪表盘。

## 快速上手
1. 安装依赖：`pip install -r requirements.txt`
2. 运行 `report_link_crawler.py` 获取指定年份公告（或直接使用仓库内 `年报链接2004-2023.xlsx`）。
3. 执行 `pdf_batch_converter.py` 批量下载 PDF 并转换为 TXT；可选保留 / 删除原始 PDF。
4. 使用升级后的 `text_analysis.py`（多进程）或 `text_analysis_universal.py`，输出包含总词数与关键词列的 Excel。
5. 参考 [Wiki](https://github.com/legeling/Annualreport_tools/wiki) 或 `docs/` 中的语言版本，完成自动化流水线。

## 标签
`Annual Report` · `CNINFO` · `Crawler` · `PDF` · `TXT` · `Jieba` · `NLP` · `Automation` · `Financial Data` · `Data Engineering` · `Keyword Stats` · `Python`

## 模块概览
| 脚本/资源 | 说明 |
| --- | --- |
| `report_link_crawler.py` | 巨潮公告爬虫，支持板块 / 行业过滤与重试机制 |
| `pdf_batch_converter.py` | 批量下载 + pdfplumber 转码，校验文件合法性 |
| `text_analysis.py` | 多进程词频分析，写入 Excel 并展示总词数 |
| `text_analysis_universal.py` | 通用 TXT 文件夹分析脚本 |
| `年报链接2004-2023.xlsx` | 预制年报链接总表，覆盖 2004-2023 年 |

## 多语言文档
- [README.zh.md](./README.zh.md) — 当前中文版本
- [README.en.md](./README.en.md) — English manual
