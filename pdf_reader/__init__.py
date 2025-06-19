"""
PDF Reader Package

A comprehensive Python package for reading encrypted PDF files, extracting specific
fields (Name, Date of Birth, Insurance information), and exporting data to spreadsheets.

This package provides both programmatic and command-line interfaces for PDF data extraction
with support for encrypted files, custom extraction patterns, and multiple output formats.
"""

__version__ = "1.0.0"
__author__ = "PDF Reader Package"
__description__ = "Extract data from encrypted PDF files and export to spreadsheets"

from .config import Config
from .exceptions import (
    PDFReaderError,
    PDFError,
    EncryptionError,
    ExtractionError,
    ExportError,
    ConfigurationError,
    ValidationError,
    TimeoutError,
    PermissionError,
    DependencyError
)
from .exporter import DataExporter
from .extractor import TextExtractor
from .pdf_reader import PDFReader

__all__ = [
    # Main classes
    'PDFReader',
    'TextExtractor',
    'DataExporter',
    'Config',
    
    # Exceptions
    'PDFReaderError',
    'PDFError',
    'EncryptionError',
    'ExtractionError',
    'ExportError',
    'ConfigurationError',
    'ValidationError',
    'TimeoutError',
    'PermissionError',
    'DependencyError',
    
    # Version info
    '__version__',
    '__author__',
    '__description__'
] 