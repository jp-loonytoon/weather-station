#!/bin/bash

DB_NAME="datalogger.db"

# Check if the database file already exists
if [ -f "$DB_NAME" ]; then
    echo "Database '$DB_NAME' already exists."
    echo "Delete it before re-running the script."
    exit 1
fi

sqlite3 $DB_NAME < database.sql

sqlite3 $DB_NAME "INSERT INTO channel_info (channel_id, channel_name) VALUES (1, 'Temperature');"
sqlite3 $DB_NAME "INSERT INTO channel_info (channel_id, channel_name) VALUES (2, 'Humidity');"
sqlite3 $DB_NAME "INSERT INTO channel_info (channel_id, channel_name) VALUES (3, 'Pressure');"

echo "Database '$DB_NAME' created and initialized successfully."