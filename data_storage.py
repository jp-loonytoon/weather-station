"""
Data Storage Module

This module provides a DataStorage class for writing temperature, humidity,
and pressure data from BME280 sensors to a SQLite database. The class handles
database connections, table creation, and data insertion operations.

The module manages sensor data storage with the following features:
- SQLite database connection management
- Automatic table creation if not exists
- Batch insert operations for efficiency
- Proper error handling and logging
- Thread-safe database operations

Example:
    Basic usage of the DataStorage class:
    
    >>> from data_storage import DataStorage
    >>> storage = DataStorage('datalogger.db')
    >>> storage.store_reading(channel_id=123, temperature=25.5, 
    ...                      humidity=60.2, pressure=1013.25)
    
Author: Weather Station Project
Date: July 2025
"""

import sqlite3
import time
import logging
from typing import Optional, Dict, Any, List
from threading import Lock


class DataStorage:
    """
    Data Storage Class for BME280 Sensor Data
    
    This class provides a thread-safe interface for storing temperature,
    humidity, and pressure readings from BME280 sensors into a SQLite database.
    The class handles database initialization, connection management, and
    provides methods for both single and batch data insertions.
    
    The database schema includes:
    - channel_info: Stores channel metadata (channel_id, channel_name)
    - channel_data: Stores sensor readings with timestamps
    
    Attributes:
        db_path (str): Path to the SQLite database file
        connection (sqlite3.Connection): Database connection object
        lock (threading.Lock): Thread synchronization lock
        logger (logging.Logger): Logger instance for error reporting
    
    Example:
        Initialize storage and store sensor data:
        
        >>> storage = DataStorage('weather_data.db')
        >>> storage.store_reading(
        ...     channel_id=42,
        ...     temperature=23.5,
        ...     humidity=65.0,
        ...     pressure=1015.2,
        ...     timestamp=int(time.time())
        ... )
        >>> storage.close()
    """
    
    def __init__(self, db_path: str = 'datalogger.db'):
        """
        Initialize the DataStorage with database connection.
        
        Args:
            db_path (str): Path to the SQLite database file
                          (default: 'datalogger.db')
        
        Raises:
            sqlite3.Error: If database connection or initialization fails
        """
        self.db_path = db_path
        self.connection = None
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
        
        try:
            self._connect()
            self._initialize_database()
            self.logger.info(f"DataStorage initialized with database: {db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _connect(self) -> None:
        """
        Establish connection to the SQLite database.
        
        Raises:
            sqlite3.Error: If connection fails
        """
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0
        )
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.execute('PRAGMA journal_mode = WAL')
        self.connection.execute('PRAGMA synchronous = NORMAL')
    
    def _initialize_database(self) -> None:
        """
        Create the required database tables if they don't exist.
        
        Creates:
            - channel_info table for channel metadata
            - channel_data table for sensor readings
        
        Raises:
            sqlite3.Error: If table creation fails
        """
        with self.lock:
            cursor = self.connection.cursor()
            
            # Create channel_info table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_info (
                    channel_id      INTEGER PRIMARY KEY,
                    channel_name    VARCHAR(255) NOT NULL
                )
            """)
            
            # Create channel_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_data (
                    channel_id      INTEGER NOT NULL,
                    timestamp       INTEGER NOT NULL,
                    temperature     NUMERIC(10, 5) NOT NULL,
                    humidity        NUMERIC(10, 5) NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
                    pressure        NUMERIC(10, 5) NOT NULL,
                    PRIMARY KEY (channel_id, timestamp),
                    FOREIGN KEY (channel_id) REFERENCES channel_info(channel_id) ON DELETE CASCADE
                )
            """)
            
            self.connection.commit()
            self.logger.debug("Database tables initialized successfully")
    
    def ensure_channel_exists(self, channel_id: int, channel_name: Optional[str] = None) -> None:
        """
        Ensure a channel exists in the channel_info table.
        
        Args:
            channel_id (int): The channel ID (typically chip_id from sensor)
            channel_name (str, optional): Human-readable channel name
                                         (default: "Channel {channel_id}")
        
        Raises:
            sqlite3.Error: If database operation fails
        """
        if channel_name is None:
            channel_name = f"Channel {channel_id}"
            
        with self.lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO channel_info (channel_id, channel_name)
                VALUES (?, ?)
            """, (channel_id, channel_name))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                self.logger.debug(f"Created new channel: {channel_id} - {channel_name}")
    
    def store_reading(self,
                     channel_id: int,
                     temperature: float,
                     humidity: float,
                     pressure: float,
                     timestamp: Optional[int] = None) -> bool:
        """
        Store a single sensor reading in the database.
        
        Args:
            channel_id (int): Channel identifier (chip_id from sensor)
            temperature (float): Temperature reading in Celsius
            humidity (float): Humidity reading in percentage (0-100)
            pressure (float): Pressure reading in hPa
            timestamp (int, optional): Unix timestamp (default: current time)
        
        Returns:
            bool: True if successful, False otherwise
        
        Raises:
            ValueError: If humidity is outside valid range (0-100)
            sqlite3.Error: If database operation fails
        """
        if not (0 <= humidity <= 100):
            raise ValueError(f"Humidity must be between 0 and 100, got {humidity}")
        
        if timestamp is None:
            timestamp = int(time.time())
        
        try:
            # Ensure channel exists
            self.ensure_channel_exists(channel_id)
            
            with self.lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO channel_data 
                    (channel_id, timestamp, temperature, humidity, pressure)
                    VALUES (?, ?, ?, ?, ?)
                """, (channel_id, timestamp, temperature, humidity, pressure))
                self.connection.commit()
                
                self.logger.debug(
                    f"Stored reading - Channel: {channel_id}, "
                    f"T: {temperature:.2f}°C, H: {humidity:.1f}%, "
                    f"P: {pressure:.2f} hPa, Time: {timestamp}"
                )
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store reading: {e}")
            return False
    
    def store_readings_batch(self, readings: List[Dict[str, Any]]) -> int:
        """
        Store multiple sensor readings in a single transaction.
        
        Args:
            readings (List[Dict]): List of reading dictionaries, each containing:
                - channel_id (int): Channel identifier
                - temperature (float): Temperature in Celsius
                - humidity (float): Humidity percentage (0-100)
                - pressure (float): Pressure in hPa
                - timestamp (int, optional): Unix timestamp
        
        Returns:
            int: Number of successfully stored readings
        
        Raises:
            ValueError: If any humidity value is outside valid range
            sqlite3.Error: If database operation fails
        """
        if not readings:
            return 0
        
        # Validate all readings first
        for reading in readings:
            humidity = reading.get('humidity', 0)
            if not (0 <= humidity <= 100):
                raise ValueError(f"Humidity must be between 0 and 100, got {humidity}")
        
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                # Ensure all channels exist
                unique_channels = set(reading['channel_id'] for reading in readings)
                for channel_id in unique_channels:
                    cursor.execute("""
                        INSERT OR IGNORE INTO channel_info (channel_id, channel_name)
                        VALUES (?, ?)
                    """, (channel_id, f"Channel {channel_id}"))
                
                # Prepare data for batch insert
                data_to_insert = []
                current_time = int(time.time())
                
                for reading in readings:
                    timestamp = reading.get('timestamp', current_time)
                    data_to_insert.append((
                        reading['channel_id'],
                        timestamp,
                        reading['temperature'],
                        reading['humidity'],
                        reading['pressure']
                    ))
                
                # Batch insert readings
                cursor.executemany("""
                    INSERT OR REPLACE INTO channel_data 
                    (channel_id, timestamp, temperature, humidity, pressure)
                    VALUES (?, ?, ?, ?, ?)
                """, data_to_insert)
                
                self.connection.commit()
                stored_count = len(data_to_insert)
                
                self.logger.info(f"Stored {stored_count} readings in batch")
                return stored_count
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store readings batch: {e}")
            return 0
    
    def get_latest_reading(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most recent reading for a specific channel.
        
        Args:
            channel_id (int): Channel identifier to query
        
        Returns:
            Dict or None: Dictionary containing the latest reading data,
                         or None if no data found
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT channel_id, timestamp, temperature, humidity, pressure
                    FROM channel_data
                    WHERE channel_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (channel_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'channel_id': row[0],
                        'timestamp': row[1],
                        'temperature': row[2],
                        'humidity': row[3],
                        'pressure': row[4]
                    }
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to retrieve latest reading: {e}")
            return None
    
    def get_readings_range(self,
                          channel_id: int,
                          start_time: int,
                          end_time: int,
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve readings for a channel within a time range.
        
        Args:
            channel_id (int): Channel identifier to query
            start_time (int): Start timestamp (inclusive)
            end_time (int): End timestamp (inclusive)
            limit (int, optional): Maximum number of records to return
        
        Returns:
            List[Dict]: List of reading dictionaries
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                query = """
                    SELECT channel_id, timestamp, temperature, humidity, pressure
                    FROM channel_data
                    WHERE channel_id = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp ASC
                """
                
                params = [channel_id, start_time, end_time]
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [
                    {
                        'channel_id': row[0],
                        'timestamp': row[1],
                        'temperature': row[2],
                        'humidity': row[3],
                        'pressure': row[4]
                    }
                    for row in rows
                ]
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to retrieve readings range: {e}")
            return []
    
    def close(self) -> None:
        """
        Close the database connection.
        
        This method should be called when the DataStorage instance
        is no longer needed to properly close the database connection.
        """
        if self.connection:
            try:
                with self.lock:
                    self.connection.close()
                    self.connection = None
                    self.logger.info("Database connection closed")
            except sqlite3.Error as e:
                self.logger.error(f"Error closing database connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close connection."""
        self.close()
