# Contributing to Annualreport_tools

First off, thank you for considering contributing to Annualreport_tools! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible
* Include your environment details (OS, Python version, package versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide (PEP 8)
* Include thoughtful comments in your code
* End all files with a newline
* Avoid platform-dependent code
* Write clear, descriptive commit messages

## Development Process

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Style Guidelines

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* No emojis in commit messages

### Python Style Guide

* Follow PEP 8
* Use type hints where appropriate
* Write docstrings for all public methods
* Keep functions focused and small
* Use meaningful variable names
* Add comments for complex logic

### Documentation Style Guide

* Use Markdown for documentation
* Keep line length to 80-100 characters
* Use clear, concise language
* Include code examples where appropriate
* Keep documentation up to date with code changes

## Project Structure

```
Annualreport_tools/
├── 1.report_link_crawler.py    # CNINFO crawler
├── 2.pdf_batch_converter.py    # PDF downloader & converter
├── 3.text_analysis.py          # Multiprocess keyword analyzer
├── text_analysis_universal.py  # Universal text analyzer
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── docs/                       # Multilingual documentation
│   ├── README.en.md
│   └── README.zh.md
├── res/                        # Resource files
│   └── AnnualReport_links_2004_2023.xlsx
└── imgs/                       # Image assets
    ├── icon.svg
    └── wechat.jpg
```

## Testing

Before submitting a pull request, please test your changes:

1. Run the scripts with various configurations
2. Test edge cases
3. Verify error handling
4. Check memory usage for large datasets
5. Ensure backward compatibility

## Questions?

Feel free to open an issue with your question or contact the maintainers directly.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for your contributions!
