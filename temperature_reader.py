#!/usr/bin/env python3
"""
Simple temperature reader application using the BME280 sensor.
This application demonstrates how to use the Sensor class to read and
display temperature data.
"""

import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from sensor import Sensor
from gpiozero import LED

LOGFILE_MAX_SIZE = 1 * 1024 * 1024  # 1 MB
SAMPLE_INTERVAL = 60        # how many seconds between samples
LED_PIN = 22                # GPIO pin for the indicator LED
LED_DURATION = 0.15         # how long the indicator LED flashes for


def setup_logging():
    """Set up logging configuration to write to weather.log file."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('weather.log',
                                maxBytes=LOGFILE_MAX_SIZE,
                                backupCount=5),
            logging.StreamHandler()  # Also log to console
        ]
    )
    return logging.getLogger(__name__)


def display_temperature_data(sensor_data, logger=None):
    """Display temperature data in a formatted way.

    Args:
        sensor_data (dict): Dictionary containing sensor readings
        logger: Logger instance for writing to log file
    """
    temp_str = f"Temperature: {sensor_data['temperature']:.2f}°C"
    humidity_str = f"Humidity: {sensor_data['humidity']:.2f}%"
    pressure_str = f"Pressure: {sensor_data['pressure']:.2f} hPa"
    timestamp_str = f"Timestamp: {sensor_data['timestamp']}"

    # Display to console
    print(temp_str)
    print(humidity_str)
    print(pressure_str)
    print(timestamp_str)
    print("-" * 40)

    # Log to file if logger is provided
    if logger:
        log_msg = (f"Sensor Reading - {temp_str}, {humidity_str}, "
                   f"{pressure_str}")
        logger.info(log_msg)


def main():
    """Main application function."""
    print("BME280 Temperature Reader")
    print("========================")
    print("Press Ctrl+C to exit\n")

    # Set up logging
    logger = setup_logging()
    logger.info("Starting BME280 Temperature Reader")

    try:
        # Initialize the sensor
        sensor = Sensor()
        led = LED(LED_PIN)
        print("Sensor initialized successfully")
        logger.info("Sensor and LED initialized successfully")

        # Continuous readings every SAMPLE_INTERVAL seconds
        print("--- Continuous Readings ---")
        print("Press Ctrl+C to stop...\n")
        logger.info("Starting continuous readings every %d seconds",
                    SAMPLE_INTERVAL)

        while True:
            led.on()
            data = sensor.read()
            display_temperature_data(data, logger)
            time.sleep(LED_DURATION)
            
            led.off()
            time.sleep(SAMPLE_INTERVAL - LED_DURATION)
            
    except KeyboardInterrupt:
        print("\nExiting temperature reader...")
        logger.info("Temperature reader stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
