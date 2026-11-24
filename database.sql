CREATE TABLE channel_info (
    channel_id      INTEGER PRIMARY KEY,
    channel_name    VARCHAR(255) NOT NULL
);

CREATE TABLE channel_data (
    channel_id      INTEGER NOT NULL,
    timestamp       INTEGER NOT NULL,
    temperature     NUMERIC(10, 5) NOT NULL,
    humidity        NUMERIC(10, 5) NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
    pressure        NUMERIC(10, 5) NOT NULL,
    PRIMARY KEY (channel_id, timestamp),
    FOREIGN KEY (channel_id) REFERENCES channel_info(channel_id) ON DELETE CASCADE
);
