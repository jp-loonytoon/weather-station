#!/usr/bin/env python3
"""
Simple temperature display application using the BME280 sensor.
Reads temperature data and displays it to the command line.
"""

import time
import sys
from sensor import Sensor
from gpiozero import LED


def main():
    """Main application function to read and display temperature."""
    print("BME280 Temperature Display")
    print("=========================")
    
    try:
        # Initialize the sensor
        led = LED(22)
        sensor = Sensor()
        print("Sensor initialized successfully!\n")
        
        # Read temperature data
        led.on()
        data = sensor.read()
        
        # Display temperature (focusing on temperature as requested)
        print(f"Current Temperature: {data['temperature']:.2f}°C")
        
        # Optional: Show other sensor data for context
        print(f"Humidity: {data['humidity']:.2f}%")
        print(f"Pressure: {data['pressure']:.2f} hPa")
        print(f"Reading taken at: {data['timestamp']}")
        
    except Exception as e:
        print(f"Error reading sensor: {e}")
        sys.exit(1)

    finally:
        time.sleep(1)
        led.off()  # Ensure LED is turned off after reading



if __name__ == "__main__":
    main()
