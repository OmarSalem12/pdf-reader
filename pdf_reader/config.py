"""
Configuration management for PDF Reader package.

This module provides configuration management functionality including loading
settings from files, environment variables, and providing default configurations.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration management class for PDF Reader package.
    
    This class handles loading and managing configuration settings from various
    sources including environment variables, configuration files, and defaults.
    
    Attributes:
        settings (Dict[str, Any]): Current configuration settings
        config_file (Optional[Path]): Path to configuration file if loaded
    """
    
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
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize configuration with optional config file.
        
        Args:
            config_file: Optional path to configuration file to load
        """
        self.settings = self._get_default_settings()
        self.config_file = None
        
        if config_file:
            self.load_config_file(config_file)
        
        # Override with environment variables
        self._load_from_environment()
        
        logger.info("Configuration initialized with %d settings", len(self.settings))
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default configuration settings.
        
        Returns:
            Dictionary containing default configuration values
        """
        return {
            'output_directory': './output',
            'log_level': 'INFO',
            'log_file': None,
            'max_file_size_mb': 50,
            'supported_formats': ['xlsx', 'csv'],
            'default_format': 'xlsx',
            'timestamp_format': '%Y%m%d_%H%M%S',
            'auto_create_directories': True,
            'extraction_timeout_seconds': 30,
            'max_retries': 3,
            'enable_debug_mode': False,
            'custom_patterns': {},
            'export_metadata': True,
            'auto_cleanup_temp_files': True,
            'temp_directory': None,
            'encryption_timeout_seconds': 60,
            'batch_size': 100,
            'enable_progress_bar': True,
            'output_encoding': 'utf-8',
            'excel_engine': 'openpyxl',
            'csv_delimiter': ',',
            'include_raw_text': False,
            'raw_text_max_length': 1000,
            'field_validation': True,
            'date_format': '%m/%d/%Y',
            'phone_format': '###-###-####',
            'ssn_format': '###-##-####',
            'insurance_format': 'auto',
            'error_handling': 'continue',  # 'continue', 'stop', 'log_only'
            'backup_extracted_data': False,
            'backup_directory': './backups',
            'compression_enabled': False,
            'compression_level': 6,
            'email_notifications': False,
            'email_recipients': [],
            'smtp_server': 'localhost',
            'smtp_port': 587,
            'smtp_username': None,
            'smtp_password': None,
            'notification_threshold': 100,
            'performance_monitoring': False,
            'cache_enabled': False,
            'cache_directory': './cache',
            'cache_ttl_hours': 24,
            'api_rate_limit': 100,  # requests per minute
            'api_timeout_seconds': 30,
            'webhook_url': None,
            'webhook_headers': {},
            'webhook_timeout_seconds': 10,
            'data_retention_days': 30,
            'privacy_mode': False,  # Mask sensitive data in logs
            'audit_logging': False,
            'audit_file': './audit.log',
            'version': '1.0.0',
            'author': 'PDF Reader Package',
            'description': 'PDF data extraction and export utility'
        }
    
    def load_config_file(self, config_file: Union[str, Path]) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            error_msg = f"Configuration file not found: {config_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # For now, we'll support basic key=value format
            # In a full implementation, you might want to support JSON, YAML, etc.
            with open(config_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            
                            # Convert value to appropriate type
                            value = self._convert_value(value)
                            
                            self.settings[key] = value
                            logger.debug("Loaded config: %s = %s", key, value)
            
            self.config_file = config_path
            logger.info("Configuration loaded from file: %s", config_path)
            
        except Exception as e:
            error_msg = f"Failed to load configuration file {config_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
    
    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate Python type.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value with appropriate type
        """
        # Boolean values
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        elif value.lower() in ('false', 'no', 'off', '0'):
            return False
        
        # Integer values
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # List values (comma-separated)
        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split(',')
            return [item.strip().strip('"\'') for item in items if item.strip()]
        
        # Default to string
        return value
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_prefix = 'PDF_READER_'
        
        for key in self.settings.keys():
            env_key = f"{env_prefix}{key.upper()}"
            env_value = os.getenv(env_key)
            
            if env_value is not None:
                converted_value = self._convert_value(env_value)
                self.settings[key] = converted_value
                logger.debug("Loaded from environment: %s = %s", env_key, converted_value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        self.settings[key] = value
        logger.debug("Configuration updated: %s = %s", key, value)
    
    def update(self, settings: Dict[str, Any]) -> None:
        """
        Update multiple configuration settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        self.settings.update(settings)
        logger.info("Updated %d configuration settings", len(settings))
    
    def save_config_file(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """
        Save current configuration to a file.
        
        Args:
            config_file: Optional path to save config file.
                        If None, uses the loaded config file path
        """
        if config_file is None:
            if self.config_file is None:
                raise ValueError("No config file path specified and no file was loaded")
            config_file = self.config_file
        
        config_path = Path(config_file)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("# PDF Reader Configuration File\n")
                f.write(f"# Generated on: {self.settings.get('version', 'Unknown')}\n\n")
                
                for key, value in self.settings.items():
                    if isinstance(value, str) and ' ' in value:
                        f.write(f'{key}="{value}"\n')
                    else:
                        f.write(f'{key}={value}\n')
            
            logger.info("Configuration saved to file: %s", config_path)
            
        except Exception as e:
            error_msg = f"Failed to save configuration file {config_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration settings.
        
        Returns:
            Dictionary containing all configuration settings
        """
        return self.settings.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.settings = self._get_default_settings()
        logger.info("Configuration reset to defaults")
    
    def validate(self) -> bool:
        """
        Validate current configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate required directories
            output_dir = Path(self.settings['output_directory'])
            if not output_dir.exists() and not self.settings['auto_create_directories']:
                logger.warning("Output directory does not exist: %s", output_dir)
            
            # Validate log level
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.settings['log_level'].upper() not in valid_log_levels:
                logger.error("Invalid log level: %s", self.settings['log_level'])
                return False
            
            # Validate numeric values
            if self.settings['max_file_size_mb'] <= 0:
                logger.error("Max file size must be positive")
                return False
            
            if self.settings['extraction_timeout_seconds'] <= 0:
                logger.error("Extraction timeout must be positive")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error("Configuration validation failed: %s", e)
            return False
    
    def get_output_directory(self) -> Path:
        """
        Get the configured output directory, creating it if necessary.
        
        Returns:
            Path to output directory
        """
        output_dir = Path(self.settings['output_directory'])
        
        if self.settings['auto_create_directories'] and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created output directory: %s", output_dir)
        
        return output_dir
    
    def get_temp_directory(self) -> Path:
        """
        Get the configured temporary directory, creating it if necessary.
        
        Returns:
            Path to temporary directory
        """
        temp_dir = self.settings['temp_directory']
        if temp_dir is None:
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / 'pdf_reader'
        else:
            temp_dir = Path(temp_dir)
        
        if self.settings['auto_create_directories'] and not temp_dir.exists():
            temp_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("Created temp directory: %s", temp_dir)
        
        return temp_dir
    
    def get_patterns(self) -> Dict[str, List[str]]:
        """Get current patterns.
        
        Returns:
            Dictionary of pattern types and their regex patterns
        """
        return self.DEFAULT_PATTERNS.copy()
    
    def add_pattern(self, pattern_type: str, pattern: str) -> None:
        """Add a custom pattern.
        
        Args:
            pattern_type: Type of pattern (name_patterns, dob_patterns, insurance_patterns)
            pattern: Regex pattern to add
        """
        if pattern_type not in self.DEFAULT_PATTERNS:
            raise ConfigurationError(f"Invalid pattern type: {pattern_type}")
        
        self.DEFAULT_PATTERNS[pattern_type].append(pattern)
    
    def save_config(self, config_file: str) -> None:
        """Save current configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_PATTERNS, f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration: {e}") 