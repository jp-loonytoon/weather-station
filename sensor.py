"""
BME280 Sensor Interface Module

This module provides a Python interface for the BME280 temperature, humidity,
and pressure sensor using I2C communication. The BME280 is a combined digital
humidity, pressure and temperature sensor based on proven sensing principles.

The module provides:
- Simple sensor initialization and configuration
- Single sensor reading functionality
- Periodic sampling with configurable intervals
- Proper error handling and sensor calibration

Compatible with Raspberry Pi and other single-board computers with I2C support.

Example:
    Basic usage of the Sensor class:
    
    >>> from sensor import Sensor
    >>> sensor = Sensor()
    >>> data = sensor.read()
    >>> print(f"Temperature: {data['temperature']:.2f}°C")
    
Author: Weather Station Project
Date: July 2025
"""

import time
import smbus2
import bme280


class Sensor:
    """
    BME280 Environmental Sensor Interface Class
    
    This class provides a high-level interface to the BME280 sensor, which
    measures temperature, humidity, and atmospheric pressure. The sensor
    communicates via I2C protocol and requires proper calibration for
    accurate readings.
    
    The BME280 sensor features:
    - Temperature measurement range: -40°C to +85°C
    - Humidity measurement range: 0% to 100% RH
    - Pressure measurement range: 300 to 1100 hPa
    - High accuracy and low power consumption
    
    Attributes:
        address (int): I2C address of the BME280 sensor
        bus (smbus2.SMBus): I2C bus interface object
        calibration_params: Sensor-specific calibration parameters
    
    Example:
        Initialize sensor and take a reading:
        
        >>> sensor = Sensor(address=0x76, bus_number=1)
        >>> reading = sensor.read()
        >>> print(f"Temp: {reading['temperature']:.1f}°C")
        >>> print(f"Humidity: {reading['humidity']:.1f}%")
        >>> print(f"Pressure: {reading['pressure']:.1f} hPa")
        
    Note:
        Ensure the BME280 sensor is properly connected to the I2C bus
        and that I2C is enabled on your system before using this class.
    """

    def __init__(self, address=0x76, bus_number=1):
        """Initialize the BME280 sensor.
        
        Args:
            address: The I2C address of the sensor (default: 0x76)
            bus_number: The I2C bus number (default: 1)
        """
        self.address = address
        self.bus = smbus2.SMBus(bus_number)
        self.calibration_params = bme280.load_calibration_params(
            self.bus, self.address)

    def read(self):
        """Read current sensor data.
        
        Returns:
            dict: Dictionary containing temperature, humidity, pressure
                  and timestamp
        """
        data = bme280.sample(self.bus, self.address, self.calibration_params)

        return {
            'temperature': data.temperature,
            'humidity': data.humidity,
            'pressure': data.pressure,
            'timestamp': data.timestamp
        }

    def sample(self, interval_seconds, count=1):
        """Sample sensor data periodically.

        Args:
            interval_seconds: Time between samples in seconds
            count: Number of samples to take (default: 1, 0 for infinite)

        Returns:
            list: List of sensor readings
        """
        readings = []
        samples_taken = 0

        while count == 0 or samples_taken < count:
            readings.append(self.read())
            samples_taken += 1

            if count == 0 or samples_taken < count:
                time.sleep(interval_seconds)

        return readings
