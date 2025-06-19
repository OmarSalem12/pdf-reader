"""
Command-line interface for PDF Reader package.

This module provides a comprehensive CLI for the PDF Reader package, allowing users
to extract data from PDFs and export to various formats from the command line.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import List, Optional

from .config import Config
from .exceptions import PDFReaderError, EncryptionError, ExtractionError, OutputError
from .exporter import DataExporter
from .extractor import TextExtractor
from .pdf_reader import PDFReader

logger = logging.getLogger(__name__)


def setup_logging(level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger.info("Logging configured with level: %s", level)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Extract data from encrypted PDF files and export to spreadsheets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from a single PDF
  pdf-reader extract document.pdf --password mypass --output results.xlsx
  
  # Extract from multiple PDFs with custom patterns
  pdf-reader extract *.pdf --password mypass --custom-patterns patterns.json
  
  # Extract specific fields only
  pdf-reader extract document.pdf --fields name,date_of_birth,insurance_number
  
  # Export to multiple formats
  pdf-reader extract document.pdf --formats excel,csv --output-dir ./exports
  
  # Verbose output with debug logging
  pdf-reader extract document.pdf --verbose --log-level DEBUG
        """
    )
    
    # Main command
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract data from PDF files'
    )
    
    extract_parser.add_argument(
        'pdf_files',
        nargs='+',
        help='PDF file(s) to process (supports glob patterns)'
    )
    
    extract_parser.add_argument(
        '--password', '-p',
        help='Password for encrypted PDFs'
    )
    
    extract_parser.add_argument(
        '--output', '-o',
        help='Output file path (default: auto-generated)'
    )
    
    extract_parser.add_argument(
        '--output-dir', '-d',
        help='Output directory (default: current directory)'
    )
    
    extract_parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['excel', 'csv'],
        default=['excel'],
        help='Output formats (default: excel)'
    )
    
    extract_parser.add_argument(
        '--fields', '-F',
        nargs='+',
        help='Specific fields to extract (default: all available fields)'
    )
    
    extract_parser.add_argument(
        '--custom-patterns', '-c',
        help='JSON file with custom extraction patterns'
    )
    
    extract_parser.add_argument(
        '--config', '-C',
        help='Configuration file path'
    )
    
    extract_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    extract_parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    extract_parser.add_argument(
        '--log-file',
        help='Log file path'
    )
    
    extract_parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of files to process in batch (default: 100)'
    )
    
    extract_parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout in seconds for PDF processing (default: 30)'
    )
    
    extract_parser.add_argument(
        '--include-raw-text',
        action='store_true',
        help='Include raw text in output'
    )
    
    extract_parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar'
    )
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Configuration management'
    )
    
    config_parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    
    config_parser.add_argument(
        '--save',
        help='Save current configuration to file'
    )
    
    config_parser.add_argument(
        '--load',
        help='Load configuration from file'
    )
    
    config_parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset to default configuration'
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Show package information'
    )
    
    info_parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    info_parser.add_argument(
        '--fields',
        action='store_true',
        help='Show available extraction fields'
    )
    
    info_parser.add_argument(
        '--formats',
        action='store_true',
        help='Show supported output formats'
    )
    
    return parser.parse_args()


