#!/usr/bin/env python3
"""
Simple temperature reader application using the BME280 sensor.
This application demonstrates how to use the Sensor class to read and
display temperature data.
"""

import time
import sys
from sensor import Sensor
from gpiozero import LED


def display_temperature_data(sensor_data):
    """Display temperature data in a formatted way.
    
    Args:
        sensor_data (dict): Dictionary containing sensor readings
    """
    print(f"Temperature: {sensor_data['temperature']:.2f}°C")
    print(f"Humidity: {sensor_data['humidity']:.2f}%")
    print(f"Pressure: {sensor_data['pressure']:.2f} hPa")
    print(f"Timestamp: {sensor_data['timestamp']}")
    print("-" * 40)


def main():
    """Main application function."""
    print("BME280 Temperature Reader")
    print("========================")
    print("Press Ctrl+C to exit\n")
    
    try:
        # Initialize the sensor
        sensor = Sensor()
        led = LED(22)
        print("Sensor initialized successfully!")
        
        # Option 1: Single reading
        print("\n--- Single Reading ---")
        led.on()
        data = sensor.read()
        display_temperature_data(data)
        led.off()
        
        # Option 2: Continuous readings every 5 seconds
        print("--- Continuous Readings (every 5 seconds) ---")
        print("Press Ctrl+C to stop...\n")
        
        while True:
            led.on()
            data = sensor.read()
            display_temperature_data(data)
            time.sleep(0.25)
            led.off()
            time.sleep(4.75)
            
    except KeyboardInterrupt:
        print("\nExiting temperature reader...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
