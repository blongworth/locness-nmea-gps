# GPS NMEA Logger

A simple Python application to read GPS NMEA data from a serial stream, parse GGA messages, and log the data to both CSV files and SQLite database.

## Features

- Reads NMEA GGA messages from serial GPS devices
- Logs PC timestamp, NMEA time, latitude, and longitude
- Dual output: CSV file and SQLite database
- Simple command-line interface
- Robust error handling

## Installation

```bash
# Install dependencies
pip install pynmeagps pyserial

# Or if using uv
uv sync
```

## Configuration

The GPS logger uses a TOML configuration file (`config.toml`) for default settings:

```toml
[gps]
port = "/dev/ttyUSB0"
baudrate = 9600
timeout = 5

[files]
csv_filename = "gps_data.csv"
db_filename = "gps_data.db"

[database]
table_name = "gps_data"

[logging]
console_level = "INFO"           # Console log level: DEBUG, INFO, WARNING, ERROR
file_level = "DEBUG"             # File log level: DEBUG, INFO, WARNING, ERROR
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
file = "gps_app.log"             # Log file name
console = true                   # Enable/disable console output (default: true)
```

## Usage

### Command Line Interface

```bash
# Use default configuration
python main.py

# Use custom configuration file
python main.py --config my_config.toml

# Single GPS reading
python main.py --single

# Override specific settings
python main.py --port /dev/ttyUSB1 --baudrate 4800

# Custom output files
python main.py --csv-file my_gps.csv --db-file my_gps.db
```

### Python API

```python
from gps import GPSLogger, read_GPS

# Read single GPS fix
data = read_GPS("/dev/ttyUSB0")
if data:
    print(f"Location: {data['latitude']}, {data['longitude']}")

# Continuous logging
logger = GPSLogger("/dev/ttyUSB0")
logger.start_logging()  # Runs until interrupted
```

## Output Format

### CSV File
```
pc_time,nmea_time,latitude,longitude
2025-07-14T10:30:45.123456,103045.00,37.7749,-122.4194
```

### SQLite Database
Table: `gps_data`
- `id`: Primary key
- `datetime_utc`: Unix timestamp (integer)
- `nmea_time`: NMEA time string
- `latitude`: Latitude in decimal degrees
- `longitude`: Longitude in decimal degrees
- `created_at`: Database timestamp

### Query Database
```bash
# Display latest 10 records
python query_db.py

# Display latest 20 records
python query_db.py --limit 20

# Use custom database file
python query_db.py --db-file my_gps.db
```

## Error Handling

- Serial connection errors are logged and handled gracefully
- Invalid NMEA messages are skipped
- Database and file I/O errors are logged
- Keyboard interrupts stop logging cleanly

## Requirements

- Python 3.13+
- pynmeagps >= 1.0.50
- pyserial >= 3.5

## License

This project is open source.
