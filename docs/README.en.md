# Annualreport_tools · Annual Report Toolkit (English)

> The default README is English. Use this condensed doc for quick reference or translation.

## Key Features
1. `report_link_crawler.py`: CNINFO annual report crawler with board/industry filters and retry logic.
2. `pdf_batch_converter.py`: resilient PDF downloader + converter with retries, MIME validation, and integrity checks.
3. `text_analysis.py`: multiprocess keyword analyzer that leverages all CPU cores.
4. `text_analysis_universal.py`: drop any TXT folder in to generate an Excel dashboard.
5. `年报链接2004-2023.xlsx`: curated master sheet for offline usage.

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`.
2. Run `report_link_crawler.py` (or reuse `年报链接2004-2023.xlsx`) to obtain annual report links.
3. Execute `pdf_batch_converter.py` to download PDFs and convert them into TXT files.
4. Launch `text_analysis.py` (multiprocess) or `text_analysis_universal.py` to produce keyword statistics.
5. Visit the [Wiki](https://github.com/legeling/Annualreport_tools/wiki) for detailed tutorials and FAQs.

## Module Overview
| Script / Asset | Description |
| --- | --- |
| `report_link_crawler.py` | Retrieves CNINFO announcements with customizable filters |
| `pdf_batch_converter.py` | Downloads PDFs and converts them to TXT via pdfplumber |
| `text_analysis.py` | Multiprocess keyword analyzer with Excel export |
| `text_analysis_universal.py` | Lightweight analyzer for arbitrary TXT folders |
| `年报链接2004-2023.xlsx` | Curated master sheet covering 2004-2023 |

## Multilingual Docs
- [README.zh.md](./README.zh.md) — Simplified Chinese version
- [README.en.md](./README.en.md) — Current English version
