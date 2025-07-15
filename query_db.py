#!/usr/bin/env python3
"""
Query GPS database and display data.
"""

import sqlite3
from datetime import datetime
import argparse


def query_gps_data(db_file: str, limit: int = 10):
    """Query GPS data from database and display it."""
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.execute('''
                SELECT datetime_utc, nmea_time, latitude, longitude, created_at
                FROM gps_data 
                ORDER BY datetime_utc DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            if not rows:
                print("No GPS data found in database.")
                return
            
            print(f"Latest {len(rows)} GPS records:")
            print("-" * 80)
            print(f"{'PC Time (UTC)':<20} {'NMEA Time':<12} {'Latitude':<12} {'Longitude':<12} {'Created':<20}")
            print("-" * 80)
            
            for row in rows:
                unix_time, nmea_time, lat, lon, created = row
                
                # Convert Unix timestamp back to readable format
                pc_time = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"{pc_time:<20} {nmea_time:<12} {lat:<12.6f} {lon:<12.6f} {created:<20}")
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Query GPS database")
    parser.add_argument("--db-file", "-d", default="gps_data.db",
                       help="SQLite database file (default: gps_data.db)")
    parser.add_argument("--limit", "-l", type=int, default=10,
                       help="Number of records to display (default: 10)")
    
    args = parser.parse_args()
    query_gps_data(args.db_file, args.limit)


if __name__ == "__main__":
    main()
