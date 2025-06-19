"""
Main PDF Reader class for processing encrypted PDF files.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import PyPDF2

from .config import Config
from .exceptions import EncryptionError, ExtractionError, PDFError
from .extractor import TextExtractor
from .exporter import DataExporter

logger = logging.getLogger(__name__)


class PDFReader:
    """Main class for reading and processing PDF files."""

    def __init__(self, config: Optional[Union[Config, str]] = None):
        """Initialize PDF reader.

        Args:
            config: Configuration object or path to config file
        """
        if isinstance(config, str):
            self.config = Config.from_file(config)
        elif isinstance(config, Config):
            self.config = config
        else:
            self.config = Config()

        self.extractor = TextExtractor()
        self.exporter = DataExporter(self.config.get("output_directory"))

        logger.info(
            "PDFReader initialized with config: %s",
            self.config.get("output_directory"),
        )

    def read_pdf(self, pdf_path: str, password: Optional[str] = None) -> str:
        """Read PDF file and extract text content.

        Args:
            pdf_path: Path to PDF file
            password: Password for encrypted PDF

        Returns:
            Extracted text content

        Raises:
            EncryptionError: If PDF is encrypted and password is incorrect
            PDFError: If PDF cannot be read
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise PDFError(f"PDF file not found: {pdf_path}")

        try:
            with open(pdf_file, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    if not password:
                        raise EncryptionError(
                            "PDF is encrypted but no password provided",
                            password_provided=False,
                        )
                    try:
                        pdf_reader.decrypt(password)
                        logger.info("Successfully decrypted PDF with password")
                    except Exception as e:
                        raise EncryptionError(
                            f"Failed to decrypt PDF: {e}",
                            password_provided=True,
                        )

                # Extract text from all pages
                text_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                        logger.debug(
                            "Extracted text from page %d", page_num + 1
                        )
                    except Exception as e:
                        logger.warning(
                            "Failed to extract text from page %d: %s",
                            page_num + 1,
                            e,
                        )

                if not text_content.strip():
                    logger.warning("No text content extracted from PDF")
                    return ""

                logger.info(
                    "Successfully extracted text from PDF: %s", pdf_path
                )
                return text_content

        except EncryptionError:
            raise
        except Exception as e:
            error_msg = f"Failed to read PDF {pdf_path}: {e}"
            logger.error(error_msg)
            raise PDFError(error_msg)

    def extract_data(
        self,
        pdf_path: str,
        password: Optional[str] = None,
        fields: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Extract data from PDF file.

        Args:
            pdf_path: Path to PDF file
            password: Password for encrypted PDF
            fields: Specific fields to extract
            patterns: Custom regex patterns

        Returns:
            Dictionary of extracted data

        Raises:
            ExtractionError: If data extraction fails
        """
        try:
            # Read PDF text
            text_content = self.read_pdf(pdf_path, password)

            if not text_content:
                logger.warning("No text content to extract from")
                return {}

            # Extract data using patterns
            if patterns:
                # Use custom patterns
                custom_patterns = {}
                for i, pattern in enumerate(patterns):
                    field_name = f"custom_field_{i+1}"
                    custom_patterns[field_name] = pattern

                extracted_data = self.extractor.extract_with_custom_patterns(
                    text_content, custom_patterns
                )
            else:
                # Use default patterns
                extracted_data = self.extractor.extract_fields(
                    text_content, fields
                )

            # Add metadata
            extracted_data["source_file"] = str(pdf_path)
            extracted_data["extraction_timestamp"] = self.config.get(
                "timestamp_format"
            )

            if self.config.get("include_raw_text"):
                max_length = self.config.get("raw_text_max_length", 1000)
                extracted_data["raw_text"] = text_content[:max_length]

            logger.info(
                "Successfully extracted %d fields from PDF",
                len(extracted_data),
            )
            return extracted_data

        except Exception as e:
            error_msg = f"Failed to extract data from PDF {pdf_path}: {e}"
            logger.error(error_msg)
            raise ExtractionError(error_msg)

    def export_data(
        self, data: Dict[str, Any], output_path: str, format_type: str = "csv"
    ) -> str:
        """Export extracted data to file.

        Args:
            data: Extracted data dictionary
            output_path: Output file path
            format_type: Export format ('csv', 'excel', 'json')

        Returns:
            Path to exported file

        Raises:
            ExportError: If export fails
        """
        try:
            # Convert single record to list for exporter
            data_list = [data] if isinstance(data, dict) else data

            # Validate data
            if not self.exporter.validate_data(data_list):
                raise ExtractionError("Invalid data format for export")

            # Export data
            exported_path = self.exporter.export_data(
                data_list, output_path, format_type
            )
            logger.info("Data exported to %s: %s", format_type, exported_path)
            return exported_path

        except Exception as e:
            error_msg = f"Failed to export data: {e}"
            logger.error(error_msg)
            raise ExtractionError(error_msg)

    def process_pdf(
        self,
        pdf_path: str,
        password: Optional[str] = None,
        output_path: Optional[str] = None,
        format_type: str = "csv",
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Process PDF file: extract data and optionally export.

        Args:
            pdf_path: Path to PDF file
            password: Password for encrypted PDF
            output_path: Output file path (optional)
            format_type: Export format
            fields: Specific fields to extract

        Returns:
            Dictionary of extracted data

        Raises:
            PDFError: If processing fails
        """
        try:
            # Extract data
            data = self.extract_data(pdf_path, password, fields)

            # Export if output path specified
            if output_path:
                self.export_data(data, output_path, format_type)

            return data

        except Exception as e:
            error_msg = f"Failed to process PDF {pdf_path}: {e}"
            logger.error(error_msg)
            raise PDFError(error_msg)

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats.

        Returns:
            List of supported format names
        """
        return self.exporter.get_supported_formats()

    def get_available_fields(self) -> List[str]:
        """Get list of available extraction fields.

        Returns:
            List of available field names
        """
        return self.extractor.get_available_fields()
