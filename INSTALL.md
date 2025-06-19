# Installation Guide

This guide will help you install and set up the PDF Reader package.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Options

### Option 1: Install from Source (Recommended)

1. Clone or download the repository:
```bash
git clone https://github.com/yourusername/pdf_reader.git
cd pdf_reader
```

2. Install the package in development mode:
```bash
pip install -e .
```

### Option 2: Install Dependencies Only

If you want to install just the dependencies:
```bash
pip install -r requirements.txt
```

## Verification

After installation, you can verify that everything is working:

1. Test the command-line interface:
```bash
pdf-reader --help
```

2. Run the example script:
```bash
python example_usage.py
```

3. Run the tests:
```bash
python test_pdf_reader.py
```

## Quick Start

### Command Line Usage

1. **Process a single encrypted PDF:**
```bash
pdf-reader --input document.pdf --password mypassword --output data.xlsx
```

2. **Process multiple PDFs:**
```bash
pdf-reader --input "*.pdf" --password mypassword --output results.xlsx
```

3. **Use custom configuration:**
```bash
pdf-reader --input file.pdf --password mypassword --output data.xlsx --config patterns.json
```

### Python API Usage

```python
from pdf_reader import PDFReader

# Initialize reader
reader = PDFReader()

# Process a single PDF
result = reader.process_single_pdf("document.pdf", password="mypassword", output_file="data.xlsx")

# Process multiple PDFs
results = reader.process_multiple_pdfs(["*.pdf"], password="mypassword", output_file="results.xlsx")
```

## Configuration

### Default Patterns

The package comes with built-in patterns for extracting:
- **Names**: Various formats like "Name:", "Full Name:", "Patient Name:"
- **Dates of Birth**: Formats like "Date of Birth:", "DOB:", "Birth Date:"
- **Insurance Information**: Patterns for insurance companies, policy numbers, etc.

### Custom Configuration

Create a JSON file with your custom patterns:

```json
{
  "name_patterns": [
    "Name:\\s*([A-Za-z\\s]+)",
    "Full Name:\\s*([A-Za-z\\s]+)"
  ],
  "dob_patterns": [
    "Date of Birth:\\s*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})",
    "DOB:\\s*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})"
  ],
  "insurance_patterns": [
    "Insurance:\\s*([A-Za-z0-9\\s-]+)",
    "Policy Number:\\s*([A-Za-z0-9\\s-]+)"
  ]
}
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've installed the package correctly
   ```bash
   pip install -e .
   ```

2. **Missing Dependencies**: Install all required packages
   ```bash
   pip install -r requirements.txt
   ```

3. **PDF Reading Issues**: Ensure the PDF is not corrupted and the password is correct

4. **Permission Errors**: Make sure you have write permissions in the output directory

### Getting Help

- Check the README.md for detailed documentation
- Run `pdf-reader --help` for command-line options
- Review the example_usage.py file for usage examples
- Run the tests to verify your installation

## Development Setup

For developers who want to contribute:

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
python -m pytest test_pdf_reader.py
```

3. Check code style:
```bash
black pdf_reader/
flake8 pdf_reader/
``` 