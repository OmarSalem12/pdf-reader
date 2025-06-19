# PDF Reader Package

A comprehensive Python package for reading encrypted PDF files, extracting specific fields (Name, Date of Birth, Insurance information), and exporting data to spreadsheets.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## Features

- **Encrypted PDF Support**: Read password-protected PDF files
- **Flexible Data Extraction**: Extract specific fields using regex patterns
- **Multiple Output Formats**: Export to Excel (.xlsx) and CSV formats
- **Custom Patterns**: Define your own extraction patterns
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Type Hints**: Full type annotations for better IDE support
- **Error Handling**: Robust error handling with custom exceptions
- **Configuration Management**: Flexible configuration system
- **Command Line Interface**: Easy-to-use CLI for batch processing
- **Testing**: Comprehensive test suite with mock PDFs

## Installation

### From PyPI (Recommended)

```bash
pip install pdf-reader
```

### From Source

```bash
git clone https://github.com/yourusername/pdf-reader.git
cd pdf-reader
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/pdf-reader.git
cd pdf-reader
pip install -e .[dev]
```

## Quick Start

### Command Line Usage

```bash
# Extract from a single PDF
pdf-reader extract document.pdf --password mypass --output results.xlsx

# Extract from multiple PDFs
pdf-reader extract *.pdf --password mypass --formats excel,csv

# Extract specific fields only
pdf-reader extract document.pdf --fields name,date_of_birth,insurance_number

# Use custom patterns
pdf-reader extract document.pdf --custom-patterns patterns.json

# Verbose output with debug logging
pdf-reader extract document.pdf --verbose --log-level DEBUG
```

### Programmatic Usage

```python
from pdf_reader import PDFReader, TextExtractor, DataExporter, Config

# Initialize components
config = Config()
pdf_reader = PDFReader(config)
extractor = TextExtractor()
exporter = DataExporter()

# Read PDF
text_content = pdf_reader.read_pdf("document.pdf", password="mypass")

# Extract data
extracted_data = extractor.extract_fields(text_content)

# Export to Excel
output_file = exporter.export_to_excel([extracted_data])
print(f"Data exported to: {output_file}")
```

## Advanced Usage

### Custom Extraction Patterns

```python
# Define custom patterns
custom_patterns = {
    'employee_id': r'Employee ID[:\s]*([A-Z0-9]+)',
    'department': r'Department[:\s]*([A-Za-z\s]+)',
    'salary': r'Salary[:\s]*\$?([0-9,]+)'
}

# Use custom patterns
extractor = TextExtractor(custom_patterns)
extracted_data = extractor.extract_fields(text_content)
```

### Configuration Management

```python
# Create custom configuration
config = Config()
config.update({
    'output_directory': './custom_output',
    'log_level': 'DEBUG',
    'include_raw_text': True,
    'export_metadata': True
})

# Validate configuration
if config.validate():
    pdf_reader = PDFReader(config)
    # Use with custom settings
```

### Multiple Format Export

```python
# Export to multiple formats
results = exporter.export_multiple_formats(extracted_data)

for format_type, file_path in results.items():
    print(f"Exported to {format_type}: {file_path}")
```

### Error Handling

```python
from pdf_reader.exceptions import (
    PDFReaderError, EncryptionError, ExtractionError, ExportError
)

try:
    text_content = pdf_reader.read_pdf("document.pdf", password="mypass")
    extracted_data = extractor.extract_fields(text_content)
    output_file = exporter.export_to_excel([extracted_data])
    
except EncryptionError as e:
    print(f"Encryption error: {e}")
except ExtractionError as e:
    print(f"Extraction error: {e}")
except ExportError as e:
    print(f"Export error: {e}")
```

## CLI Reference

### Commands

#### `extract`
Extract data from PDF files.

```bash
pdf-reader extract <pdf_files> [options]
```

**Arguments:**
- `pdf_files`: PDF file(s) to process (supports glob patterns)

**Options:**
- `--password, -p`: Password for encrypted PDFs
- `--output, -o`: Output file path (default: auto-generated)
- `--output-dir, -d`: Output directory (default: current directory)
- `--formats, -f`: Output formats: excel, csv (default: excel)
- `--fields, -F`: Specific fields to extract
- `--custom-patterns, -c`: JSON file with custom extraction patterns
- `--config, -C`: Configuration file path
- `--verbose, -v`: Enable verbose output
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Log file path
- `--batch-size`: Number of files to process in batch (default: 100)
- `--timeout`: Timeout in seconds for PDF processing (default: 30)
- `--include-raw-text`: Include raw text in output
- `--no-progress`: Disable progress bar

#### `config`
Configuration management.

```bash
pdf-reader config [options]
```

**Options:**
- `--show`: Show current configuration
- `--save <file>`: Save current configuration to file
- `--load <file>`: Load configuration from file
- `--reset`: Reset to default configuration

#### `info`
Show package information.

```bash
pdf-reader info [options]
```

