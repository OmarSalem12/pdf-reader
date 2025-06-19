"""
Command-line interface for PDF Reader package.

This module provides a comprehensive CLI for the PDF Reader package,
allowing users to extract data from PDFs and export to various formats
from the command line.
"""

import argparse
import logging
import sys
from typing import Optional

from .pdf_reader import PDFReader
from .config import Config
from .exceptions import PDFError
from .exceptions import (
    ConfigurationError,
)

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose: Enable verbose logging if True.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Extract data from encrypted PDF files"
    )
    parser.add_argument("pdf_file", help="Path to the PDF file to process")
    parser.add_argument("-p", "--password", help="Password for encrypted PDF")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument(
        "-o", "--output", help="Output file path for extracted data"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["csv", "excel", "json"],
        default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--fields", nargs="+", help="Specific fields to extract"
    )
    parser.add_argument(
        "--patterns", nargs="+", help="Custom regex patterns for extraction"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 1.0.0"
    )
    return parser


def extract_single_pdf(
    pdf_path: str,
    password: Optional[str] = None,
    config: Optional[Config] = None,
    output_path: Optional[str] = None,
    output_format: str = "csv",
    fields: Optional[list] = None,
    patterns: Optional[list] = None,
) -> dict:
    """Extract data from a single PDF file.

    Args:
        pdf_path: Path to the PDF file.
        password: Password for encrypted PDF.
        config: Configuration object.
        output_path: Output file path.
        output_format: Output format (csv, excel, json).
        fields: Specific fields to extract.
        patterns: Custom regex patterns.

    Returns:
        Extracted data dictionary.

    Raises:
        PDFError: If PDF processing fails.
    """
    try:
        # Initialize PDF reader
        if config:
            reader = PDFReader(config)
        else:
            reader = PDFReader()

        # Extract data
        data = reader.extract_data(
            pdf_path, password=password, fields=fields, patterns=patterns
        )

        # Export data if output path specified
        if output_path:
            reader.export_data(data, output_path, output_format)

        return data

    except Exception as e:
        logger.error(f"Failed to process PDF {pdf_path}: {e}")
        raise PDFError(f"PDF processing failed: {e}")


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        # Load configuration if specified
        config = None
        if args.config:
            try:
                config = Config.from_file(args.config)
                logger.info(f"Loaded configuration from {args.config}")
            except ConfigurationError as e:
                logger.error(f"Configuration error: {e}")
                return 1

        # Extract data
        data = extract_single_pdf(
            pdf_path=args.pdf_file,
            password=args.password,
            config=config,
            output_path=args.output,
            output_format=args.format,
            fields=args.fields,
            patterns=args.patterns,
        )

        # Display results
        if not args.output:
            print("\nExtracted Data:")
            print("=" * 50)
            for field, value in data.items():
                print(f"{field}: {value}")
            print("=" * 50)

        logger.info("PDF processing completed successfully")
        return 0

    except PDFError as e:
        logger.error(f"PDF processing error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
