#!/usr/bin/env python3
"""
Basic tests for the PDF Reader package.
"""

import unittest
import tempfile
import os
from pdf_reader import PDFReader
from pdf_reader.exceptions import PDFReaderError, ExtractionError


class TestPDFReader(unittest.TestCase):
    """Test cases for PDF Reader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = PDFReader()
        
        # Sample text for testing
        self.sample_text = """
        Patient Information Form
        
        Name: John Doe
        Date of Birth: 05/15/1985
        Insurance: Blue Cross Blue Shield
        Policy Number: BCBS123456
        
        Additional Information:
        Address: 123 Main St, Anytown, USA
        Phone: (555) 123-4567
        """
    
    def test_extract_fields(self):
        """Test field extraction from text."""
        extracted = self.reader.extract_fields(self.sample_text, "test.pdf")
        
        # Check that fields are extracted correctly
        self.assertEqual(extracted["Name"], "John Doe")
        self.assertEqual(extracted["Date of Birth"], "05/15/1985")
        self.assertIn("Blue Cross Blue Shield", extracted["Insurance Information"])
        self.assertEqual(extracted["Source File"], "test.pdf")
        self.assertIn("Extraction Date", extracted)
    
    def test_extract_fields_no_data(self):
        """Test field extraction with no relevant data."""
        empty_text = "This is a document with no structured data."
        extracted = self.reader.extract_fields(empty_text, "empty.pdf")
        
        # Check that fields are None when no data is found
        self.assertIsNone(extracted["Name"])
        self.assertIsNone(extracted["Date of Birth"])
        self.assertIsNone(extracted["Insurance Information"])
        self.assertEqual(extracted["Source File"], "empty.pdf")
    
    def test_multiple_extractions(self):
        """Test extracting from multiple text contents."""
        texts = [
            "Name: Alice Smith\nDate of Birth: 01/01/1990\nInsurance: Aetna",
            "Name: Bob Johnson\nDate of Birth: 02/02/1985\nInsurance: Blue Cross"
        ]
        
        extracted = self.reader.extractor.extract_multiple(texts, ["file1.pdf", "file2.pdf"])
        
        self.assertEqual(len(extracted), 2)
        self.assertEqual(extracted[0]["Name"], "Alice Smith")
        self.assertEqual(extracted[1]["Name"], "Bob Johnson")
    
    def test_export_to_spreadsheet(self):
        """Test spreadsheet export functionality."""
        # Create test data
        test_data = [
            {
                "Name": "John Doe",
                "Date of Birth": "05/15/1985",
                "Insurance Information": "Blue Cross Blue Shield",
                "Source File": "test1.pdf",
                "Extraction Date": "2024-01-01T00:00:00"
            },
            {
                "Name": "Jane Smith",
                "Date of Birth": "12/03/1990",
                "Insurance Information": "Aetna",
                "Source File": "test2.pdf",
                "Extraction Date": "2024-01-01T00:00:00"
            }
        ]
        
        # Test Excel export
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            output_file = tmp.name
        
        try:
            self.reader.export_to_spreadsheet(test_data, output_file, "excel")
            self.assertTrue(os.path.exists(output_file))
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_custom_patterns(self):
        """Test adding custom extraction patterns."""
        # Add custom pattern (non-greedy, line-ending-aware)
        self.reader.update_patterns("name_patterns", r"Client:\s*([A-Za-z\s]+?)(?:\n|$)")
        
        # Test with custom pattern
        custom_text = "Client: Custom Name\nDate of Birth: 01/01/2000"
        extracted = self.reader.extract_fields(custom_text, "custom.pdf")
        
        self.assertEqual(extracted["Name"], "Custom Name")
    
    def test_get_patterns(self):
        """Test getting current patterns."""
        patterns = self.reader.get_patterns()
        
        self.assertIn("name_patterns", patterns)
        self.assertIn("dob_patterns", patterns)
        self.assertIn("insurance_patterns", patterns)
        self.assertIsInstance(patterns["name_patterns"], list)
    
    def test_error_handling(self):
        """Test error handling in field extraction."""
        # Test with malformed text that might cause issues
        malformed_text = "Name: \nDate of Birth: invalid-date\nInsurance: "
        
        # Should not raise an exception, but return None values
        extracted = self.reader.extract_fields(malformed_text, "malformed.pdf")
        
        self.assertIsNone(extracted["Name"])
        self.assertIsNone(extracted["Date of Birth"])
        self.assertIsNone(extracted["Insurance Information"])


class TestConfiguration(unittest.TestCase):
    """Test configuration functionality."""
    
    def test_default_patterns(self):
        """Test that default patterns are loaded."""
        reader = PDFReader()
        patterns = reader.get_patterns()
        
        # Check that we have patterns for all field types
        self.assertGreater(len(patterns["name_patterns"]), 0)
        self.assertGreater(len(patterns["dob_patterns"]), 0)
        self.assertGreater(len(patterns["insurance_patterns"]), 0)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 