"""
Configuration management for PDF Reader package.
"""

import json
import os
from typing import Dict, List, Any
from .exceptions import ConfigurationError


class Config:
    """Configuration class for PDF Reader."""
    
    DEFAULT_PATTERNS = {
        "name_patterns": [
            r"Name:\s*([A-Za-z\s]+?)(?:\n|$)",
            r"Full Name:\s*([A-Za-z\s]+?)(?:\n|$)",
            r"Patient Name:\s*([A-Za-z\s]+?)(?:\n|$)",
            r"Client Name:\s*([A-Za-z\s]+?)(?:\n|$)",
            r"^([A-Z][a-z]+ [A-Z][a-z]+)$",  # Basic name pattern on its own line
        ],
        "dob_patterns": [
            r"Date of Birth:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"DOB:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"Birth Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # General date pattern
        ],
        "insurance_patterns": [
            r"Insurance:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
            r"Policy Number:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
            r"Insurance Company:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
            r"Policy:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
            r"Group Number:\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
        ]
    }
    
    def __init__(self, config_file: str = None):
        """Initialize configuration.
        
        Args:
            config_file: Path to custom configuration JSON file
        """
        self.patterns = self.DEFAULT_PATTERNS.copy()
        
        if config_file:
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
            
        Raises:
            ConfigurationError: If config file is invalid or cannot be read
        """
        try:
            if not os.path.exists(config_file):
                raise ConfigurationError(f"Configuration file not found: {config_file}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update patterns with custom ones
            for pattern_type, patterns in config_data.items():
                if pattern_type in self.patterns:
                    self.patterns[pattern_type] = patterns
                    
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def get_patterns(self) -> Dict[str, List[str]]:
        """Get current patterns.
        
        Returns:
            Dictionary of pattern types and their regex patterns
        """
        return self.patterns.copy()
    
    def add_pattern(self, pattern_type: str, pattern: str) -> None:
        """Add a custom pattern.
        
        Args:
            pattern_type: Type of pattern (name_patterns, dob_patterns, insurance_patterns)
            pattern: Regex pattern to add
        """
        if pattern_type not in self.patterns:
            raise ConfigurationError(f"Invalid pattern type: {pattern_type}")
        
        self.patterns[pattern_type].append(pattern)
    
    def save_config(self, config_file: str) -> None:
        """Save current configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration: {e}") 