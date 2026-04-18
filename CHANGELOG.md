# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2026-04-18]

### Changed
- Security and resilience hardening for crawler/downloader paths
- Improved retry strategy and request failure handling for unstable network scenarios
- Optimized text analysis hot paths to reduce unnecessary repeated computation

### Added
- Added submodule-level protection to avoid accidental open-source leakage of private paid scripts

### Fixed
- PDF conversion fallback behavior and error logging robustness in mixed PDF sources

## [2025-11-21] - Major Refactor

### Added
- Incremental save mechanism: auto-save every 100 records during crawling
- Strict year validation: filter out mismatched year records
- Comprehensive GitHub community templates (Issue, PR, Contributing, Code of Conduct)
- Enhanced documentation with bilingual support (English/Chinese)
- Organized image assets in dedicated `imgs/` folder

### Changed
- Refactored all scripts to object-oriented architecture
- Improved error handling and retry logic across all modules
- Enhanced progress tracking and statistics reporting
- Removed all emoji from code and logs for professional appearance
- Updated README with comprehensive disclaimer and donation section

### Fixed
- Progress display overflow issues in crawler
- Missing data due to coarse date segmentation (now crawls daily)
- Type hints and code style improvements throughout

## [2025-03-15]

### Added
- Requirements file for dependency management
- Support for other announcement types in downloader

## [2024-10-13]

### Fixed
- Missing companies in crawler results

## [2024-02-14]

### Added
- Uploaded master sheet covering 2004-2023
- Improved code readability

## [2024-01-04]

### Improved
- Keyword extraction accuracy
- Added universal text analyzer

## [2023-05-25]

### Changed
- Full refactor with parameterized workflow

## [2023-04-20]

### Added
- Initial project release
