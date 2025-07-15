#!/usr/bin/env python3
"""
Example usage of the GPS logger.
"""

import signal
from gps import GPSLogger, read_GPS

# Example 1: Read a single GPS fix
print("=== Single GPS Reading ===")
gps_data = read_GPS("/dev/ttyUSB0")  # Change to your GPS port
if gps_data:
    print(f"PC Time: {gps_data['pc_time']}")
    print(f"NMEA Time: {gps_data['nmea_time']}")
    print(f"Latitude: {gps_data['latitude']:.6f}")
    print(f"Longitude: {gps_data['longitude']:.6f}")
else:
    print("Failed to read GPS data")

# Example 2: Continuous logging (run for 30 seconds)
print("\n=== Continuous Logging (30 seconds) ===")
gps_logger = GPSLogger("/dev/ttyUSB0")  # Change to your GPS port

# Start logging in a separate thread would be better for real use
# For demo, we'll just run for a limited time

def signal_handler(signum, frame):
    print("Stopping...")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    # This will run until interrupted
    gps_logger.start_logging()
except KeyboardInterrupt:
    print("Logging stopped by user")
