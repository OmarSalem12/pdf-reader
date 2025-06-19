"""Tests using mock PDF files for PDF Reader package."""

import unittest
from unittest.mock import patch, mock_open

from pdf_reader import PDFReader, TextExtractor, DataExporter, Config


class TestWithMockPDFs(unittest.TestCase):
    """Test cases using mock PDF files."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.pdf_reader = PDFReader(self.config)
        self.extractor = TextExtractor()
        self.exporter = DataExporter()

        # Mock PDF content
        self.mock_pdf_content = """
        Name: John Doe
        Date of Birth: 01/15/1990
        Insurance: ABC123456
        Phone: 555-123-4567
        Email: john.doe@example.com
        """

    def test_read_mock_pdf(self):
        """Test reading a mock PDF file."""
        with patch("builtins.open", mock_open(read_data=b"mock pdf data")):
            with patch("PyPDF2.PdfReader") as mock_pdf_reader:
                mock_reader = mock_pdf_reader.return_value
                mock_reader.is_encrypted = False
                mock_reader.pages = [mock_pdf_reader.return_value]
                mock_reader.pages[0].extract_text.return_value = (
                    self.mock_pdf_content
                )

                result = self.pdf_reader.read_pdf("mock.pdf")
                self.assertEqual(result, self.mock_pdf_content)

    def test_extract_from_mock_pdf_content(self):
        """Test extracting data from mock PDF content."""
        result = self.extractor.extract_fields(self.mock_pdf_content)

        self.assertIn("name", result)
        self.assertIn("date_of_birth", result)
        self.assertIn("insurance", result)
        self.assertIn("phone", result)
        self.assertIn("email", result)

        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["date_of_birth"], "01/15/1990")
        self.assertEqual(result["insurance"], "ABC123456")

    def test_extract_specific_fields(self):
        """Test extracting specific fields from mock content."""
        fields = ["name", "date_of_birth"]
        result = self.extractor.extract_fields(self.mock_pdf_content, fields)

        self.assertIn("name", result)
        self.assertIn("date_of_birth", result)
        self.assertNotIn("insurance", result)
        self.assertNotIn("phone", result)

    def test_extract_with_custom_patterns(self):
        """Test extraction with custom patterns."""
        custom_patterns = {"custom_field": [r"Custom:\s*(.+)"]}

        test_content = "Custom: Custom Value\n" + self.mock_pdf_content
        result = self.extractor.extract_with_custom_patterns(
            test_content, custom_patterns
        )

        self.assertIn("custom_field", result)
        self.assertEqual(result["custom_field"], "Custom Value")

    def test_export_mock_data(self):
        """Test exporting mock extracted data."""
        mock_data = [
            {
                "name": "John Doe",
                "date_of_birth": "01/15/1990",
                "insurance": "ABC123456",
            },
            {
                "name": "Jane Smith",
                "date_of_birth": "02/20/1985",
                "insurance": "DEF789012",
            },
        ]

        # Test CSV export
        with patch("builtins.open", mock_open()):
            result = self.exporter.export_to_csv(mock_data, "test.csv")
            self.assertIsInstance(result, str)
            self.assertTrue(result.endswith(".csv"))

        # Test Excel export
        with patch("openpyxl.Workbook"):
            with patch("builtins.open", mock_open()):
                result = self.exporter.export_to_excel(mock_data, "test.xlsx")
                self.assertIsInstance(result, str)
                self.assertTrue(result.endswith(".xlsx"))

    def test_process_mock_pdf(self):
        """Test complete processing of mock PDF."""
        with patch.object(self.pdf_reader, "read_pdf") as mock_read:
            mock_read.return_value = self.mock_pdf_content

            result = self.pdf_reader.extract_data("mock.pdf")

            self.assertIn("name", result)
            self.assertIn("date_of_birth", result)
            self.assertIn("insurance", result)
            self.assertIn("source_file", result)

    def test_mock_pdf_with_password(self):
        """Test reading encrypted mock PDF."""
        with patch(
            "builtins.open", mock_open(read_data=b"encrypted pdf data")
        ):
            with patch("PyPDF2.PdfReader") as mock_pdf_reader:
                mock_reader = mock_pdf_reader.return_value
                mock_reader.is_encrypted = True
                mock_reader.decrypt.return_value = 1
                mock_reader.pages = [mock_pdf_reader.return_value]
                mock_reader.pages[0].extract_text.return_value = (
                    self.mock_pdf_content
                )

                result = self.pdf_reader.read_pdf(
                    "encrypted.pdf", password="test123"
                )
                self.assertEqual(result, self.mock_pdf_content)

    def test_mock_pdf_encryption_error(self):
        """Test handling of encryption errors."""
        with patch(
            "builtins.open", mock_open(read_data=b"encrypted pdf data")
        ):
            with patch("PyPDF2.PdfReader") as mock_pdf_reader:
                mock_reader = mock_pdf_reader.return_value
                mock_reader.is_encrypted = True
                mock_reader.decrypt.side_effect = Exception("Wrong password")

                with self.assertRaises(Exception):
                    self.pdf_reader.read_pdf("encrypted.pdf", password="wrong")

    def test_mock_pdf_file_not_found(self):
        """Test handling of non-existent PDF file."""
        with self.assertRaises(Exception):
            self.pdf_reader.read_pdf("nonexistent.pdf")

    def test_validate_mock_data(self):
        """Test validation of mock data."""
        valid_data = [
            {"name": "John Doe", "dob": "01/15/1990"},
            {"name": "Jane Smith", "dob": "02/20/1985"},
        ]

        invalid_data = "not a list"
        empty_data = []

        self.assertTrue(self.exporter.validate_data(valid_data))
        self.assertFalse(self.exporter.validate_data(invalid_data))
        self.assertFalse(self.exporter.validate_data(empty_data))

    def test_mock_config_operations(self):
        """Test configuration operations with mock data."""
        config = Config()

        # Test setting and getting values
        config.set("test_key", "test_value")
        self.assertEqual(config.get("test_key"), "test_value")

        # Test getting with default
        self.assertEqual(config.get("nonexistent", "default"), "default")

        # Test updating multiple values
        config.update({"key1": "value1", "key2": "value2"})
        self.assertEqual(config.get("key1"), "value1")
        self.assertEqual(config.get("key2"), "value2")

    def test_mock_pattern_validation(self):
        """Test pattern validation with mock patterns."""
        valid_pattern = r"Name:\s*(.+)"
        invalid_pattern = r"Name:\s*(.+"

        self.assertTrue(self.extractor.validate_pattern(valid_pattern))
        self.assertFalse(self.extractor.validate_pattern(invalid_pattern))

    def test_mock_available_fields(self):
        """Test getting available fields."""
        fields = self.extractor.get_available_fields()
        self.assertIsInstance(fields, list)
        self.assertIn("name", fields)
        self.assertIn("date_of_birth", fields)
        self.assertIn("insurance", fields)

    def test_mock_supported_formats(self):
        """Test getting supported export formats."""
        formats = self.exporter.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertIn("csv", formats)
        self.assertIn("excel", formats)
        self.assertIn("json", formats)


if __name__ == "__main__":
    unittest.main()
