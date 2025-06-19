#!/usr/bin/env python3
"""
Basic usage examples for PDF Reader Package.

This script demonstrates various ways to use the PDF Reader package
for extracting data from encrypted PDF files and exporting to spreadsheets.
"""

import logging

from pdf_reader import PDFReader, TextExtractor, DataExporter, Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_pdf() -> None:
    """Example: Process a single PDF file."""
    print("=== Single PDF Processing Example ===")

    # Initialize components
    config = Config()
    pdf_reader = PDFReader(config)
    extractor = TextExtractor()
    exporter = DataExporter()

    # Process a single PDF
    pdf_file = "path/to/your/document.pdf"
    password = "your_password"

    try:
        # Read PDF content
        text_content = pdf_reader.read_pdf(pdf_file, password)
        logger.info(f"Successfully read PDF: {pdf_file}")

        # Extract data
        extracted_data = extractor.extract_fields(text_content)
        logger.info(f"Extracted {len(extracted_data)} fields")

        # Add metadata
        extracted_data["source_file"] = pdf_file
        extracted_data["extraction_timestamp"] = config.get("timestamp_format")

        # Export to Excel
        output_file = exporter.export_to_excel([extracted_data])
        logger.info(f"Data exported to: {output_file}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")


def example_multiple_pdfs() -> None:
    """Example: Process multiple PDF files."""
    print("\n=== Multiple PDF Processing Example ===")

    # Initialize components
    config = Config()
    pdf_reader = PDFReader(config)
    extractor = TextExtractor()
    exporter = DataExporter()

    # List of PDF files to process
    pdf_files = ["path/to/doc1.pdf", "path/to/doc2.pdf", "path/to/doc3.pdf"]
    password = "your_password"

    results = []

    for pdf_file in pdf_files:
        try:
            # Read PDF content
            text_content = pdf_reader.read_pdf(pdf_file, password)

            # Extract data
            extracted_data = extractor.extract_fields(text_content)

            # Add metadata
            extracted_data["source_file"] = pdf_file
            extracted_data["extraction_timestamp"] = config.get("timestamp_format")

            results.append(extracted_data)
            logger.info(f"Processed: {pdf_file}")

        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")
            # Add error record
            error_data = {
                "source_file": pdf_file,
                "error": str(e),
                "extraction_timestamp": config.get("timestamp_format"),
            }
            results.append(error_data)

    # Export all results
    if results:
        output_file = exporter.export_to_excel(results)
        logger.info(f"All data exported to: {output_file}")


