#!/usr/bin/env python3
"""
BME280 Data Logger Class

This module provides a configurable data logger for the BME280 sensor that
periodically samples temperature, humidity, and pressure data. The logger
supports customizable logging levels, LED indicator duration, and sampling
intervals. It is designed to run on a Raspberry Pi.`

Features:
- Configurable sampling intervals with continuous logging
- Ability to log temperature, humidity, and pressure data
- Adjustable LED indicator duration

Example:
    Basic usage of the DataLogger class:

    >>> from datalogger import DataLogger
    >>> dl = DataLogger()
    >>> dl.start_logging()

Author: james@ecreationtech.co.uk
Date: July 2025
"""

import time
from datetime import datetime
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from gpiozero import LED
from sensor import Sensor
from data_storage import DataStorage

DATALOGGER_UUID = "609219BA-72F6-5D0D-A0F1-3FF7E603B2DC"
GPIO_LED_PIN = 22
DEFAULT_SAMPLE_INTERVAL = 60  # seconds
DEFAULT_LED_DURATION = 0.15  # seconds
DATABASE_FILE = 'datalogger.db'


class DataLogger:
    """
    BME280 Data Logger Class

    A configurable data logger that periodically samples BME280 sensor data
    and logs it to both console and file outputs. Provides visual feedback
    through an LED indicator and supports various configuration options.

    Features:
    - Configurable sampling intervals with continuous logging
    - Ability to log temperature, humidity, and pressure data
    - Adjustable LED indicator duration

    Attributes:
        sensor (Sensor): BME280 sensor interface instance
        led (LED): GPIO LED indicator instance
        logger (logging.Logger): Python logger instance
        led_duration (float): Duration to keep LED on during readings
        log_level (str): Current logging level
        is_running (bool): Flag indicating if continuous logging is active

    Example:
        Create and configure a data logger:

        >>> datalogger = DataLogger(
        ...     sensor_address=0x76,
        ...     led_pin=22,
        ...     log_level='INFO',
        ...     led_duration=0.5,
        ...     log_file='weather.log'
        ... )
        >>> datalogger.start_continuous_logging(interval=10)
    """

    def __init__(self,
                 sensor_address: int = 0x76,
                 sensor_bus: int = 1,
                 led_pin: int = GPIO_LED_PIN,
                 backing_store: str = None,
                 log_level: str = 'WARNING',
                 led_duration: float = DEFAULT_LED_DURATION,
                 log_file: str = 'weather.log',
                 max_log_size: int = 1024 * 1024,
                 backup_count: int = 5):
        """
        Initialize the DataLogger with configurable parameters.

        Args:
            sensor_address (int): I2C address of BME280 sensor (default: 0x76)
            sensor_bus (int): I2C bus number (default: 1)
            led_pin (int): GPIO pin number for LED indicator (default: 22)
            backing_store (str): Local database file for storing readings
            log_level (str): Logging level ('DEBUG', 'INFO', 'WARNING',
                           'ERROR')
            led_duration (float): Duration to keep LED on during readings
                                (seconds)
            log_file (str): Name of the log file (default: 'weather.log')
            max_log_size (int): Maximum log file size in bytes (default: 1MB)
            backup_count (int): Number of backup log files to keep (default: 5)

        Raises:
            ValueError: If invalid log level is provided
            Exception: If sensor or LED initialization fails
        """
        self.led_duration = led_duration
        self.log_level = log_level.upper()
        self.is_running = False
        self.storage = None

        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if self.log_level not in valid_levels:
            msg = f"Invalid log level. Must be one of: {valid_levels}"
            raise ValueError(msg)

        try:
            self.sensor = Sensor(address=sensor_address, bus_number=sensor_bus)
            self.led = LED(led_pin)
            self.logger = self._setup_logging(
                log_file, max_log_size, backup_count)
            log_msg = ("DataLogger initialized")
            self.logger.info(log_msg)
            if backing_store is not None:
                self.storage = DataStorage(backing_store)
                log_msg += (f"Using backing store: {backing_store}")

            self.logger.info(log_msg)
        except Exception as e:
            print(f"Failed to initialize DataLogger: {e}")
            raise

    def _setup_logging(self, log_file: str, max_size: int,
                       backup_count: int) -> logging.Logger:
        """
        Set up logging configuration with rotating file handler.

        Args:
            log_file (str): Name of the log file
            max_size (int): Maximum log file size in bytes
            backup_count (int): Number of backup files to keep

        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.log_level))
        logger.handlers.clear()

        # Create formatter
        fmt_string = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt_string)

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, self.log_level))

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, self.log_level))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def set_log_level(self, level: str) -> None:
        """
        Change the logging level dynamically. Possible logging
        levels are 'DEBUG', 'INFO', 'WARNING', 'ERROR'.

        Args:
            level (str): New logging level

        Raises:
            ValueError: If invalid log level is provided
        """
        level = level.upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

        if level not in valid_levels:
            msg = f"Invalid log level. Must be one of: {valid_levels}"
            raise ValueError(msg)

        self.log_level = level
        log_level_obj = getattr(logging, level)
        self.logger.setLevel(log_level_obj)
        for handler in self.logger.handlers:
            handler.setLevel(log_level_obj)

        self.logger.info(f"Log level changed to: {level}")

    def set_led_duration(self, duration: float) -> None:
        """
        Set the duration for LED indicator during readings.

        Args:
            duration (float): Duration in seconds to keep LED on
        """
        if duration < 0:
            raise ValueError("LED duration must be non-negative")

        self.led_duration = duration
        self.logger.info(f"LED duration set to: {duration}s")

    def _read_data(self) -> dict:
        """
        Read sensor data and return the results.

        Returns:
            dict: Sensor reading data
        """

        try:
            self.led.on()
            data = self.sensor.read()

            # Keep LED on for specified duration
            if self.led_duration > 0:
                time.sleep(self.led_duration)

            return data

        finally:
            # Always turn off LED
            self.led.off()

    def start_continuous_logging(self,
                                 interval: float = DEFAULT_SAMPLE_INTERVAL,
                                 duration: Optional[float] = None) -> None:
        """
        Start continuous data logging at specified intervals.

        Args:
            interval (float): Time between readings in seconds
            duration (Optional[float]): Total duration to log in seconds.
                None for infinite logging (default: None)
        """

        def convert_datestring_to_timestamp(date_input: datetime) -> int:
            unix_timestamp = int(date_input.timestamp())
            return unix_timestamp

        if interval <= 0:
            raise ValueError("Interval must be positive")

        self.is_running = True
        start_time = time.time()

        print(f"Starting continuous logging every {interval} seconds")
        if duration:
            print(f"Logging for {duration} seconds total")
        print("Press Ctrl+C to stop...\n")

        self.logger.info(
            f"Starting continuous logging - Interval: {interval}s")
        if duration:
            self.logger.info(f"Will continue logging for {duration}s")

        try:
            while self.is_running:
                data = self._read_data()    # take the sensor reading

                temp_str = f"{data['temperature']:.3f}°C"
                humidity_str = f"{data['humidity']:.3f}%"
                pressure_str = f"{data['pressure']:.3f} hPa"
                unix_timestamp = convert_datestring_to_timestamp(
                    data['timestamp'])

                if self.storage is not None:
                    self.storage.store_reading(
                        channel_id=self.sensor.chip_id,
                        temperature=data['temperature'],
                        humidity=data['humidity'],
                        pressure=data['pressure'],
                        timestamp=unix_timestamp
                    )

                log_msg = (f"Sensor data - "
                           f"Timestamp: {unix_timestamp}, "
                           f"Temperature: {temp_str}, "
                           f"Humidity: {humidity_str}, "
                           f"Pressure: {pressure_str}")
                self.logger.info(log_msg)

                # Check if duration limit reached
                if duration and (time.time() - start_time) >= duration:
                    self.logger.info(
                        "Duration limit reached, stopping logging")
                    break

                # Wait for next reading (minus LED duration already waited)
                sleep_time = interval - self.led_duration
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.logger.info("Continuous logging stopped by user")
        finally:
            self.is_running = False
            print("\nLogging stopped")

    def stop_logging(self) -> None:
        """Stop continuous logging if currently running."""
        if self.is_running:
            self.is_running = False
            self.logger.info("Logging stopped programmatically")

    def get_status(self) -> dict:
        """
        Get current status of the data logger.

        Returns:
            dict: Status information including configuration and state
        """
        return {
            'is_running': self.is_running,
            'log_level': self.log_level,
            'led_duration': self.led_duration,
            'sensor_address': self.sensor.address,
            'led_pin': self.led.pin.number
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        try:
            self.led.off()
            self.led.close()
        except Exception as e:
            # Log specific cleanup errors but continue with exit
            self.logger.error(f"Error occurred during cleanup: {e}")
            pass

        if exc_type:
            self.logger.error(f"Exception occurred: {exc_val}")


def main():
    """Main function demonstrating DataLogger usage."""
    print("BME280 Data Logger")
    print("==================")

    try:
        with DataLogger(backing_store=DATABASE_FILE, log_level='INFO') as dl:
            dl.start_continuous_logging(interval=DEFAULT_SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("\nExiting data logger...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
