"""
Text extraction utilities for PDF content.

This module provides functionality to extract structured data from PDF text content
using regular expressions and pattern matching.
"""

import logging
import re
from typing import Dict, List, Optional, Pattern, Union

from .exceptions import ExtractionError

logger = logging.getLogger(__name__)


class TextExtractor:
    """
    A class for extracting structured data from PDF text content.
    
    This class provides methods to extract specific fields from PDF text using
    regular expressions and pattern matching. It supports both predefined patterns
    and custom patterns for flexible data extraction.
    
    Attributes:
        patterns (Dict[str, Pattern]): Dictionary of compiled regex patterns
        custom_patterns (Dict[str, Pattern]): Dictionary of custom regex patterns
    """
    
    def __init__(self, custom_patterns: Optional[Dict[str, object]] = None):
        """
        Initialize the TextExtractor with default and custom patterns.
        
        Args:
            custom_patterns: Optional dictionary of custom regex patterns
                           where keys are field names and values are regex strings or lists of regex strings
        """
        self.patterns = self._get_default_patterns()
        self.custom_patterns = {}
        
        if custom_patterns:
            self.add_custom_patterns(custom_patterns)
            
        logger.debug("TextExtractor initialized with %d default patterns and %d custom patterns",
                    len(self.patterns), len(self.custom_patterns))
    
    def _get_default_patterns(self) -> Dict[str, Pattern]:
        """
        Get the default regex patterns for common fields.
        
        Returns:
            Dictionary mapping field names to compiled regex patterns
        """
        return {
            # Non-greedy, match up to end of line for name
            'name': re.compile(r'Name[:\s]*(.+)', re.IGNORECASE),
            'date_of_birth': re.compile(r'(?:Date of Birth|DOB|Birth Date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', re.IGNORECASE),
            'insurance_number': re.compile(r'(?:Insurance|Policy|Member)[\s#]*Number[:\s]*([A-Za-z0-9-]+)', re.IGNORECASE),
            'insurance_provider': re.compile(r'(?:Insurance|Provider|Company)[:\s]*([A-Za-z\s]+)', re.IGNORECASE),
            'phone': re.compile(r'(?:Phone|Tel|Telephone)[:\s]*(\d{3}[-.]?\d{3}[-.]?\d{4})', re.IGNORECASE),
            'email': re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'),
            'address': re.compile(r'(?:Address)[:\s]*([0-9A-Za-z\s,.-]+)', re.IGNORECASE),
            'ssn': re.compile(r'(?:SSN|Social Security)[:\s]*(\d{3}-\d{2}-\d{4})', re.IGNORECASE),
        }
    
    def add_custom_patterns(self, patterns: Dict[str, object]) -> None:
        """
        Add custom regex patterns for field extraction.
        
        Args:
            patterns: Dictionary where keys are field names and values are regex strings or lists of regex strings
            
        Raises:
            ExtractionError: If any pattern is invalid
        """
        for field_name, pattern_value in patterns.items():
            try:
                if isinstance(pattern_value, str):
                    compiled_pattern = re.compile(pattern_value, re.IGNORECASE)
                    self.custom_patterns[field_name] = compiled_pattern
                    logger.debug("Added custom pattern for field '%s': %s", field_name, pattern_value)
                elif isinstance(pattern_value, list):
                    # Compile all patterns and store as a list
                    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in pattern_value]
                    self.custom_patterns[field_name] = compiled_patterns
                    logger.debug("Added custom pattern list for field '%s': %s", field_name, pattern_value)
                else:
                    raise ExtractionError(f"Pattern for field '{field_name}' must be a string or list of strings.")
            except re.error as e:
                error_msg = f"Invalid regex pattern for field '{field_name}': {pattern_value}"
                logger.error(error_msg)
                raise ExtractionError(error_msg) from e
    
    def extract_fields(self, text: str) -> Dict[str, str]:
        """
        Extract all available fields from the given text.
        
        Args:
            text: The text content to extract fields from
            
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
        
        # Extract using default patterns
        for field_name, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                # For name, only take up to the first line (fixes greedy match)
                if field_name == 'name':
                    value = value.splitlines()[0].strip()
                if value:
                    extracted_data[field_name] = value
                    logger.debug("Extracted field '%s': %s", field_name, value)
        
        # Extract using custom patterns
        for field_name, pattern in self.custom_patterns.items():
            if isinstance(pattern, list):
                for pat in pattern:
                    match = pat.search(text)
                    if match:
                        value = match.group(1).strip()
                        if value:
                            extracted_data[field_name] = value
                            logger.debug("Extracted custom field '%s': %s", field_name, value)
                            break
            else:
                match = pattern.search(text)
                if match:
                    value = match.group(1).strip()
                    if value:
                        extracted_data[field_name] = value
                        logger.debug("Extracted custom field '%s': %s", field_name, value)
        
        logger.info("Extracted %d fields from text", len(extracted_data))
        return extracted_data
    
    def extract_specific_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extract a specific field from the given text.
        
        Args:
            text: The text content to extract from
            field_name: The name of the field to extract
            
        Returns:
            The extracted value if found, None otherwise
            
        Raises:
            ExtractionError: If text is empty or field_name is invalid
        """
        if not text or not text.strip():
            error_msg = "Cannot extract field from empty or invalid text"
            logger.error(error_msg)
            raise ExtractionError(error_msg)
        
        if not field_name:
            error_msg = "Field name cannot be empty"
            logger.error(error_msg)
            raise ExtractionError(error_msg)
        
        logger.debug("Extracting specific field '%s' from text", field_name)
        
        # Check default patterns first
        if field_name in self.patterns:
            match = self.patterns[field_name].search(text)
            if match:
                value = match.group(1).strip()
                if value:
                    logger.debug("Extracted field '%s': %s", field_name, value)
                    return value
        
        # Check custom patterns
        if field_name in self.custom_patterns:
            match = self.custom_patterns[field_name].search(text)
            if match:
                value = match.group(1).strip()
                if value:
                    logger.debug("Extracted custom field '%s': %s", field_name, value)
                    return value
        
        logger.debug("Field '%s' not found in text", field_name)
        return None
    
    def get_available_fields(self) -> List[str]:
        """
        Get a list of all available field names (default + custom).
        
        Returns:
            List of field names that can be extracted
        """
        all_fields = list(self.patterns.keys()) + list(self.custom_patterns.keys())
        logger.debug("Available fields: %s", all_fields)
        return all_fields
    
    def clear_custom_patterns(self) -> None:
        """Clear all custom patterns."""
        count = len(self.custom_patterns)
        self.custom_patterns.clear()
        logger.info("Cleared %d custom patterns", count) 