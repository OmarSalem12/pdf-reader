"""
Comprehensive tests for the refactored PDF Reader package.

This module tests all major components of the refactored package including
PDF reading, text extraction, data export, configuration management, and CLI.
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pandas as pd

from pdf_reader import (
    PDFReader, TextExtractor, DataExporter, Config,
    PDFReaderError, EncryptionError, ExtractionError, ExportError, ConfigurationError
)


class TestConfig(unittest.TestCase):
    """Test configuration management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_default_settings(self):
        """Test that default settings are loaded correctly."""
        settings = self.config.get_all()
        
        # Check that essential settings exist
        self.assertIn('output_directory', settings)
        self.assertIn('log_level', settings)
        self.assertIn('max_file_size_mb', settings)
        self.assertIn('supported_formats', settings)
        
        # Check default values
        self.assertEqual(settings['log_level'], 'INFO')
        self.assertEqual(settings['output_directory'], './output')
        self.assertIn('xlsx', settings['supported_formats'])
        self.assertIn('csv', settings['supported_formats'])
    
    def test_get_set_methods(self):
        """Test get and set configuration methods."""
        # Test setting a value
        self.config.set('test_key', 'test_value')
        self.assertEqual(self.config.get('test_key'), 'test_value')
        
        # Test getting with default
        self.assertEqual(self.config.get('nonexistent_key', 'default'), 'default')
    
    def test_update_method(self):
        """Test updating multiple settings at once."""
        new_settings = {
            'output_directory': '/custom/path',
            'log_level': 'DEBUG',
            'custom_setting': 'custom_value'
        }
        
        self.config.update(new_settings)
        
        for key, value in new_settings.items():
            self.assertEqual(self.config.get(key), value)
    
    def test_validation(self):
        """Test configuration validation."""
        # Valid configuration should pass
        self.assertTrue(self.config.validate())
        
        # Invalid configuration should fail
        self.config.set('max_file_size_mb', -1)
        self.assertFalse(self.config.validate())
    
    def test_output_directory_creation(self):
        """Test output directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.set('output_directory', temp_dir)
            self.config.set('auto_create_directories', True)
            
            output_path = self.config.get_output_directory()
            self.assertTrue(output_path.exists())
    
    def test_save_load_config_file(self):
        """Test saving and loading configuration files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            config_file = f.name
        
        try:
            # Save configuration
            self.config.save_config_file(config_file)
            self.assertTrue(Path(config_file).exists())
            
            # Load configuration
            new_config = Config(config_file)
            original_settings = self.config.get_all()
            loaded_settings = new_config.get_all()
            
            # Compare essential settings
            for key in ['output_directory', 'log_level', 'max_file_size_mb']:
                self.assertEqual(original_settings[key], loaded_settings[key])
                
        finally:
            Path(config_file).unlink(missing_ok=True)


