# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-bme280-data-logger/

import smbus2
import bme280
import os
import time
import pytz
from gpiozero import LED




def read_sensor_data(bus, address, calibration_params):
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)

    return data


def main():
    # Initialize LED
    led = LED(22)

    # BME280 sensor address (default address)
    address = 0x76

    # Initialize I2C bus
    bus = smbus2.SMBus(1)

    # Load calibration parameters
    calibration_params = bme280.load_calibration_params(bus, address)

    led.on()

    data = read_sensor_data(bus, address, calibration_params)

    # Extract data
    temperature = data.temperature
    humidity = data.humidity
    pressure = data.pressure
    timestamp = data.timestamp

    print(f"temperature = {temperature} C")
    print(f"humidity = {humidity} %")
    print(f"pressure = {pressure} hPa")

    desired_timezone = pytz.timezone('Europe/London')
    timestamp_tz = timestamp.replace(tzinfo=pytz.utc).astimezone(desired_timezone)

    print(f"timestamp (utc) = {timestamp.strftime('%H:%M:%S %d-%m-%Y')}")
    print(f"timestamp (local) = {timestamp_tz.strftime('%H:%M:%S %d-%m-%Y')}")

    led.off()


if __name__ == "__main__":
    main()




