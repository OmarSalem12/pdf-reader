"""
Text extraction and field parsing functionality.
"""

import re
import regex
from datetime import datetime
from typing import Dict, List, Optional, Any
from dateutil import parser as date_parser
from .exceptions import ExtractionError


class FieldExtractor:
    """Extract specific fields from PDF text content."""
    
    def __init__(self, patterns: Dict[str, List[str]]):
        """Initialize extractor with patterns.
        
        Args:
            patterns: Dictionary of pattern types and their regex patterns
        """
        self.patterns = patterns
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficiency.
        
        Returns:
            Dictionary of compiled regex patterns
        """
        compiled = {}
        for pattern_type, pattern_list in self.patterns.items():
            compiled[pattern_type] = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in pattern_list]
        return compiled
    
    def extract_fields(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Extract all fields from text.
        
        Args:
            text: Text content from PDF
            filename: Source filename for reference
            
        Returns:
            Dictionary containing extracted fields
        """
        try:
            extracted_data = {
                "Name": self._extract_name(text),
                "Date of Birth": self._extract_dob(text),
                "Insurance Information": self._extract_insurance(text),
                "Source File": filename,
                "Extraction Date": datetime.now().isoformat(),
                "Raw Text": text[:1000] + "..." if len(text) > 1000 else text  # Truncated for debugging
            }
            
            return extracted_data
            
        except Exception as e:
            raise ExtractionError(f"Error extracting fields: {e}")
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from text.
        
        Args:
            text: Text content to search
            
        Returns:
            Extracted name or None if not found
        """
        for pattern in self.compiled_patterns.get("name_patterns", []):
            match = pattern.search(text)
            if match:
                name = match.group(1).strip()
                # Basic validation - should contain at least 2 words and reasonable length
                words = name.split()
                if len(words) >= 2 and 3 <= len(name) <= 100:
                    # Clean up any extra whitespace or newlines
                    name = re.sub(r'\s+', ' ', name).strip()
                    return name
        
        return None
    
    def _extract_dob(self, text: str) -> Optional[str]:
        """Extract date of birth from text.
        
        Args:
            text: Text content to search
            
        Returns:
            Extracted date as string or None if not found
        """
        for pattern in self.compiled_patterns.get("dob_patterns", []):
            match = pattern.search(text)
            if match:
                date_str = match.group(1).strip()
                # Try to parse and validate the date
                try:
                    parsed_date = date_parser.parse(date_str, dayfirst=False)
                    # Ensure it's a reasonable date (not in the future, not too old)
                    if parsed_date.year > 1900 and parsed_date.year <= datetime.now().year:
                        return parsed_date.strftime("%m/%d/%Y")
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_insurance(self, text: str) -> Optional[str]:
        """Extract insurance information from text.
        
        Args:
            text: Text content to search
            
        Returns:
            Extracted insurance info or None if not found
        """
        insurance_info = []
        
        for pattern in self.compiled_patterns.get("insurance_patterns", []):
            matches = pattern.finditer(text)
            for match in matches:
                info = match.group(1).strip()
                if info and len(info) > 2 and len(info) < 200:
                    # Clean up the extracted text
                    info = re.sub(r'\s+', ' ', info).strip()
                    insurance_info.append(info)
        
        if insurance_info:
            # Return the first found insurance info, or combine multiple
            return "; ".join(insurance_info[:3])  # Limit to first 3 matches
        
        return None
    
    def extract_multiple(self, text_list: List[str], filenames: List[str] = None) -> List[Dict[str, Any]]:
        """Extract fields from multiple text contents.
        
        Args:
            text_list: List of text contents
            filenames: List of corresponding filenames
            
        Returns:
            List of dictionaries containing extracted fields
        """
        if filenames is None:
            filenames = [f"file_{i}" for i in range(len(text_list))]
        
        results = []
        for text, filename in zip(text_list, filenames):
            try:
                extracted = self.extract_fields(text, filename)
                results.append(extracted)
            except ExtractionError as e:
                # Log error but continue with other files
                print(f"Warning: Could not extract from {filename}: {e}")
                results.append({
                    "Name": None,
                    "Date of Birth": None,
                    "Insurance Information": None,
                    "Source File": filename,
                    "Extraction Date": datetime.now().isoformat(),
                    "Error": str(e)
                })
        
        return results 