"""
Custom exceptions for the PDF Reader package.
"""


class PDFReaderError(Exception):
    """Base exception for PDF Reader package."""
    pass


class EncryptionError(PDFReaderError):
    """Raised when there's an issue with PDF encryption/decryption."""
    pass


class ExtractionError(PDFReaderError):
    """Raised when there's an issue extracting text or fields from PDF."""
    pass


class ConfigurationError(PDFReaderError):
    """Raised when there's an issue with configuration files or settings."""
    pass


class OutputError(PDFReaderError):
    """Raised when there's an issue writing output files."""
    pass 