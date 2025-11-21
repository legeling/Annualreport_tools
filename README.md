<div align="center">
  <img src="https://raw.githubusercontent.com/legeling/Annualreport_tools/main/res/icon.svg" width="96" alt="Annualreport Tools Icon" />
  <h1>Annualreport_tools · Annual Report Toolkit</h1>
  <p>Fetch CNINFO annual reports, batch download PDFs, convert to TXT, and run keyword analytics in minutes.</p>
  <p>
    <a href="https://github.com/legeling/Annualreport_tools/stargazers"><img src="https://img.shields.io/github/stars/legeling/Annualreport_tools?style=flat-square" alt="GitHub Stars"/></a>
    <a href="https://github.com/legeling/Annualreport_tools/network/members"><img src="https://img.shields.io/github/forks/legeling/Annualreport_tools?style=flat-square" alt="GitHub Forks"/></a>
    <a href="https://github.com/legeling/Annualreport_tools/watchers"><img src="https://img.shields.io/github/watchers/legeling/Annualreport_tools?style=flat-square" alt="GitHub Watchers"/></a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version"/>
    <a href="https://github.com/legeling/Annualreport_tools/issues"><img src="https://img.shields.io/github/issues/legeling/Annualreport_tools?style=flat-square" alt="GitHub Issues"/></a>
  </p>
</div>

<p align="center">
  <a href="./docs/README.en.md">English</a> ·
  <a href="./docs/README.zh.md">简体中文</a>
</p>

![Demo Screenshot](https://cdn.nlark.com/yuque/0/2023/png/22569186/1684739594091-379cdf84-28f5-4998-835f-7c9555fddac7.png#averageHue=%23a8c1db&clientId=uc29edf23-5138-4&from=paste&height=687&id=ua755022a&originHeight=1374&originWidth=2560&originalType=binary&ratio=2&rotation=0&showTitle=false&size=944474&status=done&style=none&taskId=ucc34614d-4b0d-48dc-a316-949d41f13b8&title=&width=1280)

---

## Disclaimer
- This project is **for research and educational purposes only**. Do not use it for unlawful scraping or commercial redistribution.
- Please **prefer the curated cloud-drive dataset** that already contains downloaded annual reports. Avoid hammering CNINFO with frequent crawls; respect the source website and relevant regulations.
- You are solely responsible for any data collection behavior triggered by these scripts.

## Key Features
1. **report_link_crawler.py** – segmented CNINFO queries across boards/industries to stay stable under rate limits.
2. **pdf_batch_converter.py** – resilient PDF downloader with MIME verification + conversion to TXT.
3. **text_analysis.py** – multiprocess keyword analyzer + Excel export.
4. **text_analysis_universal.py** – lightweight analyzer that accepts any TXT directory.
5. **Res assets (`/res`)** – curated annual report master sheet & icon assets for docs.
6. **Docs folder** – bilingual documentation stored under `docs/` for easy switching.

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run `report_link_crawler.py` (or reuse `./res/AnnualReport_links_2004_2023.xlsx`) to prepare annual-report links.
3. Execute `pdf_batch_converter.py` to download PDFs and convert them to TXT; optionally delete the original PDFs afterward.
4. Launch `text_analysis.py` (multiprocess) or `text_analysis_universal.py` to produce keyword totals + overall word counts in Excel.
5. Check the [Wiki](https://github.com/legeling/Annualreport_tools/wiki) or `docs/` for language-specific walkthroughs.

## Module Overview
| Script / Asset | Description |
| --- | --- |
| `report_link_crawler.py` | CNINFO crawler with board/industry filters and retry logic |
| `pdf_batch_converter.py` | Batch download + pdfplumber conversion with file validation |
| `text_analysis.py` | Multiprocess keyword analytics with Excel export |
| `text_analysis_universal.py` | Lightweight analyzer for arbitrary TXT folders |
| `./res/AnnualReport_links_2004_2023.xlsx` | Curated master sheet covering 2004-2023 |

## Script Index (Legacy Numbering)
1. `report_link_crawler.py`（原 `1.年报链接抓取.py`）
2. `pdf_batch_converter.py`（原 `2.PDF转码.py`）
3. `text_analysis.py`（原 `3.文本分析.py`）
4. `text_analysis_universal.py`（原 `文本分析-universal.py`）

## Requirements
```
pip install -r requirements.txt
```

## Multilingual Docs
- [docs/README.en.md](./docs/README.en.md) — English (full version)
- [docs/README.zh.md](./docs/README.zh.md) — 简体中文版本

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=legeling/Annualreport_tools&type=Date)](https://star-history.com/#legeling/Annualreport_tools&Date)

## Changelog
| Date | Highlights |
| --- | --- |
| 2025/11/21 | Code optimization: added type hints, improved error handling, enhanced robustness across all scripts |
| 2025/11/21 | README switched to English default + disclaimer, multiprocess analyzer, docs folder added |
| 2025/03/15 | Added requirements file, downloader now supports other announcements |
| 2024/10/13 | Fixed missing companies in crawler results |
| 2024/02/14 | Uploaded master sheet, improved readability |
| 2024/01/04 | Improved keyword accuracy, added universal analyzer |
| 2023/05/25 | Full refactor with parameterized workflow |
| 2023/04/20 | Initial commit |

## TODO
- [ ] GUI / desktop front-end
- [ ] Persist data into PostgreSQL / DuckDB for further analysis
- [ ] Cloud keyword analysis & API endpoints
- [ ] Automated scheduling + alerting (GitHub Actions / cron)
- [x] Bilingual docs & project metrics

## Contributing
Issues & PRs are welcome! Share feature ideas, bug reports, or best practices with the community.

## Support
[爱发电 · 感谢支持](https://afdian.net/a/NBFX1)

<div align="center">
  <img width="280" src="https://github.com/legeling/-/blob/main/afdian-%E5%87%8C%E5%B0%8F%E6%B7%BB.jpg?raw=true" alt="Donate QR"/>
</div>