def load_custom_patterns(pattern_file: str) -> dict:
    """
    Load custom extraction patterns from JSON file.
    
    Args:
        pattern_file: Path to JSON file containing patterns
        
    Returns:
        Dictionary of custom patterns
        
    Raises:
        PDFReaderError: If pattern file cannot be loaded
    """
    import json
    
    try:
        with open(pattern_file, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        
        if not isinstance(patterns, dict):
            raise PDFReaderError("Pattern file must contain a JSON object")
        
        logger.info("Loaded %d custom patterns from %s", len(patterns), pattern_file)
        return patterns
        
    except FileNotFoundError:
        raise PDFReaderError(f"Pattern file not found: {pattern_file}")
    except json.JSONDecodeError as e:
        raise PDFReaderError(f"Invalid JSON in pattern file: {e}")
    except Exception as e:
        raise PDFReaderError(f"Error loading pattern file: {e}")


def process_pdf_files(
    pdf_files: List[str],
    password: Optional[str] = None,
    fields: Optional[List[str]] = None,
    custom_patterns: Optional[dict] = None,
    config: Config = None
) -> List[dict]:
    """
    Process multiple PDF files and extract data.
    
    Args:
        pdf_files: List of PDF file paths
        password: Optional password for encrypted PDFs
        fields: Optional list of specific fields to extract
        custom_patterns: Optional custom extraction patterns
        config: Configuration object
        
    Returns:
        List of extracted data dictionaries
    """
    if config is None:
        config = Config()
    
    # Initialize components
    pdf_reader = PDFReader(config)
    extractor = TextExtractor(custom_patterns)
    
    results = []
    total_files = len(pdf_files)
    
    logger.info("Processing %d PDF files", total_files)
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            logger.info("Processing file %d/%d: %s", i, total_files, pdf_file)
            
            # Read PDF
            text_content = pdf_reader.read_pdf(pdf_file, password)
            
            # Extract data
            if fields:
                extracted_data = {}
                for field in fields:
                    value = extractor.extract_specific_field(text_content, field)
                    if value:
                        extracted_data[field] = value
            else:
                extracted_data = extractor.extract_fields(text_content)
            
            # Add metadata
            extracted_data['source_file'] = pdf_file
            extracted_data['extraction_timestamp'] = config.get('timestamp_format')
            
            if config.get('include_raw_text'):
                max_length = config.get('raw_text_max_length', 1000)
                extracted_data['raw_text'] = text_content[:max_length]
            
            results.append(extracted_data)
            logger.info("Successfully extracted %d fields from %s", 
                       len(extracted_data), pdf_file)
            
        except Exception as e:
            logger.error("Failed to process %s: %s", pdf_file, e)
            # Add error record
            error_data = {
                'source_file': pdf_file,
                'error': str(e),
                'extraction_timestamp': config.get('timestamp_format')
            }
            results.append(error_data)
    
    logger.info("Completed processing %d files, %d successful", 
               total_files, len([r for r in results if 'error' not in r]))
    
    return results


def export_data(
    data: List[dict],
    formats: List[str],
    output: Optional[str] = None,
    output_dir: Optional[str] = None,
    config: Config = None
) -> dict:
    """
    Export extracted data to specified formats.
    
    Args:
        data: List of extracted data dictionaries
        formats: List of output formats
        output: Optional output filename
        output_dir: Optional output directory
        config: Configuration object
        
    Returns:
        Dictionary mapping formats to output file paths
    """
    if config is None:
        config = Config()
    
    # Set up exporter
    exporter = DataExporter(output_dir or config.get('output_directory'))
    
    results = {}
    
    for format_type in formats:
        try:
            if format_type == 'excel':
                file_path = exporter.export_to_excel(data, output)
                results['excel'] = file_path
                logger.info("Exported to Excel: %s", file_path)
                
            elif format_type == 'csv':
                if output and output.endswith('.xlsx'):
                    csv_output = output.replace('.xlsx', '.csv')
                else:
                    csv_output = output
                file_path = exporter.export_to_csv(data, csv_output)
                results['csv'] = file_path
                logger.info("Exported to CSV: %s", file_path)
                
        except Exception as e:
            logger.error("Failed to export to %s: %s", format_type, e)
    
    return results


def show_info(args: argparse.Namespace) -> None:
    """Show package information based on arguments."""
    if args.version:
        from . import __version__
        print(f"PDF Reader Package v{__version__}")
    
    if args.fields:
        extractor = TextExtractor()
        fields = extractor.get_available_fields()
        print("\nAvailable extraction fields:")
        for field in fields:
            print(f"  - {field}")
    
    if args.formats:
        print("\nSupported output formats:")
        print("  - excel (Excel spreadsheet)")
        print("  - csv (Comma-separated values)")
    
    if not any([args.version, args.fields, args.formats]):
        print("PDF Reader Package - Extract data from encrypted PDF files")
        print("Use --help for more information")


def handle_config(args: argparse.Namespace) -> None:
    """Handle configuration management commands."""
    config = Config()
    
    if args.show:
        print("\nCurrent configuration:")
        for key, value in config.get_all().items():
            print(f"  {key}: {value}")
    
    if args.save:
        config.save_config_file(args.save)
        print(f"Configuration saved to: {args.save}")
    
    if args.load:
        config.load_config_file(args.load)
        print(f"Configuration loaded from: {args.load}")
    
    if args.reset:
        config.reset_to_defaults()
        print("Configuration reset to defaults")


def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        args = parse_arguments()
        
        # Handle info command
        if args.command == 'info':
            show_info(args)
            return 0
        
        # Handle config command
        if args.command == 'config':
            handle_config(args)
            return 0
        
        # Handle extract command
        if args.command == 'extract':
            # Set up logging
            log_level = 'DEBUG' if args.verbose else args.log_level
            setup_logging(log_level, args.log_file)
            
            # Load configuration
            config = Config(args.config)
            
            # Load custom patterns if specified
            custom_patterns = None
            if args.custom_patterns:
                custom_patterns = load_custom_patterns(args.custom_patterns)
            
            # Process PDF files
            data = process_pdf_files(
                pdf_files=args.pdf_files,
                password=args.password,
                fields=args.fields,
                custom_patterns=custom_patterns,
                config=config
            )
            
            if not data:
                logger.warning("No data extracted from any files")
                return 1
            
            # Export data
            export_results = export_data(
                data=data,
                formats=args.formats,
                output=args.output,
                output_dir=args.output_dir,
                config=config
            )
            
            if export_results:
                print("\nExport completed successfully!")
                for format_type, file_path in export_results.items():
                    print(f"  {format_type.upper()}: {file_path}")
                return 0
            else:
                logger.error("Failed to export data to any format")
                return 1
        
        # No command specified
        print("No command specified. Use --help for usage information.")
        return 1
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except PDFReaderError as e:
        logger.error("PDF Reader error: %s", e)
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return 1


if __name__ == '__main__':
    sys.exit(main()) 