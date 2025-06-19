#!/usr/bin/env python3
"""
Comprehensive test script using mock PDFs to test the PDF Reader package.
"""

import os
import sys
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
from pdf_reader import PDFReader


def create_pdf_with_text(text_content, filename):
    """Create a PDF with the given text content."""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    y_position = 750
    for line in text_content.split('\n'):
        if line.strip():
            can.drawString(100, y_position, line.strip())
            y_position -= 20
    
    can.save()
    packet.seek(0)
    
    new_pdf = PdfReader(packet)
    with open(filename, 'wb') as output_file:
        writer = PdfWriter()
        writer.add_page(new_pdf.pages[0])
        writer.write(output_file)


def encrypt_pdf(input_filename, output_filename, password):
    """Encrypt a PDF with a password."""
    with open(input_filename, 'rb') as file:
        reader = PdfReader(file)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        writer.encrypt(password)
        
        with open(output_filename, 'wb') as output_file:
            writer.write(output_file)


def create_mock_pdfs():
    """Create mock PDFs for testing."""
    os.makedirs('mock_pdfs', exist_ok=True)
    
    # Test data for different PDF formats
    test_data = [
        {
            'name': 'patient1',
            'password': 'password123',
            'content': """
            PATIENT INFORMATION FORM
            
            Name: John Doe
            Date of Birth: 05/15/1985
            Insurance: Blue Cross Blue Shield
            Policy Number: BCBS123456
            
            Additional Information:
            Address: 123 Main St, Anytown, USA
            Phone: (555) 123-4567
            """
        },
        {
            'name': 'patient2',
            'password': 'secure456',
            'content': """
            MEDICAL RECORD
            
            Patient Name: Jane Smith
            Date of Birth: 12/03/1990
            Insurance Company: Aetna Health
            Policy: AET789012
            Group Number: AET456
            
            Medical History:
            - No known allergies
            - Previous surgeries: None
            """
        },
        {
            'name': 'patient3',
            'password': 'test789',
            'content': """
            INSURANCE FORM
            
            Full Name: Robert Johnson
            DOB: 08/22/1975
            Insurance: Cigna Health
            Group Number: CIG456789
            Member ID: CIG789012
            
            Coverage Details:
            - Medical: Comprehensive
            - Dental: Basic
            """
        },
        {
            'name': 'patient4',
            'password': 'demo321',
            'content': """
            CLIENT INFORMATION
            
            Client: Mary Wilson
            Birth Date: 03/10/1988
            Insurance Information: United Health
            Policy Number: UHC987654
            Coverage Type: Family Plan
            """
        },
        {
            'name': 'patient5',
            'password': 'simple555',
            'content': """
            BASIC FORM
            
            Name: Alice Brown
            Date of Birth: 11/20/1982
            Insurance: Humana Health
            
            Notes: Basic coverage plan
            """
        }
    ]
    
    for data in test_data:
        unencrypted_file = f"mock_pdfs/{data['name']}_unencrypted.pdf"
        encrypted_file = f"mock_pdfs/{data['name']}_encrypted.pdf"
        
        create_pdf_with_text(data['content'], unencrypted_file)
        encrypt_pdf(unencrypted_file, encrypted_file, data['password'])
    
    print("✅ Created 5 mock PDFs with different formats and passwords")


def test_single_pdf_extraction():
    """Test extraction from single encrypted PDFs."""
    print("\n" + "=" * 50)
    print("TESTING SINGLE PDF EXTRACTION")
    print("=" * 50)
    
    reader = PDFReader()
    
    # Test cases with different formats
    test_cases = [
        ("patient1_encrypted.pdf", "password123", "John Doe", "05/15/1985"),
        ("patient2_encrypted.pdf", "secure456", "Jane Smith", "12/03/1990"),
        ("patient3_encrypted.pdf", "test789", "Robert Johnson", "08/22/1975"),
    ]
    
    for filename, password, expected_name, expected_dob in test_cases:
        print(f"\nTesting {filename} (password: {password})")
        try:
            result = reader.process_single_pdf(f"mock_pdfs/{filename}", password=password)
            
            print(f"✅ Success: {result['Name']} - {result['Date of Birth']}")
            assert result['Name'] == expected_name, f"Name mismatch: {result['Name']} != {expected_name}"
            assert result['Date of Birth'] == expected_dob, f"DOB mismatch: {result['Date of Birth']} != {expected_dob}"
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True


def test_multiple_pdf_extraction():
    """Test extraction from multiple encrypted PDFs."""
    print("\n" + "=" * 50)
    print("TESTING MULTIPLE PDF EXTRACTION")
    print("=" * 50)
    
    reader = PDFReader()
    
    # Process all encrypted PDFs
    pdf_files = [
        ("patient1_encrypted.pdf", "password123"),
        ("patient2_encrypted.pdf", "secure456"),
        ("patient3_encrypted.pdf", "test789"),
        ("patient4_encrypted.pdf", "demo321"),
        ("patient5_encrypted.pdf", "simple555"),
    ]
    
    results = []
    for filename, password in pdf_files:
        print(f"Processing {filename}...")
        try:
            result = reader.process_single_pdf(f"mock_pdfs/{filename}", password=password)
            results.append(result)
            print(f"✅ {result['Name']} - {result['Date of Birth']}")
        except Exception as e:
            print(f"❌ Error with {filename}: {e}")
            return False
    
    # Export results
    try:
        reader.export_to_spreadsheet(results, "test_output.xlsx")
        print(f"\n✅ Successfully exported {len(results)} records to test_output.xlsx")
    except Exception as e:
        print(f"❌ Export error: {e}")
        return False
    
    return True


def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 50)
    print("TESTING ERROR HANDLING")
    print("=" * 50)
    
    reader = PDFReader()
    
    # Test wrong password
    print("Testing wrong password...")
    try:
        reader.process_single_pdf("mock_pdfs/patient1_encrypted.pdf", password="wrongpassword")
        print("❌ Should have failed with wrong password")
        return False
    except Exception as e:
        print(f"✅ Correctly handled wrong password: {str(e)[:50]}...")
    
    # Test unencrypted PDF
    print("Testing unencrypted PDF...")
    try:
        result = reader.process_single_pdf("mock_pdfs/patient1_unencrypted.pdf")
        print(f"✅ Unencrypted PDF works: {result['Name']}")
    except Exception as e:
        print(f"❌ Error with unencrypted PDF: {e}")
        return False
    
    return True


def test_custom_patterns():
    """Test custom extraction patterns."""
    print("\n" + "=" * 50)
    print("TESTING CUSTOM PATTERNS")
    print("=" * 50)
    
    reader = PDFReader()
    
    # Add custom patterns for "Client:" format
    reader.update_patterns("name_patterns", r"Client:\s*([A-Za-z\s]+?)(?:\n|$)")
    reader.update_patterns("dob_patterns", r"Birth Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
    
    print("Testing custom patterns on patient4...")
    try:
        result = reader.process_single_pdf("mock_pdfs/patient4_encrypted.pdf", password="demo321")
        print(f"✅ Custom pattern success: {result['Name']} - {result['Date of Birth']}")
        return True
    except Exception as e:
        print(f"❌ Custom pattern error: {e}")
        return False


def main():
    """Run all tests."""
    print("PDF READER PACKAGE - COMPREHENSIVE TESTING")
    print("=" * 50)
    
    # Create mock PDFs
    print("Creating mock PDFs...")
    create_mock_pdfs()
    
    # Run all tests
    tests = [
        test_single_pdf_extraction,
        test_multiple_pdf_extraction,
        test_error_handling,
        test_custom_patterns
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 