def example_custom_patterns() -> None:
    """Example: Using custom extraction patterns."""
    print("\n=== Custom Patterns Example ===")

    # Define custom patterns
    custom_patterns = {
        "employee_id": r"Employee ID[:\s]*([A-Z0-9]+)",
        "department": r"Department[:\s]*([A-Za-z\s]+)",
        "salary": r"Salary[:\s]*\$?([0-9,]+)",
        "hire_date": r"Hire Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    }

    # Initialize with custom patterns
    extractor = TextExtractor(custom_patterns)  # type: ignore
    pdf_reader = PDFReader()

    pdf_file = "path/to/employee_document.pdf"
    password = "your_password"

    try:
        # Read and extract
        text_content = pdf_reader.read_pdf(pdf_file, password)
        extracted_data = extractor.extract_fields(text_content)

        logger.info(f"Extracted data with custom patterns: {extracted_data}")

    except Exception as e:
        logger.error(f"Error: {e}")


def example_specific_fields() -> None:
    """Example: Extract only specific fields."""
    print("\n=== Specific Fields Example ===")

    extractor = TextExtractor()
    pdf_reader = PDFReader()

    pdf_file = "path/to/document.pdf"
    password = "your_password"

    # Fields to extract
    target_fields = ["name", "date_of_birth", "insurance_number"]

    try:
        text_content = pdf_reader.read_pdf(pdf_file, password)

        extracted_data = {}
        for field in target_fields:
            value = extractor.extract_specific_field(text_content, field)
            if value:
                extracted_data[field] = value

        logger.info(f"Extracted specific fields: {extracted_data}")

    except Exception as e:
        logger.error(f"Error: {e}")


def example_multiple_formats() -> None:
    """Example: Export to multiple formats."""
    print("\n=== Multiple Formats Example ===")

    config = Config()
    pdf_reader = PDFReader(config)
    extractor = TextExtractor()
    exporter = DataExporter()

    pdf_file = "path/to/document.pdf"
    password = "your_password"

    try:
        # Extract data
        text_content = pdf_reader.read_pdf(pdf_file, password)
        extracted_data = extractor.extract_fields(text_content)
        extracted_data["source_file"] = pdf_file

        # Export to multiple formats
        results = exporter.export_multiple_formats([extracted_data])  # type: ignore

        for format_type, file_path in results.items():
            logger.info(f"Exported to {format_type}: {file_path}")

    except Exception as e:
        logger.error(f"Error: {e}")


def example_configuration() -> None:
    """Example: Using custom configuration."""
    print("\n=== Configuration Example ===")

    # Create custom configuration
    config = Config()

    # Update settings
    config.update(
        {
            "output_directory": "./custom_output",
            "log_level": "DEBUG",
            "include_raw_text": True,
            "raw_text_max_length": 500,
            "export_metadata": True,
        }
    )

    # Validate configuration
    if config.validate():
        logger.info("Configuration is valid")

        # Use custom configuration
        pdf_reader = PDFReader(config)
        exporter = DataExporter(config.get("output_directory"))
        extractor = TextExtractor()

        # Process with custom settings
        pdf_file = "path/to/document.pdf"
        password = "your_password"

        try:
            text_content = pdf_reader.read_pdf(pdf_file, password)
            extracted_data = extractor.extract_fields(text_content)

            # Export with custom settings
            output_file = exporter.export_to_excel([extracted_data])
            logger.info(f"Exported with custom config: {output_file}")

        except Exception as e:
            logger.error(f"Error: {e}")
    else:
        logger.error("Configuration validation failed")


def example_error_handling() -> None:
    """Example: Comprehensive error handling."""
    print("\n=== Error Handling Example ===")

    from pdf_reader.exceptions import (
        PDFReaderError,
        EncryptionError,
        ExtractionError,
        ExportError,
    )

    pdf_reader = PDFReader()
    extractor = TextExtractor()
    exporter = DataExporter()

    pdf_files = [
        "path/to/valid.pdf",
        "path/to/encrypted.pdf",
        "path/to/corrupted.pdf",
        "path/to/nonexistent.pdf",
    ]

    results = []

    for pdf_file in pdf_files:
        try:
            # Try to read PDF
            text_content = pdf_reader.read_pdf(pdf_file, password="test")

            # Try to extract data
            extracted_data = extractor.extract_fields(text_content)
            extracted_data["source_file"] = pdf_file
            results.append(extracted_data)

        except EncryptionError as e:
            logger.error(f"Encryption error for {pdf_file}: {e}")
            results.append(
                {
                    "source_file": pdf_file,
                    "error": f"Encryption error: {e}",
                    "error_type": "encryption",
                }
            )

        except ExtractionError as e:
            logger.error(f"Extraction error for {pdf_file}: {e}")
            results.append(
                {
                    "source_file": pdf_file,
                    "error": f"Extraction error: {e}",
                    "error_type": "extraction",
                }
            )

        except PDFReaderError as e:
            logger.error(f"PDF Reader error for {pdf_file}: {e}")
            results.append(
                {
                    "source_file": pdf_file,
                    "error": f"PDF Reader error: {e}",
                    "error_type": "pdf_reader",
                }
            )

        except Exception as e:
            logger.error(f"Unexpected error for {pdf_file}: {e}")
            results.append(
                {
                    "source_file": pdf_file,
                    "error": f"Unexpected error: {e}",
                    "error_type": "unknown",
                }
            )

    # Export results including errors
    if results:
        try:
            output_file = exporter.export_to_excel(results)
            logger.info(f"Results exported to: {output_file}")
        except ExportError as e:
            logger.error(f"Export error: {e}")


def main() -> None:
    """Run all examples."""
    print("PDF Reader Package - Usage Examples")
    print("=" * 50)

    # Note: These examples use placeholder file paths
    # Replace with actual PDF files to test

    example_single_pdf()
    example_multiple_pdfs()
    example_custom_patterns()
    example_specific_fields()
    example_multiple_formats()
    example_configuration()
    example_error_handling()

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Note: Replace placeholder file paths with actual PDF files to test")


if __name__ == "__main__":
    main()
