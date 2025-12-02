<div align="center">
  <img src="https://raw.githubusercontent.com/legeling/Annualreport_tools/main/imgs/icon.svg" width="96" alt="Annualreport Tools Icon" />
  <h1>Annualreport_tools · 年报工具集</h1>
  <p>快速抓取巨潮资讯年报、批量下载PDF、转换为TXT，并进行关键词分析。</p>
  <p>
    <a href="https://github.com/legeling/Annualreport_tools/stargazers"><img src="https://img.shields.io/github/stars/legeling/Annualreport_tools?style=flat-square" alt="GitHub Stars"/></a>
    <a href="https://github.com/legeling/Annualreport_tools/network/members"><img src="https://img.shields.io/github/forks/legeling/Annualreport_tools?style=flat-square" alt="GitHub Forks"/></a>
    <a href="https://github.com/legeling/Annualreport_tools/watchers"><img src="https://img.shields.io/github/watchers/legeling/Annualreport_tools?style=flat-square" alt="GitHub Watchers"/></a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version"/>
    <a href="https://github.com/legeling/Annualreport_tools/issues"><img src="https://img.shields.io/github/issues/legeling/Annualreport_tools?style=flat-square" alt="GitHub Issues"/></a>
  </p>
</div>

<p align="center">
  <a href="../README.md">English</a> ·
  <a href="./README.zh.md">简体中文</a>
</p>

![演示截图](https://cdn.nlark.com/yuque/0/2023/png/22569186/1684739594091-379cdf84-28f5-4998-835f-7c9555fddac7.png#averageHue=%23a8c1db&clientId=uc29edf23-5138-4&from=paste&height=687&id=ua755022a&originHeight=1374&originWidth=2560&originalType=binary&ratio=2&rotation=0&showTitle=false&size=944474&status=done&style=none&taskId=ucc34614d-4b0d-48dc-a316-949d41f13b8&title=&width=1280)

---

## 免责声明

**重要提示：**

- 本项目**仅供学习研究使用**，请勿用于任何违法违规的爬虫行为、商业转售或其他违反法律法规的活动。
- 请**优先使用已整理好的网盘数据集**（`./res/AnnualReport_links_2004_2023.xlsx`），该文件已包含下载好的年报链接。避免频繁访问巨潮资讯服务器，尊重源站资源与相关监管要求。
- **限速至关重要**：爬虫实现了按天分片的机制以最小化服务器负载。请不要修改代码以增加请求频率。
- 您对使用这些脚本触发的任何数据收集行为**负全部责任**。作者不对滥用行为承担任何责任。
- 使用本工具集即表示您已阅读并同意本免责声明。

## 核心功能

1. **report_link_crawler.py** – 按板块/行业分段查询巨潮资讯，在速率限制下保持稳定。
2. **pdf_batch_converter.py** – 具有MIME验证的鲁棒PDF下载器 + 转换为TXT。
3. **text_analysis.py** – 多进程关键词分析器 + Excel导出。
4. **text_analysis_universal.py** – 接受任意TXT目录的轻量级分析器。
5. **资源文件（`/res`）** – 精选的年报主表和文档图标资源。
6. **文档文件夹** – 存储在`docs/`下的双语文档，方便切换。

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 运行 `1.report_link_crawler.py`（或复用 `./res/AnnualReport_links_2004_2023.xlsx`）准备年报链接。
3. 执行 `2.pdf_batch_converter.py` 下载PDF并转换为TXT；可选择之后删除原始PDF。
4. 启动 `3.text_analysis.py`（多进程）或 `text_analysis_universal.py` 生成Excel中的关键词总计和总词数。
5. 查看 [Wiki](https://github.com/legeling/Annualreport_tools/wiki) 或 `docs/` 获取特定语言的详细教程。

## 模块概览

| 脚本/资源 | 说明 |
| --- | --- |
| `1.report_link_crawler.py` | 带板块/行业过滤器和重试逻辑的巨潮资讯爬虫 |
| `2.pdf_batch_converter.py` | 批量下载 + pdfplumber转换，带文件验证 |
| `3.text_analysis.py` | 多进程关键词分析，Excel导出 |
| `text_analysis_universal.py` | 适用于任意TXT文件夹的轻量级分析器 |
| `./res/AnnualReport_links_2004_2023.xlsx` | 涵盖2004-2023年的精选主表 |

## 脚本索引（旧版编号）

1. `1.report_link_crawler.py`（原 `1.年报链接抓取.py`）
2. `2.pdf_batch_converter.py`（原 `2.PDF转码.py`）
3. `3.text_analysis.py`（原 `3.文本分析.py`）
4. `text_analysis_universal.py`（原 `文本分析-universal.py`）

## 依赖要求

```bash
pip install -r requirements.txt
```

## 多语言文档

- [README.md](../README.md) — English（完整版本）
- [docs/README.zh.md](./README.zh.md) — 简体中文版本

## Star历史

[![Star History Chart](https://api.star-history.com/svg?repos=legeling/Annualreport_tools&type=Date)](https://star-history.com/#legeling/Annualreport_tools&Date)

## 更新日志

| 日期 | 亮点 |
| --- | --- |
| 2025/11/21 | 代码优化：添加类型提示，改进错误处理，增强所有脚本的鲁棒性 |
| 2025/11/21 | README切换为英文默认 + 免责声明，多进程分析器，添加docs文件夹 |
| 2025/03/15 | 添加requirements文件，下载器现在支持其他公告 |
| 2024/10/13 | 修复爬虫结果中缺失公司的问题 |
| 2024/02/14 | 上传主表，改进可读性 |
| 2024/01/04 | 改进关键词准确性，添加通用分析器 |
| 2023/05/25 | 全面重构，参数化工作流 |
| 2023/04/20 | 初始提交 |

## TODO

- [ ] GUI / 桌面前端
- [ ] 将数据持久化到PostgreSQL / DuckDB进行进一步分析
- [ ] 云端关键词分析 & API端点
- [ ] 自动化调度 + 告警（GitHub Actions / cron）
- [x] 双语文档 & 项目指标

## 贡献

欢迎提交Issues和PRs！与社区分享功能想法、bug报告或最佳实践。

请查看我们的[贡献指南](.github/CONTRIBUTING.md)和[行为准则](.github/CODE_OF_CONDUCT.md)。

## 支持

如果这个项目对您的研究或工作有帮助，请考虑请我喝杯咖啡！您的支持让项目保持活力并激励进一步改进。

<div align="center">
  <a href="https://www.buymeacoffee.com/legeling">
    <img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-orange?style=for-the-badge&logo=buy-me-a-coffee" alt="Buy Me A Coffee"/>
  </a>
</div>

<div align="center">
  <p><strong>或扫描微信二维码：</strong></p>
  <img width="280" src="https://raw.githubusercontent.com/legeling/Annualreport_tools/main/imgs/wechat.jpg" alt="微信捐赠二维码"/>
  <p><em>每一份贡献都值得感激！感谢您的支持！</em></p>
</div>
