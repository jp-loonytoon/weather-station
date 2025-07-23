#!/usr/bin/env python3
"""
Example script demonstrating DataLogger usage with different configurations.
"""

from datalogger import DataLogger
import sys


def example_basic_usage():
    """Demonstrate basic DataLogger usage."""
    print("=== Basic DataLogger Example ===")
    
    try:
        # Create data logger with default settings
        with DataLogger() as logger:
            # Take a single reading
            print("\nTaking single reading...")
            logger.take_single_reading()
            
            # Short continuous logging demo (10 seconds)
            print("\nStarting 10-second continuous logging demo...")
            logger.start_continuous_logging(interval=2.0, duration=10.0)
            
    except Exception as e:
        print(f"Error in basic example: {e}")


def example_custom_configuration():
    """Demonstrate DataLogger with custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    try:
        # Create data logger with custom settings
        with DataLogger(
            led_pin=22,
            log_level='DEBUG',
            led_duration=1.0,
            log_file='custom_weather.log'
        ) as logger:
            
            print(f"Logger status: {logger.get_status()}")
            
            # Change settings dynamically
            logger.set_led_duration(0.1)
            logger.set_log_level('INFO')
            
            # Take readings
            logger.take_single_reading()
            
    except Exception as e:
        print(f"Error in custom example: {e}")


def main():
    """Run all examples."""
    print("DataLogger Examples")
    print("==================")
    
    try:
        example_basic_usage()
        example_custom_configuration()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
