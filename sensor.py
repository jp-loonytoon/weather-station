import smbus2
import bme280
import time
from gpiozero import LED

class Sensor:
    def __init__(self, address=0x76, bus_number=1):
        """Initialize the BME280 sensor.
        
        Args:
            address: The I2C address of the sensor (default: 0x76)
            bus_number: The I2C bus number (default: 1)
        """
        self.address = address
        self.bus = smbus2.SMBus(bus_number)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
    
    def read(self):
        """Read current sensor data.
        
        Returns:
            dict: Dictionary containing temperature, humidity, pressure and timestamp
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