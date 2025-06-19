"""Tests for the refactored PDF Reader package."""

import unittest
from unittest.mock import patch, mock_open

from pdf_reader import (
    PDFReader,
    TextExtractor,
    DataExporter,
    Config,
    PDFError,
    EncryptionError,
    ExtractionError,
    ExportError,
    ConfigurationError,
)


class TestPDFReaderPackage(unittest.TestCase):
    """Test cases for the PDF Reader package."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.config = Config()
        self.pdf_reader = PDFReader(self.config)
        self.extractor = TextExtractor()
        self.exporter = DataExporter()

    def test_pdf_reader_initialization(self) -> None:
        """Test PDFReader initialization."""
        reader = PDFReader()
        self.assertIsNotNone(reader)
        self.assertIsInstance(reader.config, Config)

    def test_config_initialization(self) -> None:
        """Test Config initialization."""
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config.settings, dict)

    def test_extractor_initialization(self) -> None:
        """Test TextExtractor initialization."""
        extractor = TextExtractor()
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor.patterns, dict)

    def test_exporter_initialization(self) -> None:
        """Test DataExporter initialization."""
        exporter = DataExporter()
        self.assertIsNotNone(exporter)
        self.assertIsInstance(
            exporter.output_directory,
            type(self.config.get("output_directory")),
        )

    def test_extract_fields_from_text(self) -> None:
        """Test field extraction from text."""
        test_text = """
        Name: John Doe
        Date of Birth: 01/15/1990
        Insurance: ABC123456
        """
        result = self.extractor.extract_fields(test_text)
        self.assertIn("name", result)
        self.assertIn("date_of_birth", result)
        self.assertIn("insurance", result)

    def test_extract_specific_field(self) -> None:
        """Test extraction of specific field."""
        test_text = "Name: Jane Smith"
        result = self.extractor.extract_specific_field(test_text, "name")
        self.assertEqual(result, "Jane Smith")

    def test_extract_nonexistent_field(self) -> None:
        """Test extraction of non-existent field."""
        test_text = "Name: John Doe"
        result = self.extractor.extract_specific_field(test_text, "nonexistent")
        self.assertIsNone(result)

    def test_export_to_csv(self) -> None:
        """Test CSV export functionality."""
        test_data = [
            {"name": "John Doe", "dob": "01/15/1990"},
            {"name": "Jane Smith", "dob": "02/20/1985"},
        ]
        result = self.exporter.export_to_csv(test_data, "test_output.csv")
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith(".csv"))

    def test_export_to_excel(self) -> None:
        """Test Excel export functionality."""
        test_data = [
            {"name": "John Doe", "dob": "01/15/1990"},
            {"name": "Jane Smith", "dob": "02/20/1985"},
        ]
        with patch("openpyxl.Workbook"):
            result = self.exporter.export_to_excel(test_data, "test_output.xlsx")
            self.assertIsInstance(result, str)
            self.assertTrue(result.endswith(".xlsx"))

    def test_config_get_set(self) -> None:
        """Test Config get and set methods."""
        config = Config()
        config.set("test_key", "test_value")
        result = config.get("test_key")
        self.assertEqual(result, "test_value")

    def test_config_get_default(self) -> None:
        """Test Config get with default value."""
        config = Config()
        result = config.get("nonexistent_key", "default_value")
        self.assertEqual(result, "default_value")

    def test_pdf_reader_with_config_file(self) -> None:
        """Test PDFReader with config file path."""
        with patch("builtins.open", mock_open(read_data='{"test": "value"}')):
            reader = PDFReader("test_config.json")
            self.assertIsNotNone(reader)

    def test_extract_with_custom_patterns(self) -> None:
        """Test extraction with custom patterns."""
        test_text = "Custom Field: Custom Value"
        custom_patterns = {"custom_field": [r"Custom Field:\s*(.+)"]}
        result = self.extractor.extract_with_custom_patterns(test_text, custom_patterns)
        self.assertIn("custom_field", result)
        self.assertEqual(result["custom_field"], "Custom Value")

    def test_validate_pattern(self) -> None:
        """Test pattern validation."""
        valid_pattern = r"Name:\s*(.+)"
        invalid_pattern = r"Name:\s*(.+"

        self.assertTrue(self.extractor.validate_pattern(valid_pattern))
        self.assertFalse(self.extractor.validate_pattern(invalid_pattern))

    def test_get_available_fields(self) -> None:
        """Test getting available fields."""
        fields = self.extractor.get_available_fields()
        self.assertIsInstance(fields, list)
        self.assertIn("name", fields)
        self.assertIn("date_of_birth", fields)

    def test_get_supported_formats(self) -> None:
        """Test getting supported export formats."""
        formats = self.exporter.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertIn("csv", formats)
        self.assertIn("excel", formats)
        self.assertIn("json", formats)

    def test_validate_data(self) -> None:
        """Test data validation."""
        valid_data = [{"name": "John Doe"}]
        invalid_data = "not a list"

        self.assertTrue(self.exporter.validate_data(valid_data))
        self.assertFalse(self.exporter.validate_data(invalid_data))

    def test_config_from_file(self) -> None:
        """Test Config.from_file method."""
        with patch("builtins.open", mock_open(read_data='{"test": "value"}')):
            config = Config.from_file("test.json")
            self.assertIsInstance(config, Config)

    def test_config_save_config(self) -> None:
        """Test Config.save_config method."""
        config = Config()
        with patch("builtins.open", mock_open()):
            config.save_config("test.json")

    def test_pdf_reader_process_pdf(self) -> None:
        """Test PDFReader.process_pdf method."""
        with patch.object(self.pdf_reader, "extract_data") as mock_extract:
            mock_extract.return_value = {"name": "John Doe"}
            result = self.pdf_reader.process_pdf("test.pdf")
            self.assertIsInstance(result, dict)

    def test_pdf_reader_get_methods(self) -> None:
        """Test PDFReader getter methods."""
        formats = self.pdf_reader.get_supported_formats()
        fields = self.pdf_reader.get_available_fields()

        self.assertIsInstance(formats, list)
        self.assertIsInstance(fields, list)

    def test_exceptions(self) -> None:
        """Test custom exceptions."""
        with self.assertRaises(PDFError):
            raise PDFError("Test error")

        with self.assertRaises(EncryptionError):
            raise EncryptionError("Test encryption error")

        with self.assertRaises(ExtractionError):
            raise ExtractionError("Test extraction error")

        with self.assertRaises(ExportError):
            raise ExportError("Test export error")

        with self.assertRaises(ConfigurationError):
            raise ConfigurationError("Test config error")


if __name__ == "__main__":
    unittest.main()
