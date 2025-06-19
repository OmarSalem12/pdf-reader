"""
Custom exceptions for PDF Reader package.
"""


class PDFReaderError(Exception):
    """
    Base exception class for PDF Reader package.

    This is the base exception that all other exceptions in the package inherit from.
    It provides a common interface for error handling across the package.
    """

    def __init__(self, message: str, details: str = None):
        """
        Initialize the PDFReaderError.

        Args:
            message: Primary error message
            details: Optional additional details about the error
        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class PDFError(PDFReaderError):
    """
    Exception raised for PDF-related errors.

    This exception is raised when there are issues with PDF files themselves,
    such as corrupted files, unsupported formats, or access problems.
    """

    def __init__(
        self, message: str, file_path: str = None, details: str = None
    ):
        """
        Initialize the PDFError.

        Args:
            message: Error message describing the PDF issue
            file_path: Optional path to the problematic PDF file
            details: Optional additional details about the error
        """
        self.file_path = file_path
        if file_path:
            message = f"{message} (File: {file_path})"
        super().__init__(message, details)


class EncryptionError(PDFError):
    """
    Exception raised for PDF encryption-related errors.

    This exception is raised when there are issues with encrypted PDFs,
    such as missing passwords, incorrect passwords, or unsupported encryption.
    """

    def __init__(
        self, message: str, file_path: str = None, encryption_type: str = None
    ):
        """
        Initialize the EncryptionError.

        Args:
            message: Error message describing the encryption issue
            file_path: Optional path to the encrypted PDF file
            encryption_type: Optional type of encryption that failed
        """
        self.encryption_type = encryption_type
        if encryption_type:
            message = f"{message} (Encryption: {encryption_type})"
        super().__init__(message, file_path)


class ExtractionError(PDFError):
    """
    Exception raised for data extraction errors.

    This exception is raised when there are issues extracting data from PDFs,
    such as missing text content, invalid patterns, or extraction failures.
    """

    def __init__(
        self, message: str, field_name: str = None, text_length: int = None
    ):
        """
        Initialize the ExtractionError.

        Args:
            message: Error message describing the extraction issue
            field_name: Optional name of the field that failed to extract
            text_length: Optional length of text that was being processed
        """
        self.field_name = field_name
        self.text_length = text_length

        details = []
        if field_name:
            details.append(f"Field: {field_name}")
        if text_length is not None:
            details.append(f"Text length: {text_length}")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)


class ExportError(PDFError):
    """
    Exception raised for data export errors.

    This exception is raised when there are issues exporting extracted data,
    such as file permission problems, disk space issues, or format errors.
    """

    def __init__(
        self, message: str, output_path: str = None, format_type: str = None
    ):
        """
        Initialize the ExportError.

        Args:
            message: Error message describing the export issue
            output_path: Optional path where export was attempted
            format_type: Optional format type that failed (e.g., 'excel', 'csv')
        """
        self.output_path = output_path
        self.format_type = format_type

        details = []
        if output_path:
            details.append(f"Output: {output_path}")
        if format_type:
            details.append(f"Format: {format_type}")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)


class ConfigurationError(PDFError):
    """
    Exception raised for configuration-related errors.

    This exception is raised when there are issues with configuration files,
    settings, or environment variables.
    """

    def __init__(
        self, message: str, config_key: str = None, config_file: str = None
    ):
        """
        Initialize the ConfigurationError.

        Args:
            message: Error message describing the configuration issue
            config_key: Optional configuration key that caused the error
            config_file: Optional path to the configuration file
        """
        self.config_key = config_key
        self.config_file = config_file

        details = []
        if config_key:
            details.append(f"Key: {config_key}")
        if config_file:
            details.append(f"File: {config_file}")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)


class ValidationError(PDFError):
    """
    Exception raised for data validation errors.

    This exception is raised when extracted data fails validation checks,
    such as invalid formats, missing required fields, or data type mismatches.
    """

    def __init__(
        self,
        message: str,
        field_name: str = None,
        value: str = None,
        expected_format: str = None,
    ):
        """
        Initialize the ValidationError.

        Args:
            message: Error message describing the validation issue
            field_name: Optional name of the field that failed validation
            value: Optional value that failed validation
            expected_format: Optional expected format for the field
        """
        self.field_name = field_name
        self.value = value
        self.expected_format = expected_format

        details = []
        if field_name:
            details.append(f"Field: {field_name}")
        if value is not None:
            details.append(f"Value: {value}")
        if expected_format:
            details.append(f"Expected: {expected_format}")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)


class TimeoutError(PDFError):
    """
    Exception raised for operation timeout errors.

    This exception is raised when operations take longer than expected,
    such as PDF processing, data extraction, or export operations.
    """

    def __init__(
        self, message: str, operation: str = None, timeout_seconds: int = None
    ):
        """
        Initialize the TimeoutError.

        Args:
            message: Error message describing the timeout issue
            operation: Optional name of the operation that timed out
            timeout_seconds: Optional timeout duration in seconds
        """
        self.operation = operation
        self.timeout_seconds = timeout_seconds

        details = []
        if operation:
            details.append(f"Operation: {operation}")
        if timeout_seconds:
            details.append(f"Timeout: {timeout_seconds}s")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)


class PermissionError(PDFError):
    """
    Exception raised for permission-related errors.

    This exception is raised when there are insufficient permissions
    to read files, write output, or access system resources.
    """

    def __init__(
        self, message: str, file_path: str = None, operation: str = None
    ):
        """
        Initialize the PermissionError.

        Args:
            message: Error message describing the permission issue
            file_path: Optional path to the file that caused the permission error
            operation: Optional operation that failed due to permissions
        """
        self.file_path = file_path
        self.operation = operation

        details = []
        if file_path:
            details.append(f"File: {file_path}")
        if operation:
            details.append(f"Operation: {operation}")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)


class DependencyError(PDFError):
    """
    Exception raised for missing or incompatible dependencies.

    This exception is raised when required dependencies are missing,
    incompatible, or not properly installed.
    """

    def __init__(
        self,
        message: str,
        dependency_name: str = None,
        required_version: str = None,
    ):
        """
        Initialize the DependencyError.

        Args:
            message: Error message describing the dependency issue
            dependency_name: Optional name of the missing dependency
            required_version: Optional required version of the dependency
        """
        self.dependency_name = dependency_name
        self.required_version = required_version

        details = []
        if dependency_name:
            details.append(f"Dependency: {dependency_name}")
        if required_version:
            details.append(f"Required: {required_version}")

        details_str = "; ".join(details) if details else None
        super().__init__(message, details_str)
