#!/usr/bin/env python3
"""
Data Storage Example

This script demonstrates how to use the DataStorage class with the BME280
sensor to store temperature, humidity, and pressure readings in a SQLite
database.

Example usage:
    python3 data_storage_example.py

Author: Weather Station Project
Date: July 2025
"""

import time
import logging
from sensor import Sensor
from data_storage import DataStorage

def setup_logging():
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function demonstrating DataStorage usage."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize sensor
        logger.info("Initializing BME280 sensor...")
        sensor = Sensor()
        
        # Use chip_id as channel_id as specified in the requirements
        channel_id = sensor.chip_id
        logger.info(f"Using chip_id {channel_id} as channel_id")
        
        # Initialize data storage
        logger.info("Initializing data storage...")
        with DataStorage('datalogger.db') as storage:
            
            # Take a single reading
            logger.info("Taking sensor reading...")
            reading = sensor.read()
            
            logger.info(f"Sensor reading: T={reading['temperature']:.2f}°C, "
                       f"H={reading['humidity']:.1f}%, P={reading['pressure']:.2f} hPa")
            
            # Store the reading in the database
            success = storage.store_reading(
                channel_id=channel_id,
                temperature=reading['temperature'],
                humidity=reading['humidity'],
                pressure=reading['pressure'],
                timestamp=int(reading['timestamp'])
            )
            
            if success:
                logger.info("Reading stored successfully in database")
            else:
                logger.error("Failed to store reading in database")
            
            # Demonstrate retrieving the latest reading
            latest = storage.get_latest_reading(channel_id)
            if latest:
                logger.info(f"Latest reading from database: T={latest['temperature']:.2f}°C, "
                           f"H={latest['humidity']:.1f}%, P={latest['pressure']:.2f} hPa, "
                           f"Time={latest['timestamp']}")
            
            # Example of batch storage (storing multiple readings)
            logger.info("Taking 3 readings for batch storage example...")
            readings_batch = []
            
            for i in range(3):
                time.sleep(1)  # Wait 1 second between readings
                reading = sensor.read()
                readings_batch.append({
                    'channel_id': channel_id,
                    'temperature': reading['temperature'],
                    'humidity': reading['humidity'],
                    'pressure': reading['pressure'],
                    'timestamp': int(reading['timestamp'])
                })
                logger.info(f"Reading {i+1}: T={reading['temperature']:.2f}°C")
            
            # Store batch
            stored_count = storage.store_readings_batch(readings_batch)
            logger.info(f"Stored {stored_count} readings in batch")
            
            # Demonstrate time range query
            end_time = int(time.time())
            start_time = end_time - 300  # Last 5 minutes
            
            range_readings = storage.get_readings_range(
                channel_id=channel_id,
                start_time=start_time,
                end_time=end_time,
                limit=10
            )
            
            logger.info(f"Retrieved {len(range_readings)} readings from last 5 minutes")
            for reading in range_readings[-3:]:  # Show last 3
                logger.info(f"  Time={reading['timestamp']}: T={reading['temperature']:.2f}°C, "
                           f"H={reading['humidity']:.1f}%, P={reading['pressure']:.2f} hPa")
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    main()
