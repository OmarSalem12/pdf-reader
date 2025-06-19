#!/usr/bin/env python3
"""
Example usage of the PDF Reader package.

This script demonstrates how to use the PDF Reader package to process
encrypted PDF files and extract specific fields.
"""

from pdf_reader import PDFReader
import json


def create_sample_config():
    """Create a sample configuration file."""
    config = {
        "name_patterns": [
            r"Name:\s*([A-Za-z\s]+)",
            r"Full Name:\s*([A-Za-z\s]+)",
            r"Patient Name:\s*([A-Za-z\s]+)",
            r"([A-Z][a-z]+ [A-Z][a-z]+)",  # Basic name pattern
        ],
        "dob_patterns": [
            r"Date of Birth:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"DOB:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # General date pattern
        ],
        "insurance_patterns": [
            r"Insurance:\s*([A-Za-z0-9\s\-]+)",
            r"Policy Number:\s*([A-Za-z0-9\s\-]+)",
            r"Insurance Company:\s*([A-Za-z0-9\s\-]+)",
        ]
    }
    
    with open("sample_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Sample configuration file created: sample_config.json")


def example_single_pdf():
    """Example: Process a single PDF file."""
    print("\n=== Example: Single PDF Processing ===")
    
    # Initialize reader
    reader = PDFReader()
    
    # Example text content (simulating PDF text)
    sample_text = """
    Patient Information Form
    
    Name: John Doe
    Date of Birth: 05/15/1985
    Insurance: Blue Cross Blue Shield
    Policy Number: BCBS123456
    
    Additional Information:
    Address: 123 Main St, Anytown, USA
    Phone: (555) 123-4567
    """
    
    # Extract fields
    extracted_data = reader.extract_fields(sample_text, "sample_patient.pdf")
    
    print("Extracted Data:")
    for key, value in extracted_data.items():
        if key != "Raw Text":  # Skip raw text for display
            print(f"  {key}: {value}")
    
    # Export to spreadsheet
    reader.export_to_spreadsheet([extracted_data], "single_patient_data.xlsx")
    print("Data exported to: single_patient_data.xlsx")


def example_multiple_pdfs():
    """Example: Process multiple PDF files."""
    print("\n=== Example: Multiple PDF Processing ===")
    
    # Initialize reader with custom config
    reader = PDFReader("sample_config.json")
    
    # Sample text contents (simulating multiple PDFs)
    sample_texts = [
        """
        Medical Record - Patient 1
        Name: Jane Smith
        Date of Birth: 12/03/1990
        Insurance Company: Aetna
        Policy: AET789012
        """,
        """
        Insurance Form - Patient 2
        Full Name: Robert Johnson
        DOB: 08/22/1975
        Insurance: Cigna Health
        Group Number: CIG456789
        """,
        """
        Patient: Mary Wilson
        Birth Date: 03/10/1988
        Insurance Information: United Health
        Policy Number: UHC987654
        """
    ]
    
    filenames = ["patient1.pdf", "patient2.pdf", "patient3.pdf"]
    
    # Extract fields from all texts
    extracted_data = reader.extractor.extract_multiple(sample_texts, filenames)
    
    print("Extracted Data from Multiple Files:")
    for i, data in enumerate(extracted_data, 1):
        print(f"\nFile {i}: {data['Source File']}")
        print(f"  Name: {data['Name']}")
        print(f"  Date of Birth: {data['Date of Birth']}")
        print(f"  Insurance: {data['Insurance Information']}")
    
    # Export to spreadsheet
    reader.export_to_spreadsheet(extracted_data, "multiple_patients_data.xlsx")
    print("\nData exported to: multiple_patients_data.xlsx")


def example_custom_patterns():
    """Example: Add custom extraction patterns."""
    print("\n=== Example: Custom Patterns ===")
    
    # Initialize reader
    reader = PDFReader()
    
    # Add custom patterns
    reader.update_patterns("name_patterns", r"Client:\s*([A-Za-z\s]+)")
    reader.update_patterns("dob_patterns", r"Birth:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
    reader.update_patterns("insurance_patterns", r"Coverage:\s*([A-Za-z0-9\s\-]+)")
    
    # Test with custom pattern
    custom_text = """
    Client: Alice Brown
    Birth: 11/20/1982
    Coverage: Humana Health
    """
    
    extracted_data = reader.extract_fields(custom_text, "custom_pattern_test.pdf")
    
    print("Extracted Data with Custom Patterns:")
    for key, value in extracted_data.items():
        if key != "Raw Text":
            print(f"  {key}: {value}")


def example_error_handling():
    """Example: Error handling."""
    print("\n=== Example: Error Handling ===")
    
    reader = PDFReader()
    
    # Test with problematic text
    problematic_text = """
    This is a document without clear field labels.
    Some random text here.
    No structured data to extract.
    """
    
    try:
        extracted_data = reader.extract_fields(problematic_text, "problematic.pdf")
        print("Extracted Data (should be mostly None):")
        for key, value in extracted_data.items():
            if key != "Raw Text":
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error occurred: {e}")


def main():
    """Run all examples."""
    print("PDF Reader Package - Example Usage")
    print("=" * 50)
    
    # Create sample configuration
    create_sample_config()
    
    # Run examples
    example_single_pdf()
    example_multiple_pdfs()
    example_custom_patterns()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("Check the generated Excel files for the extracted data.")


if __name__ == "__main__":
    main() 