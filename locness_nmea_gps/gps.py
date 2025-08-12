"""
Simple GPS NMEA data reader and logger.
"""

import sqlite3
import csv
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from pynmeagps import NMEAReader
from serial import Serial, SerialException

logger = logging.getLogger(__name__)


class GPSLogger:
    """Simple GPS data logger for GGA messages."""
    
    def __init__(self, port: str, baudrate: int = 9600, 
                 csv_file: str = "gps_data.csv", 
                 db_file: str = "gps_data.db"):
        self.port = port
        self.baudrate = baudrate
        self.csv_file = csv_file
        self.db_file = db_file
        
        self._init_csv()
        self._init_db()
    
    def _init_csv(self):
        """Initialize CSV file with headers."""
        if not Path(self.csv_file).exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['pc_time', 'nmea_time', 'latitude', 'longitude'])
    
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS gps(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime_utc INTEGER NOT NULL,
                    nmea_time TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def _log_data(self, pc_time: str, nmea_time: str, latitude: float, longitude: float):
        """Log GPS data to both CSV and database."""
        try:
            # Write to CSV
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([pc_time, nmea_time, latitude, longitude])
            
            # Convert ISO string to Unix timestamp for database
            dt = datetime.fromisoformat(pc_time)
            unix_timestamp = int(dt.timestamp())
            
            # Write to database
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    INSERT INTO gps (datetime_utc, nmea_time_utc, latitude, longitude)
                    VALUES (?, ?, ?, ?)
                ''', (unix_timestamp, nmea_time, latitude, longitude))
                conn.commit()
            
            logger.info(f"Logged GPS: {latitude:.6f}, {longitude:.6f}")
            
        except Exception as e:
            logger.error(f"Error logging data: {e}")
    
    def read_gga_single(self) -> Optional[dict]:
        """Read a single GGA message and return parsed data."""
        max_retries = 3
        for retry in range(max_retries):
            try:
                with Serial(self.port, self.baudrate, timeout=5) as stream:
                    nmr = NMEAReader(stream)
                    
                    # Read until we get a GGA message
                    for _ in range(100):  # Max 100 attempts
                        try:
                            raw_data, parsed_data = nmr.read()
                            if parsed_data and parsed_data.msgID == "GGA":
                                nmea_time = str(parsed_data.time) if hasattr(parsed_data, 'time') else ""
                                latitude = float(parsed_data.lat) if hasattr(parsed_data, 'lat') and parsed_data.lat else None
                                longitude = float(parsed_data.lon) if hasattr(parsed_data, 'lon') and parsed_data.lon else None
                                pc_time = datetime.now().isoformat()
                                
                                if latitude is not None and longitude is not None:
                                    return {
                                        'pc_time': pc_time,
                                        'nmea_time': nmea_time,
                                        'latitude': latitude,
                                        'longitude': longitude
                                    }
                        except Exception as e:
                            logger.warning(f"Error reading NMEA data: {e}")
                            time.sleep(1)  # Wait 1 second before retrying
                            continue
                    
                    logger.warning("No valid GGA message received")
                    return None
                    
            except SerialException as e:
                logger.error(f"Serial connection error (attempt {retry + 1}/{max_retries}): {e}")
                if retry < max_retries - 1:
                    time.sleep(1)  # Wait 1 second before retrying
                    continue
                return None
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
    
    def start_logging(self):
        """Start continuous GPS logging."""
        logger.info(f"Starting GPS logging from {self.port}")
        
        while True:
            try:
                with Serial(self.port, self.baudrate, timeout=5) as stream:
                    nmr = NMEAReader(stream)
                    
                    while True:
                        try:
                            raw_data, parsed_data = nmr.read()
                            if parsed_data and parsed_data.msgID == "GGA":
                                nmea_time = str(parsed_data.time) if hasattr(parsed_data, 'time') else ""
                                latitude = float(parsed_data.lat) if hasattr(parsed_data, 'lat') and parsed_data.lat else None
                                longitude = float(parsed_data.lon) if hasattr(parsed_data, 'lon') and parsed_data.lon else None
                                pc_time = datetime.now().isoformat()
                                
                                if latitude is not None and longitude is not None:
                                    self._log_data(pc_time, nmea_time, latitude, longitude)
                        
                        except KeyboardInterrupt:
                            logger.info("Stopping GPS logging...")
                            return
                        except Exception as e:
                            logger.warning(f"Error reading NMEA data: {e}")
                            time.sleep(1)  # Wait 1 second before retrying
                            continue
                            
            except KeyboardInterrupt:
                logger.info("Stopping GPS logging...")
                break
            except SerialException as e:
                logger.error(f"Serial connection error: {e}")
                logger.info("Retrying connection in 1 second...")
                time.sleep(1)  # Wait 1 second before retrying
                continue
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                logger.info("Retrying in 1 second...")
                time.sleep(1)  # Wait 1 second before retrying
                continue


def read_GPS(port: str, baudrate: int = 9600) -> Optional[dict]:
    """
    Simple function to read a single GPS GGA message.
    
    Args:
        port: Serial port (e.g., '/dev/ttyUSB0')
        baudrate: Serial baudrate
        
    Returns:
        Dict with GPS data or None if failed
    """
    gps_logger = GPSLogger(port, baudrate)
    return gps_logger.read_gga_single()
