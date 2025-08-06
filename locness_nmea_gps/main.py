#!/usr/bin/env python3
"""
Simple GPS logger main module.
"""

# TODO: Fix runaaway issues with logging Error reading NMEA data error

import argparse
import logging
import sys
from locness_nmea_gps.gps import GPSLogger, read_GPS
from locness_nmea_gps.config_loader import (
    load_config, get_gps_config, get_files_config, 
    get_logging_config
)


def setup_logging(config: dict):
    """Setup logging with both console and file output."""
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set root logger to the most verbose level needed
    console_level = getattr(logging, config.get('console_level', 'DEBUG').upper())
    file_level = getattr(logging, config.get('file_level', 'DEBUG').upper())
    root_logger.setLevel(min(console_level, file_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config['format'])
    
    # Console handler 
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if config.get('file'):
        file_handler = logging.FileHandler(config['file'])
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple GPS NMEA logger")
    parser.add_argument("--config", "-c", default="config.toml",
                       help="Configuration file (default: config.toml)")
    parser.add_argument("--port", "-p", 
                       help="Serial port (overrides config)")
    parser.add_argument("--baudrate", "-b", type=int,
                       help="Serial baudrate (overrides config)")
    parser.add_argument("--single", "-s", action="store_true",
                       help="Read single GPS fix and exit")
    parser.add_argument("--csv-file", default=None,
                       help="CSV output file (overrides config)")
    parser.add_argument("--db-file", default=None,
                       help="SQLite database file (overrides config)")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    gps_config = get_gps_config(config)
    files_config = get_files_config(config)
    logging_config = get_logging_config(config)
    
    # Override with command line arguments
    if args.port:
        gps_config['port'] = args.port
    if args.baudrate:
        gps_config['baudrate'] = args.baudrate
    if args.csv_file:
        files_config['csv_filename'] = args.csv_file
    if args.db_file:
        files_config['db_filename'] = args.db_file
    
    setup_logging(logging_config)
    
    if args.single:
        # Single reading mode
        print(f"Reading single GPS fix from {gps_config['port']}...")
        data = read_GPS(gps_config['port'], gps_config['baudrate'])
        
        if data:
            print("GPS Data:")
            print(f"  PC Time: {data['pc_time']}")
            print(f"  NMEA Time: {data['nmea_time']}")
            print(f"  Latitude: {data['latitude']:.6f}")
            print(f"  Longitude: {data['longitude']:.6f}")
        else:
            print("Failed to read GPS data")
            sys.exit(1)
    else:
        # Continuous logging mode
        gps_logger = GPSLogger(
            gps_config['port'], 
            gps_config['baudrate'], 
            files_config['csv_filename'], 
            files_config['db_filename']
        )
        try:
            gps_logger.start_logging()
        except KeyboardInterrupt:
            print("\nStopping GPS logger...")


if __name__ == "__main__":
    main()
