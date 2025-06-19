"""
Text extraction functionality for PDF Reader package.

This module provides functionality to extract structured data from PDF text
content using regular expressions and pattern matching.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union, Mapping

from .exceptions import ExtractionError

logger = logging.getLogger(__name__)


class TextExtractor:
    """
    A class for extracting structured data from PDF text content.

    This class provides methods to extract specific fields from PDF text using
    regular expressions and pattern matching. It supports both predefined
    patterns and custom patterns for flexible data extraction.

    Attributes:
        patterns (Dict[str, Pattern]): Dictionary of compiled regex patterns
        custom_patterns (Dict[str, Pattern]): Dictionary of custom regex 
        patterns
    """

    def __init__(self, 
                 custom_patterns: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the TextExtractor.

        Args:
            custom_patterns: Optional dictionary of custom regex patterns
        """
        self.patterns = self._get_default_patterns()
        self.custom_patterns = custom_patterns or {}

        if custom_patterns:
            self.patterns.update(custom_patterns)

        logger.debug(
            "TextExtractor initialized with %d default patterns \
                and %d custom patterns",
            len(self.patterns),
            len(self.custom_patterns),
        )

    def _get_default_patterns(self) -> Dict[str, List[str]]:
        """
        Get the default regex patterns for common fields.

        Returns:
            Dictionary mapping field names to compiled regex patterns
        """
        return {
            "name": [
                r"Name:\s*([A-Za-z\s]+?)(?:\n|$)",
                r"Full Name:\s*([A-Za-z\s]+?)(?:\n|$)",
                r"Patient Name:\s*([A-Za-z\s]+?)(?:\n|$)",
                r"Client Name:\s*([A-Za-z\s]+?)(?:\n|$)",
                r"^([A-Z][a-z]+ [A-Z][a-z]+)$",
            ],
            "date_of_birth": [
                r"Date of Birth:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"DOB:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Birth Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ],
            "insurance": [
                r"Insurance:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
                r"Policy Number:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
                r"Insurance Company:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
                r"Policy:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
                r"Group Number:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
            ],
            "phone": [
                r"Phone:\s*(\d{3}[-.]?\d{3}[-.]?\d{4})",
                r"Telephone:\s*(\d{3}[-.]?\d{3}[-.]?\d{4})",
                r"(\d{3}[-.]?\d{3}[-.]?\d{4})",
            ],
            "email": [
                r"Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            ],
            "ssn": [
                r"SSN:\s*(\d{3}-\d{2}-\d{4})",
                r"Social Security:\s*(\d{3}-\d{2}-\d{4})",
                r"(\d{3}-\d{2}-\d{4})",
            ],
        }

    def extract_fields(
        self, text: str, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract all available fields from the given text.

        Args:
            text: The text content to extract fields from
            fields: Specific fields to extract (if None, extract all)

        Returns:
            Dictionary mapping field names to extracted values

        Raises:
            ExtractionError: If text is empty or invalid
        """
        if not text or not text.strip():
            error_msg = "Cannot extract fields from empty or invalid text"
            logger.error(error_msg)
            raise ExtractionError(error_msg)

        logger.debug("Extracting fields from text of length %d", len(text))

        extracted_data = {}
        target_fields = fields or list(self.patterns.keys())

        for field in target_fields:
            if field in self.patterns:
                value = self.extract_specific_field(text, field)
                if value:
                    extracted_data[field] = value

        logger.info("Extracted %d fields from text", len(extracted_data))
        return extracted_data

    def extract_specific_field(self, text: str, field: str) -> Optional[str]:
        """
        Extract a specific field from the given text.

        Args:
            text: The text content to extract from
            field: The name of the field to extract

        Returns:
            The extracted value if found, None otherwise

        Raises:
            ExtractionError: If text is empty or field_name is invalid
        """
        if not text or not text.strip():
            error_msg = "Cannot extract field from empty or invalid text"
            logger.error(error_msg)
            raise ExtractionError(error_msg)

        if not field:
            error_msg = "Field name cannot be empty"
            logger.error(error_msg)
            raise ExtractionError(error_msg)

        logger.debug("Extracting specific field '%s' from text", field)

        if field not in self.patterns:
            logger.warning("Unknown field: %s", field)
            return None

        try:
            patterns = self.patterns[field]
            for pattern in patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if value:
                        logger.debug("Extracted field '%s': %s", field, value)
                        return value

            logger.debug("Field '%s' not found in text", field)
            return None

        except Exception as e:
            error_msg = f"Failed to extract field {field}: {e}"
            logger.error(error_msg)
            raise ExtractionError(error_msg, field_name=field)

    def get_available_fields(self) -> List[str]:
        """
        Get a list of all available field names (default + custom).

        Returns:
            List of field names that can be extracted
        """
        all_fields = list(self.patterns.keys())
        logger.debug("Available fields: %s", all_fields)
        return all_fields

    def add_pattern(self, field: str, pattern: str) -> None:
        """
        Add custom regex pattern for field extraction.

        Args:
            field: Field name
            pattern: Regex pattern
        """
        if field not in self.patterns:
            self.patterns[field] = []

        self.patterns[field].append(pattern)
        logger.info("Added custom pattern for field %s: %s", field, pattern)

    def validate_pattern(self, pattern: str) -> bool:
        """
        Validate regex pattern.

        Args:
            pattern: Regex pattern to validate

        Returns:
            True if pattern is valid
        """
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    def extract_with_custom_patterns(
        self, text: str, patterns: Mapping[str, Union[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Extract fields using custom patterns.

        Args:
            text: Text content to extract from
            patterns: Custom patterns dictionary

        Returns:
            Dictionary of extracted field values

        Raises:
            ExtractionError: If extraction fails
        """
        if not text:
            raise ExtractionError("No text content provided")

        try:
            extracted_data = {}

            for field, pattern_list in patterns.items():
                if isinstance(pattern_list, str):
                    pattern_list = [pattern_list]

                for pattern in pattern_list:
                    if not self.validate_pattern(pattern):
                        logger.warning(
                            "Invalid pattern for field %s: %s", field, pattern
                        )
                        continue

                    match = re.search(
                        pattern, text, re.MULTILINE | re.IGNORECASE
                    )
                    if match:
                        value = match.group(1).strip()
                        if value:
                            extracted_data[field] = value
                            break

            logger.info(
                "Extracted %d fields with custom patterns",
                len(extracted_data)
            )
            return extracted_data

        except Exception as e:
            error_msg = f"Failed to extract with custom patterns: {e}"
            logger.error(error_msg)
            raise ExtractionError(error_msg)
