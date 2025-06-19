"""
Main PDF Reader class for handling encrypted PDF files.
"""

import os
import glob
import logging
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from .exceptions import EncryptionError, ExtractionError, ExportError
from .config import Config
from .extractor import TextExtractor
from .exporter import DataExporter

logger = logging.getLogger(__name__)

class PDFReader:
    """Main class for reading encrypted PDF files and extracting fields."""
    
    def __init__(self, config_file: Optional[str] = None) -> None:
        """Initializes the PDFReader.
        
        Args:
            config_file (Optional[str]): Path to custom configuration JSON file.
        """
        self.config = Config(config_file)
        self.extractor = TextExtractor(self.config.get_patterns())
        self.exporter = DataExporter()
    
    def read_pdf(self, file_path: str, password: Optional[str] = None) -> str:
        """Reads and decrypts a single PDF file.
        
        Args:
            file_path (str): Path to the PDF file.
            password (Optional[str]): Password for encrypted PDF.
        
        Returns:
            str: Extracted text content from PDF.
        
        Raises:
            EncryptionError: If PDF is encrypted and password is incorrect.
            ExtractionError: If PDF cannot be read or text cannot be extracted.
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
                        logger.warning(f"Could not extract text from page: {e}")
                
                if not text_content.strip():
                    raise ExtractionError(f"No text content found in PDF: {file_path}")
                
                return text_content
                
        except Exception as e:
            if isinstance(e, (EncryptionError, ExtractionError)):
                raise
            raise ExtractionError(f"Error reading PDF {file_path}: {e}")
    
    def read_multiple_pdfs(self, file_patterns: List[str], password: Optional[str] = None) -> List[Dict[str, Any]]:
        """Reads multiple PDF files and extracts text.
        
        Args:
            file_patterns (List[str]): List of file patterns (e.g., ["*.pdf", "documents/*.pdf"]).
            password (Optional[str]): Password for encrypted PDFs.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries with file info and text content.
        """
        all_files: List[str] = []
        for pattern in file_patterns:
            files = glob.glob(pattern, recursive=True)
            all_files.extend(files)
        
        if not all_files:
            raise ExtractionError(f"No files found matching patterns: {file_patterns}")
        
        results: List[Dict[str, Any]] = []
        for file_path in all_files:
            try:
                text_content = self.read_pdf(file_path, password)
                results.append({
                    "file_path": file_path,
                    "text_content": text_content,
                    "filename": os.path.basename(file_path)
                })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                results.append({
                    "file_path": file_path,
                    "text_content": "",
                    "filename": os.path.basename(file_path),
                    "error": str(e)
                })
        
        return results
    
    def extract_fields(self, text_content: str, filename: str = "") -> Dict[str, Any]:
        """Extracts specific fields from PDF text content.
        
        Args:
            text_content (str): Text content from PDF.
            filename (str): Source filename for reference.
        
        Returns:
            Dict[str, Any]: Dictionary containing extracted fields.
        """
        return self.extractor.extract_fields(text_content, filename)
    
    def extract_fields_from_multiple(self, pdf_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts fields from multiple PDF text contents.
        
        Args:
            pdf_data (List[Dict[str, Any]]): List of dictionaries with text content and file info.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing extracted fields.
        """
        text_list = [item["text_content"] for item in pdf_data]
        filenames = [item["filename"] for item in pdf_data]
        
        return self.extractor.extract_multiple(text_list, filenames)
    
    def export_to_spreadsheet(self, data: List[Dict[str, Any]], output_file: str, 
                            format_type: str = "excel") -> None:
        """Exports extracted data to spreadsheet.
        
        Args:
            data (List[Dict[str, Any]]): List of dictionaries containing extracted fields.
            output_file (str): Path to output file.
            format_type (str): Output format ("excel" or "csv").
        
        Raises:
            ExportError: If export fails.
        """
        try:
            self.exporter.export(data, output_file, format_type)
        except Exception as e:
            raise ExportError(f"Failed to export data: {e}")
    
    def process_single_pdf(self, pdf_path: str, password: Optional[str] = None, 
                          output_file: Optional[str] = None) -> Dict[str, Any]:
        """Processes a single PDF file end-to-end.
        
        Args:
            pdf_path (str): Path to PDF file.
            password (Optional[str]): Password for encrypted PDF.
            output_file (Optional[str]): Optional output file path.
        
        Returns:
            Dict[str, Any]: Dictionary containing extracted fields.
        """
        text_content = self.read_pdf(pdf_path, password)
        extracted_data = self.extract_fields(text_content, os.path.basename(pdf_path))
        if output_file:
            self.export_to_spreadsheet([extracted_data], output_file)
        return extracted_data
    
    def process_multiple_pdfs(self, file_patterns: List[str], password: Optional[str] = None,
                            output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """Processes multiple PDF files end-to-end.
        
        Args:
            file_patterns (List[str]): List of file patterns.
            password (Optional[str]): Password for encrypted PDFs.
            output_file (Optional[str]): Optional output file path.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing extracted fields.
        """
        pdf_data = self.read_multiple_pdfs(file_patterns, password)
        extracted_data = self.extract_fields_from_multiple(pdf_data)
        if output_file:
            self.export_to_spreadsheet(extracted_data, output_file)
        return extracted_data
    
    def update_patterns(self, pattern_type: str, pattern: str) -> None:
        """Adds a custom extraction pattern.
        
        Args:
            pattern_type (str): Type of pattern (name_patterns, dob_patterns, insurance_patterns).
            pattern (str): Regex pattern to add.
        """
        self.config.add_pattern(pattern_type, pattern)
        self.extractor = TextExtractor(self.config.get_patterns())
    
    def get_patterns(self) -> Dict[str, List[str]]:
        """Gets current extraction patterns.
        
        Returns:
            Dict[str, List[str]]: Dictionary of current patterns.
        """
        return self.config.get_patterns() 