**Options:**
- `--version`: Show version information
- `--fields`: Show available extraction fields
- `--formats`: Show supported output formats

### Examples

```bash
# Basic extraction
pdf-reader extract document.pdf --password mypass

# Multiple files with custom output
pdf-reader extract *.pdf --password mypass --output-dir ./exports --formats excel,csv

# Extract specific fields with custom patterns
pdf-reader extract document.pdf --fields name,employee_id --custom-patterns patterns.json

# Verbose processing with logging
pdf-reader extract document.pdf --verbose --log-level DEBUG --log-file processing.log

# Show configuration
pdf-reader config --show

# Show available fields
pdf-reader info --fields
```

## Configuration

The package supports configuration through:

1. **Default settings**: Built-in sensible defaults
2. **Configuration files**: Custom configuration files
3. **Environment variables**: Override settings with environment variables

### Configuration File Format

```ini
# PDF Reader Configuration File
output_directory=./output
log_level=INFO
max_file_size_mb=50
supported_formats=["xlsx", "csv"]
default_format=xlsx
include_raw_text=false
export_metadata=true
```

### Environment Variables

Set environment variables with the `PDF_READER_` prefix:

```bash
export PDF_READER_OUTPUT_DIRECTORY=./custom_output
export PDF_READER_LOG_LEVEL=DEBUG
export PDF_READER_INCLUDE_RAW_TEXT=true
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/pdf-reader.git
cd pdf-reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=pdf_reader --cov-report=html

# Run specific test file
pytest tests/test_refactored_package.py

# Run tests with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black pdf_reader tests
isort pdf_reader tests

# Lint code
flake8 pdf_reader tests

# Type checking
mypy pdf_reader

# Run all quality checks
make check-all
```

### Building Documentation

```bash
# Build documentation
cd docs && make html

# Serve documentation locally
cd docs && python -m http.server 8000
```

### Making a Release

```bash
# Update version
bump2version patch  # or minor, major

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Project Structure

```
pdf_reader/
├── pdf_reader/              # Main package
│   ├── __init__.py          # Package initialization
│   ├── pdf_reader.py        # PDF reading functionality
│   ├── extractor.py         # Text extraction utilities
│   ├── exporter.py          # Data export functionality
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   └── cli.py              # Command-line interface
├── tests/                   # Test suite
│   ├── test_refactored_package.py
│   ├── test_with_mock_pdfs.py
│   └── mock_pdfs/          # Mock PDF files for testing
├── examples/                # Usage examples
│   └── basic_usage.py
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
├── pyproject.toml          # Modern Python packaging
├── Makefile                # Development tasks
└── README.md               # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Add tests for new features
- Update documentation as needed
- Use conventional commit messages

## Testing

The package includes comprehensive tests:

- **Unit tests**: Test individual components
- **Integration tests**: Test complete workflows
- **Mock PDFs**: Test with encrypted PDF files
- **Error handling**: Test exception scenarios

Run tests with:

```bash
# All tests
pytest

# With coverage
pytest --cov=pdf_reader --cov-report=term-missing

# Specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -k "test_extract"  # Run tests matching pattern
```

## Performance

The package is optimized for:

- **Memory efficiency**: Processes large PDFs without loading entire content into memory
- **Speed**: Uses efficient regex patterns and optimized data structures
- **Scalability**: Supports batch processing of multiple files
- **Resource management**: Proper cleanup of temporary files and resources

## Security

- **Password handling**: Secure password management for encrypted PDFs
- **File validation**: Validates PDF files before processing
- **Error sanitization**: Prevents information leakage in error messages
- **Input validation**: Validates all user inputs and configuration

## Troubleshooting

### Common Issues

1. **Encryption Error**: Ensure correct password is provided
2. **File Not Found**: Check file path and permissions
3. **Extraction Issues**: Verify PDF contains extractable text
4. **Export Errors**: Check output directory permissions and disk space

### Debug Mode

Enable debug logging for detailed information:

```bash
pdf-reader extract document.pdf --log-level DEBUG --log-file debug.log
```

### Getting Help

- Check the [documentation](https://pdf-reader.readthedocs.io/)
- Search [existing issues](https://github.com/yourusername/pdf-reader/issues)
- Create a [new issue](https://github.com/yourusername/pdf-reader/issues/new)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyPDF2](https://pypdf2.readthedocs.io/) for PDF processing
- [pandas](https://pandas.pydata.org/) for data manipulation
- [openpyxl](https://openpyxl.readthedocs.io/) for Excel export
- [pytest](https://docs.pytest.org/) for testing framework

## Changelog

### Version 1.0.0
- Complete package refactoring with logging and type hints
- Enhanced CLI with subcommands and better error handling
- Comprehensive configuration management
- Improved exception handling with detailed error information
- Added support for custom extraction patterns
- Multiple output format support (Excel and CSV)
- Comprehensive test suite with mock PDFs
- Development tools and CI/CD pipeline
- Documentation and examples 