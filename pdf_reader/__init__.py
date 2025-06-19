"""PDF Reader package for extracting data from encrypted PDF files.

This package provides functionality to read encrypted PDF files,
extract specific fields using regex patterns, and export data to
spreadsheets.
"""

from .pdf_reader import PDFReader
from .extractor import TextExtractor
from .exporter import DataExporter
from .config import Config
from .exceptions import (
    PDFError,
    EncryptionError,
    ExtractionError,
    ExportError,
    ConfigurationError,
)

__version__ = "1.0.0"
__author__ = "PDF Reader Team"
__email__ = "support@pdfreader.com"

__all__ = [
    "PDFReader",
    "TextExtractor",
    "DataExporter",
    "Config",
    "PDFError",
    "EncryptionError",
    "ExtractionError",
    "ExportError",
    "ConfigurationError",
]
