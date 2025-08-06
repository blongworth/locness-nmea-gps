"""
Configuration loader for GPS logger.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import tomllib


def load_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """
    Load configuration from TOML file.
    
    Args:
        config_path: Path to the TOML configuration file
        
    Returns:
        Dictionary containing configuration data
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"Error: Configuration file '{config_path}' not found")
        sys.exit(1)
    
    try:
        with open(config_file, 'rb') as f:
            config = tomllib.load(f)
        return config
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)


def get_gps_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract GPS-specific configuration."""
    return {
        'port': config.get('gps', {}).get('port', '/dev/ttyUSB0'),
        'baudrate': config.get('gps', {}).get('baudrate', 9600),
        'timeout': config.get('gps', {}).get('timeout', 5),
    }


def get_files_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract file-specific configuration."""
    return {
        'csv_filename': config.get('files', {}).get('csv_filename', 'gps_data.csv'),
        'db_filename': config.get('files', {}).get('db_filename', 'gps_data.db'),
    }


def get_database_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract database-specific configuration."""
    return {
        'table_name': config.get('database', {}).get('table_name', 'gps_data'),
    }


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract logging-specific configuration."""
    return {
        'console_level': config.get('logging', {}).get('console_level', 'INFO'),
        'file_level': config.get('logging', {}).get('file_level', 'DEBUG'),
        'format': config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        'file': config.get('logging', {}).get('file', 'gps_app.log'),
        'console': config.get('logging', {}).get('console', True),
    }