class TestTextExtractor(unittest.TestCase):
    """Test text extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = TextExtractor()
    
    def test_default_patterns(self):
        """Test that default patterns are loaded correctly."""
        patterns = self.extractor.patterns
        
        # Check that essential patterns exist
        self.assertIn('name', patterns)
        self.assertIn('date_of_birth', patterns)
        self.assertIn('insurance_number', patterns)
        self.assertIn('phone', patterns)
        self.assertIn('email', patterns)
    
    def test_extract_fields(self):
        """Test field extraction from text."""
        test_text = """
        Name: John Doe
        Date of Birth: 01/15/1985
        Insurance Number: ABC123456
        Phone: 555-123-4567
        Email: john.doe@example.com
        """
        
        extracted = self.extractor.extract_fields(test_text)
        
        self.assertIn('name', extracted)
        self.assertIn('date_of_birth', extracted)
        self.assertIn('insurance_number', extracted)
        self.assertIn('phone', extracted)
        self.assertIn('email', extracted)
        
        self.assertEqual(extracted['name'], 'John Doe')
        self.assertEqual(extracted['date_of_birth'], '01/15/1985')
        self.assertEqual(extracted['insurance_number'], 'ABC123456')
        self.assertEqual(extracted['phone'], '555-123-4567')
        self.assertEqual(extracted['email'], 'john.doe@example.com')
    
    def test_extract_specific_field(self):
        """Test extracting a specific field."""
        test_text = "Name: Jane Smith\nDate of Birth: 05/20/1990"
        
        name = self.extractor.extract_specific_field(test_text, 'name')
        dob = self.extractor.extract_specific_field(test_text, 'date_of_birth')
        phone = self.extractor.extract_specific_field(test_text, 'phone')
        
        self.assertEqual(name, 'Jane Smith')
        self.assertEqual(dob, '05/20/1990')
        self.assertIsNone(phone)  # Not in text
    
    def test_custom_patterns(self):
        """Test custom pattern functionality."""
        custom_patterns = {
            'employee_id': r'Employee ID[:\s]*([A-Z0-9]+)',
            'department': r'Department[:\s]*([A-Za-z\s]+)'
        }
        
        extractor = TextExtractor(custom_patterns)
        
        test_text = """
        Employee ID: EMP123
        Department: Engineering
        """
        
        extracted = extractor.extract_fields(test_text)
        
        self.assertIn('employee_id', extracted)
        self.assertIn('department', extracted)
        self.assertEqual(extracted['employee_id'], 'EMP123')
        self.assertEqual(extracted['department'], 'Engineering')
    
    def test_invalid_custom_pattern(self):
        """Test handling of invalid custom patterns."""
        invalid_patterns = {
            'test': r'[invalid regex pattern'
        }
        
        with self.assertRaises(ExtractionError):
            TextExtractor(invalid_patterns)
    
    def test_empty_text(self):
        """Test handling of empty text."""
        with self.assertRaises(ExtractionError):
            self.extractor.extract_fields("")
        
        with self.assertRaises(ExtractionError):
            self.extractor.extract_fields("   ")
    
    def test_get_available_fields(self):
        """Test getting available field names."""
        fields = self.extractor.get_available_fields()
        
        self.assertIn('name', fields)
        self.assertIn('date_of_birth', fields)
        self.assertIn('insurance_number', fields)
        
        # Test with custom patterns
        custom_patterns = {'custom_field': r'test'}
        extractor = TextExtractor(custom_patterns)
        fields = extractor.get_available_fields()
        
        self.assertIn('custom_field', fields)


class TestDataExporter(unittest.TestCase):
    """Test data export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = DataExporter(self.temp_dir)
        self.test_data = [
            {
                'name': 'John Doe',
                'date_of_birth': '01/15/1985',
                'insurance_number': 'ABC123456',
                'source_file': 'test.pdf'
            },
            {
                'name': 'Jane Smith',
                'date_of_birth': '05/20/1990',
                'insurance_number': 'DEF789012',
                'source_file': 'test2.pdf'
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_to_excel(self):
        """Test Excel export functionality."""
        output_file = self.exporter.export_to_excel(self.test_data)
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.xlsx'))
        
        # Verify Excel file can be read
        df = pd.read_excel(output_file)
        self.assertEqual(len(df), 2)  # Two records
        self.assertIn('name', df.columns)
        self.assertIn('date_of_birth', df.columns)
    
    def test_export_to_csv(self):
        """Test CSV export functionality."""
        output_file = self.exporter.export_to_csv(self.test_data)
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.csv'))
        
        # Verify CSV file can be read
        df = pd.read_csv(output_file)
        self.assertEqual(len(df), 2)  # Two records
        self.assertIn('name', df.columns)
        self.assertIn('date_of_birth', df.columns)
    
    def test_export_multiple_formats(self):
        """Test exporting to multiple formats."""
        results = self.exporter.export_multiple_formats(self.test_data)
        
        self.assertIn('excel', results)
        self.assertIn('csv', results)
        
        self.assertTrue(Path(results['excel']).exists())
        self.assertTrue(Path(results['csv']).exists())
    
    def test_empty_data(self):
        """Test handling of empty data."""
        with self.assertRaises(ExportError):
            self.exporter.export_to_excel([])
        
        with self.assertRaises(ExportError):
            self.exporter.export_to_csv([])
    
    def test_invalid_data(self):
        """Test handling of invalid data."""
        invalid_data = "not a list"
        
        with self.assertRaises(ExportError):
            self.exporter.export_to_excel(invalid_data)
    
    def test_custom_filename(self):
        """Test custom filename functionality."""
        custom_filename = "custom_output.xlsx"
        output_file = self.exporter.export_to_excel(self.test_data, custom_filename)
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.xlsx'))
    
    def test_get_export_summary(self):
        """Test export summary generation."""
        summary = self.exporter.get_export_summary(self.test_data)
        
        self.assertIn('total_records', summary)
        self.assertIn('fields', summary)
        self.assertIn('field_count', summary)
        self.assertIn('non_null_counts', summary)
        
        self.assertEqual(summary['total_records'], 2)
        self.assertIn('name', summary['fields'])
        self.assertEqual(summary['field_count'], 4)  # name, dob, insurance, source_file


class TestPDFReader(unittest.TestCase):
    """Test PDF reading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.pdf_reader = PDFReader(self.config)
    
    @patch('pdf_reader.pdf_reader.PyPDF2.PdfReader')
    def test_read_pdf_success(self, mock_pdf_reader):
        """Test successful PDF reading."""
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [Mock()]
        mock_reader.pages[0].extract_text.return_value = "Test PDF content"
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            content = self.pdf_reader.read_pdf("test.pdf")
        
        self.assertEqual(content, "Test PDF content")
    
    @patch('pdf_reader.pdf_reader.PyPDF2.PdfReader')
    def test_read_encrypted_pdf(self, mock_pdf_reader):
        """Test reading encrypted PDF."""
        # Mock encrypted PDF
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = 1  # Success
        mock_reader.pages = [Mock()]
        mock_reader.pages[0].extract_text.return_value = "Encrypted content"
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            content = self.pdf_reader.read_pdf("encrypted.pdf", password="test123")
        
        self.assertEqual(content, "Encrypted content")
        mock_reader.decrypt.assert_called_once_with("test123")
    
    @patch('pdf_reader.pdf_reader.PyPDF2.PdfReader')
    def test_read_encrypted_pdf_wrong_password(self, mock_pdf_reader):
        """Test reading encrypted PDF with wrong password."""
        # Mock encrypted PDF with wrong password
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = 0  # Failure
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            with self.assertRaises(EncryptionError):
                self.pdf_reader.read_pdf("encrypted.pdf", password="wrong")
    
    def test_read_nonexistent_pdf(self):
        """Test reading non-existent PDF file."""
        with self.assertRaises(PDFError):
            self.pdf_reader.read_pdf("nonexistent.pdf")
    
    @patch('pdf_reader.pdf_reader.PyPDF2.PdfReader')
    def test_read_corrupted_pdf(self, mock_pdf_reader):
        """Test reading corrupted PDF file."""
        mock_pdf_reader.side_effect = Exception("PDF is corrupted")
        
        with patch('builtins.open', mock_open()):
            with self.assertRaises(PDFError):
                self.pdf_reader.read_pdf("corrupted.pdf")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.pdf_reader = PDFReader(self.config)
        self.extractor = TextExtractor()
        self.exporter = DataExporter()
    
    @patch('pdf_reader.pdf_reader.PyPDF2.PdfReader')
    def test_complete_workflow(self, mock_pdf_reader):
        """Test complete workflow from PDF to Excel."""
        # Mock PDF content
        test_content = """
        Name: John Doe
        Date of Birth: 01/15/1985
        Insurance Number: ABC123456
        Phone: 555-123-4567
        Email: john.doe@example.com
        """
        
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [Mock()]
        mock_reader.pages[0].extract_text.return_value = test_content
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            # Read PDF
            content = self.pdf_reader.read_pdf("test.pdf")
            
            # Extract data
            extracted_data = self.extractor.extract_fields(content)
            
            # Add metadata
            extracted_data['source_file'] = 'test.pdf'
            
            # Export to Excel
            output_file = self.exporter.export_to_excel([extracted_data])
        
        # Verify results
        self.assertIn('name', extracted_data)
        self.assertIn('date_of_birth', extracted_data)
        self.assertIn('insurance_number', extracted_data)
        self.assertEqual(extracted_data['name'], 'John Doe')
        self.assertTrue(Path(output_file).exists())


class TestErrorHandling(unittest.TestCase):
    """Test error handling across the package."""
    
    def test_pdf_reader_error(self):
        """Test PDFReaderError handling."""
        error = PDFReaderError("Test error", "Additional details")
        self.assertIn("Test error", str(error))
        self.assertIn("Additional details", str(error))
    
    def test_encryption_error(self):
        """Test EncryptionError handling."""
        error = EncryptionError("Encryption failed", "test.pdf", "AES-256")
        self.assertIn("Encryption failed", str(error))
        self.assertIn("test.pdf", str(error))
        self.assertIn("AES-256", str(error))
    
    def test_extraction_error(self):
        """Test ExtractionError handling."""
        error = ExtractionError("Extraction failed", "name", 1000)
        self.assertIn("Extraction failed", str(error))
        self.assertEqual(error.field_name, "name")
        self.assertEqual(error.text_length, 1000)
    
    def test_export_error(self):
        """Test ExportError handling."""
        error = ExportError("Export failed", "/path/to/output", "excel")
        self.assertIn("Export failed", str(error))
        self.assertEqual(error.output_path, "/path/to/output")
        self.assertEqual(error.format_type, "excel")


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2) 