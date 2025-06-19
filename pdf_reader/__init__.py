"""
PDF Reader Package

A Python package for reading encrypted PDF files and extracting specific fields.
"""

from .pdf_reader import PDFReader
from .exceptions import PDFReaderError, EncryptionError, ExtractionError

__version__ = "1.0.0"
__author__ = "PDF Reader Team"
__email__ = "info@pdfreader.com"

__all__ = ["PDFReader", "PDFReaderError", "EncryptionError", "ExtractionError"] 