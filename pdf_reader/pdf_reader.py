"""
Main PDF Reader class for handling encrypted PDF files.
"""

import os
import glob
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from .exceptions import EncryptionError, ExtractionError, OutputError
from .config import Config
from .extractor import FieldExtractor
from .exporter import SpreadsheetExporter


class PDFReader:
    """Main class for reading encrypted PDF files and extracting fields."""
    
    def __init__(self, config_file: str = None):
        """Initialize PDF Reader.
        
        Args:
            config_file: Path to custom configuration JSON file
        """
        self.config = Config(config_file)
        self.extractor = FieldExtractor(self.config.get_patterns())
        self.exporter = SpreadsheetExporter()
    
    def read_pdf(self, file_path: str, password: str = None) -> str:
        """Read and decrypt a single PDF file.
        
        Args:
            file_path: Path to the PDF file
            password: Password for encrypted PDF
            
        Returns:
            Extracted text content from PDF
            
        Raises:
            EncryptionError: If PDF is encrypted and password is incorrect
            ExtractionError: If PDF cannot be read or text cannot be extracted
        """
        try:
            if not os.path.exists(file_path):
                raise ExtractionError(f"PDF file not found: {file_path}")
            
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    if not password:
                        raise EncryptionError(f"PDF is encrypted but no password provided: {file_path}")
                    
                    try:
                        pdf_reader.decrypt(password)
                    except Exception as e:
                        raise EncryptionError(f"Failed to decrypt PDF with provided password: {e}")
                
                # Extract text from all pages
                text_content = ""
                for page in pdf_reader.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    except Exception as e:
                        print(f"Warning: Could not extract text from page: {e}")
                
                if not text_content.strip():
                    raise ExtractionError(f"No text content found in PDF: {file_path}")
                
                return text_content
                
        except Exception as e:
            if isinstance(e, (EncryptionError, ExtractionError)):
                raise
            raise ExtractionError(f"Error reading PDF {file_path}: {e}")
    
    def read_multiple_pdfs(self, file_patterns: List[str], password: str = None) -> List[Dict[str, Any]]:
        """Read multiple PDF files and extract text.
        
        Args:
            file_patterns: List of file patterns (e.g., ["*.pdf", "documents/*.pdf"])
            password: Password for encrypted PDFs
            
        Returns:
            List of dictionaries with file info and text content
        """
        all_files = []
        for pattern in file_patterns:
            files = glob.glob(pattern, recursive=True)
            all_files.extend(files)
        
        if not all_files:
            raise ExtractionError(f"No files found matching patterns: {file_patterns}")
        
        results = []
        for file_path in all_files:
            try:
                text_content = self.read_pdf(file_path, password)
                results.append({
                    "file_path": file_path,
                    "text_content": text_content,
                    "filename": os.path.basename(file_path)
                })
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                results.append({
                    "file_path": file_path,
                    "text_content": "",
                    "filename": os.path.basename(file_path),
                    "error": str(e)
                })
        
        return results
    
    def extract_fields(self, text_content: str, filename: str = "") -> Dict[str, Any]:
        """Extract specific fields from PDF text content.
        
        Args:
            text_content: Text content from PDF
            filename: Source filename for reference
            
        Returns:
            Dictionary containing extracted fields
        """
        return self.extractor.extract_fields(text_content, filename)
    
    def extract_fields_from_multiple(self, pdf_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract fields from multiple PDF text contents.
        
        Args:
            pdf_data: List of dictionaries with text content and file info
            
        Returns:
            List of dictionaries containing extracted fields
        """
        text_list = [item["text_content"] for item in pdf_data]
        filenames = [item["filename"] for item in pdf_data]
        
        return self.extractor.extract_multiple(text_list, filenames)
    
    def export_to_spreadsheet(self, data: List[Dict[str, Any]], output_file: str, 
                            format_type: str = "excel") -> None:
        """Export extracted data to spreadsheet.
        
        Args:
            data: List of dictionaries containing extracted fields
            output_file: Path to output file
            format_type: Output format ("excel" or "csv")
            
        Raises:
            OutputError: If export fails
        """
        try:
            self.exporter.export(data, output_file, format_type)
        except Exception as e:
            raise OutputError(f"Failed to export data: {e}")
    
    def process_single_pdf(self, pdf_path: str, password: str = None, 
                          output_file: str = None) -> Dict[str, Any]:
        """Process a single PDF file end-to-end.
        
        Args:
            pdf_path: Path to PDF file
            password: Password for encrypted PDF
            output_file: Optional output file path
            
        Returns:
            Dictionary containing extracted fields
        """
        # Read PDF
        text_content = self.read_pdf(pdf_path, password)
        
        # Extract fields
        extracted_data = self.extract_fields(text_content, os.path.basename(pdf_path))
        
        # Export if output file specified
        if output_file:
            self.export_to_spreadsheet([extracted_data], output_file)
        
        return extracted_data
    
    def process_multiple_pdfs(self, file_patterns: List[str], password: str = None,
                            output_file: str = None) -> List[Dict[str, Any]]:
        """Process multiple PDF files end-to-end.
        
        Args:
            file_patterns: List of file patterns
            password: Password for encrypted PDFs
            output_file: Optional output file path
            
        Returns:
            List of dictionaries containing extracted fields
        """
        # Read all PDFs
        pdf_data = self.read_multiple_pdfs(file_patterns, password)
        
        # Extract fields from all PDFs
        extracted_data = self.extract_fields_from_multiple(pdf_data)
        
        # Export if output file specified
        if output_file:
            self.export_to_spreadsheet(extracted_data, output_file)
        
        return extracted_data
    
    def update_patterns(self, pattern_type: str, pattern: str) -> None:
        """Add a custom extraction pattern.
        
        Args:
            pattern_type: Type of pattern (name_patterns, dob_patterns, insurance_patterns)
            pattern: Regex pattern to add
        """
        self.config.add_pattern(pattern_type, pattern)
        # Recreate extractor with new patterns
        self.extractor = FieldExtractor(self.config.get_patterns())
    
    def get_patterns(self) -> Dict[str, List[str]]:
        """Get current extraction patterns.
        
        Returns:
            Dictionary of current patterns
        """
        return self.config.get_patterns() 