"""
Command-line interface for PDF Reader package.
"""

import argparse
import sys
import os
from typing import List
from .pdf_reader import PDFReader
from .exceptions import PDFReaderError, EncryptionError, ExtractionError, OutputError


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        run_cli(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Read encrypted PDF files and extract specific fields to spreadsheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single encrypted PDF
  pdf-reader --input document.pdf --password mypassword --output data.xlsx
  
  # Process multiple PDFs with wildcards
  pdf-reader --input "*.pdf" --password mypassword --output results.xlsx
  
  # Use custom configuration
  pdf-reader --input file.pdf --password mypassword --output data.xlsx --config patterns.json
  
  # Export to CSV format
  pdf-reader --input file.pdf --password mypassword --output data.csv --format csv
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input PDF file(s). Can be a single file, multiple files, or glob pattern (e.g., '*.pdf')"
    )
    
    parser.add_argument(
        "--password", "-p",
        help="Password for encrypted PDF files"
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path for spreadsheet (.xlsx or .csv)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to custom configuration JSON file with extraction patterns"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["excel", "csv"],
        default="excel",
        help="Output format (default: excel)"
    )
    
    parser.add_argument(
        "--summary",
        help="Path to save extraction summary report"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser


def run_cli(args):
    """Run the CLI with parsed arguments.
    
    Args:
        args: Parsed command-line arguments
    """
    # Initialize PDF reader
    reader = PDFReader(config_file=args.config)
    
    if args.verbose:
        print("PDF Reader initialized")
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")
        print(f"Format: {args.format}")
        if args.config:
            print(f"Config: {args.config}")
    
    # Determine input files
    input_files = get_input_files(args.input)
    
    if not input_files:
        print(f"Error: No files found matching pattern '{args.input}'")
        sys.exit(1)
    
    if args.verbose:
        print(f"Found {len(input_files)} file(s) to process")
    
    # Process files
    try:
        if len(input_files) == 1:
            # Single file processing
            result = reader.process_single_pdf(
                input_files[0], 
                password=args.password,
                output_file=args.output
            )
            results = [result]
        else:
            # Multiple file processing
            results = reader.process_multiple_pdfs(
                [args.input], 
                password=args.password,
                output_file=args.output
            )
        
        # Print results summary
        print_extraction_summary(results)
        
        # Export summary if requested
        if args.summary:
            reader.exporter.export_summary(results, args.summary)
            print(f"Summary report saved to: {args.summary}")
        
        print(f"Processing completed successfully!")
        print(f"Data exported to: {args.output}")
        
    except EncryptionError as e:
        print(f"Encryption error: {e}")
        print("Please provide the correct password using --password")
        sys.exit(1)
    except ExtractionError as e:
        print(f"Extraction error: {e}")
        sys.exit(1)
    except OutputError as e:
        print(f"Output error: {e}")
        sys.exit(1)
    except PDFReaderError as e:
        print(f"PDF Reader error: {e}")
        sys.exit(1)


def get_input_files(input_pattern: str) -> List[str]:
    """Get list of input files from pattern.
    
    Args:
        input_pattern: File pattern or path
        
    Returns:
        List of matching file paths
    """
    import glob
    
    # Check if it's a single file
    if os.path.isfile(input_pattern):
        return [input_pattern]
    
    # Try glob pattern
    files = glob.glob(input_pattern, recursive=True)
    
    # Filter for PDF files
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    
    return sorted(pdf_files)


def print_extraction_summary(results: List[dict]):
    """Print a summary of extraction results.
    
    Args:
        results: List of extraction results
    """
    total_files = len(results)
    successful = sum(1 for r in results if not r.get("Error"))
    failed = total_files - successful
    
    names_found = sum(1 for r in results if r.get("Name"))
    dobs_found = sum(1 for r in results if r.get("Date of Birth"))
    insurance_found = sum(1 for r in results if r.get("Insurance Information"))
    
    print("\n" + "="*50)
    print("EXTRACTION SUMMARY")
    print("="*50)
    print(f"Total files processed: {total_files}")
    print(f"Successful extractions: {successful}")
    print(f"Failed extractions: {failed}")
    print(f"Names found: {names_found}")
    print(f"Dates of birth found: {dobs_found}")
    print(f"Insurance information found: {insurance_found}")
    print("="*50)
    
    # Show details for failed extractions
    if failed > 0:
        print("\nFailed extractions:")
        for result in results:
            if result.get("Error"):
                print(f"  - {result.get('Source File', 'Unknown')}: {result['Error']}")


if __name__ == "__main__":
    main() 