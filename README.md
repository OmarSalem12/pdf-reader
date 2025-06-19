# PDF Reader

A Python package for reading encrypted PDF files, extracting specific fields (Name, Date of Birth, Insurance information), and outputting the data to spreadsheets.

---

## 📖 Tutorial: How to Use PDF Reader

### 1. Installation

**With pip (from source):**
```bash
git clone https://github.com/OmarSalem12/pdf-reader.git
cd pdf-reader
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Install dependencies only:**
```bash
pip install -r requirements.txt
```

---

### 2. Command-Line Usage

#### **Extract from a single encrypted PDF:**
```bash
pdf-reader --input myfile.pdf --password mypassword --output extracted.xlsx
```

#### **Extract from multiple PDFs:**
```bash
pdf-reader --input "*.pdf" --password mypassword --output all_data.xlsx
```

#### **Use a custom extraction pattern config:**
```bash
pdf-reader --input myfile.pdf --password mypassword --output data.xlsx --config my_patterns.json
```

#### **Export to CSV:**
```bash
pdf-reader --input myfile.pdf --password mypassword --output data.csv --format csv
```

#### **Get help:**
```bash
pdf-reader --help
```

---

### 3. Python API Usage

```python
from pdf_reader import PDFReader

# Initialize the reader (optionally with a config file)
reader = PDFReader()

# Read and extract from a single PDF
result = reader.process_single_pdf("myfile.pdf", password="mypassword", output_file="output.xlsx")

# Read and extract from multiple PDFs
results = reader.process_multiple_pdfs(["*.pdf"], password="mypassword", output_file="all_data.xlsx")

# Extract fields from raw text (e.g., for testing)
sample_text = """
Name: John Doe
Date of Birth: 01/01/1980
Insurance: Blue Cross
"""
fields = reader.extract_fields(sample_text, filename="test.pdf")
print(fields)
```

---

### 4. Custom Extraction Patterns (Best Practice)

To improve extraction accuracy, use non-greedy, line-ending-aware regexes. Example config:

```json
{
  "name_patterns": [
    "Name:\\s*([A-Za-z\\s]+?)(?:\\n|$)",
    "Full Name:\\s*([A-Za-z\\s]+?)(?:\\n|$)"
  ],
  "dob_patterns": [
    "Date of Birth:\\s*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})"
  ],
  "insurance_patterns": [
    "Insurance:\\s*([A-Za-z0-9\\s-]+?)(?:\\n|$)"
  ]
}
```

Save as `my_patterns.json` and use with `--config my_patterns.json` or `PDFReader(config_file="my_patterns.json")`.

---

### 5. Troubleshooting
- If extraction is too broad, make your regex non-greedy and end-aware (see above).
- If you get `ModuleNotFoundError`, ensure you are in your virtual environment and dependencies are installed.
- For encrypted PDFs, always provide the correct password.

---

### 6. More Examples
See `example_usage.py` for more advanced usage and pattern customization.

---

## Features

- 🔐 Read encrypted PDF files with password support
- 📝 Extract specific fields: Name, Date of Birth, Insurance information
- 📊 Export data to Excel/CSV spreadsheets
- 🛡️ Robust error handling and validation
- 🎯 Configurable field extraction patterns
- 📦 Easy-to-use command-line interface

## Output Format

The package generates spreadsheets with the following columns:
- **Name**: Extracted full name
- **Date of Birth**: Extracted date of birth
- **Insurance Information**: Extracted insurance details
- **Source File**: Original PDF filename
- **Extraction Date**: Timestamp of extraction

## Requirements

- Python 3.8+
- PyPDF2
- pandas
- openpyxl
- python-dateutil
- regex
- cryptography

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub. 