"""
Configuration management for PDF Reader package.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration management class for PDF Reader package.

    This class handles loading and managing configuration settings from
    various sources including environment variables, configuration files,
    and defaults.

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
            r"^([A-Z][a-z]+ [A-Z][a-z]+)$",  # Basic name pattern
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
        ],
    }

    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize configuration with optional config file.

        Args:
            config_file: Optional path to configuration file to load
        """
        self.settings = self._get_default_settings()
        self.config_file: Optional[Path] = None

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
            "output_directory": "./output",
            "log_level": "INFO",
            "log_file": None,
            "max_file_size_mb": 50,
            "supported_formats": ["xlsx", "csv"],
            "default_format": "xlsx",
            "timestamp_format": "%Y%m%d_%H%M%S",
            "auto_create_directories": True,
            "extraction_timeout_seconds": 30,
            "max_retries": 3,
            "enable_debug_mode": False,
            "custom_patterns": {},
            "export_metadata": True,
            "auto_cleanup_temp_files": True,
            "temp_directory": None,
            "encryption_timeout_seconds": 60,
            "batch_size": 100,
            "enable_progress_bar": True,
            "output_encoding": "utf-8",
            "excel_engine": "openpyxl",
            "csv_delimiter": ",",
            "include_raw_text": False,
            "raw_text_max_length": 1000,
            "field_validation": True,
            "date_format": "%m/%d/%Y",
            "phone_format": "###-###-####",
            "ssn_format": "###-##-####",
            "insurance_format": "auto",
            "error_handling": "continue",  # 'continue', 'stop', 'log_only'
            "backup_extracted_data": False,
            "backup_directory": "./backups",
            "compression_enabled": False,
            "compression_level": 6,
            "email_notifications": False,
            "email_recipients": [],
            "smtp_server": "localhost",
            "smtp_port": 587,
            "smtp_username": None,
            "smtp_password": None,
            "notification_threshold": 100,
            "performance_monitoring": False,
            "cache_enabled": False,
            "cache_directory": "./cache",
            "cache_ttl_hours": 24,
            "api_rate_limit": 100,  # requests per minute
            "api_timeout_seconds": 30,
            "webhook_url": None,
            "webhook_headers": {},
            "webhook_timeout_seconds": 10,
            "data_retention_days": 30,
            "privacy_mode": False,  # Mask sensitive data in logs
            "audit_logging": False,
            "audit_file": "./audit.log",
            "version": "1.0.0",
            "author": "PDF Reader Package",
            "description": "PDF data extraction and export utility",
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
            # Support JSON format
            with open(config_path, "r", encoding="utf-8") as f:
                file_settings = json.load(f)

            if not isinstance(file_settings, dict):
                raise ValueError("Config file must contain a JSON object")

            self.settings.update(file_settings)
            self.config_file = config_path
            logger.info("Configuration loaded from file: %s", config_path)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file {config_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to load config file {config_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_prefix = "PDF_READER_"

        for key in self.settings:
            env_key = env_prefix + key.upper()
            if env_key in os.environ:
                value = os.environ[env_key]
                # Convert string values to appropriate types
                if isinstance(self.settings[key], bool):
                    self.settings[key] = value.lower() in ("true", "1", "yes")
                elif isinstance(self.settings[key], int):
                    try:
                        self.settings[key] = int(value)
                    except ValueError:
                        logger.warning(
                            "Invalid integer value for %s: %s", env_key, value
                        )
                elif isinstance(self.settings[key], list):
                    self.settings[key] = value.split(",")
                else:
                    self.settings[key] = value

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
        logger.debug("Set config: %s = %s", key, value)

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
                raise ConfigurationError("No config file path specified")
            config_file = self.config_file

        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, default=str)

            logger.info("Configuration saved to: %s", config_path)

        except Exception as e:
            error_msg = f"Failed to save config file {config_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg) from e

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
        required_keys = ["output_directory", "log_level", "default_format"]
        for key in required_keys:
            if key not in self.settings:
                logger.error("Missing required configuration key: %s", key)
                return False

        # Validate output directory
        output_dir = self.settings.get("output_directory")
        if output_dir and not Path(output_dir).parent.exists():
            logger.warning("Output directory parent does not exist: %s", output_dir)

        # Validate log level
        log_level = self.settings.get("log_level")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            logger.error("Invalid log level: %s", log_level)
            return False

        logger.info("Configuration validation passed")
        return True

    def get_output_directory(self) -> Path:
        """
        Get the configured output directory, creating it if necessary.

        Returns:
            Path to output directory
        """
        output_dir = Path(self.settings["output_directory"])

        if self.settings["auto_create_directories"] and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created output directory: %s", output_dir)

        return output_dir

    def get_temp_directory(self) -> Path:
        """
        Get the configured temporary directory, creating it if necessary.

        Returns:
            Path to temporary directory
        """
        temp_dir_setting = self.settings["temp_directory"]
        if temp_dir_setting is None:
            import tempfile

            temp_dir = Path(tempfile.gettempdir()) / "pdf_reader"
        else:
            temp_dir = Path(temp_dir_setting)

        if self.settings["auto_create_directories"] and not temp_dir.exists():
            temp_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("Created temp directory: %s", temp_dir)

        return temp_dir

    def get_patterns(self) -> Dict[str, List[str]]:
        """Get current patterns.

        Returns:
            Dictionary of pattern types and their regex patterns
        """
        patterns = self.DEFAULT_PATTERNS.copy()
        custom_patterns = self.settings.get("custom_patterns", {})
        patterns.update(custom_patterns)
        return patterns

    def add_pattern(self, pattern_type: str, pattern: str) -> None:
        """Add a custom pattern.

        Args:
            pattern_type: Type of pattern (name_patterns, dob_patterns,
            insurance_patterns)
            pattern: Regex pattern to add
        """
        if pattern_type not in self.DEFAULT_PATTERNS:
            raise ConfigurationError(f"Invalid pattern type: {pattern_type}")

        if "custom_patterns" not in self.settings:
            self.settings["custom_patterns"] = {}

        if pattern_type not in self.settings["custom_patterns"]:
            self.settings["custom_patterns"][pattern_type] = []

        self.settings["custom_patterns"][pattern_type].append(pattern)
        logger.info("Added custom pattern for %s: %s", pattern_type, pattern)

    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> "Config":
        """Create Config instance from file.

        Args:
            config_file: Path to configuration file

        Returns:
            Config instance

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        try:
            return cls(config_file)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {config_file}: {e}")

    def save_config(self, config_file: str) -> None:
        """Save current configuration to JSON file.

        Args:
            config_file: Path to save configuration file
        """
        self.save_config_file(config_file)
