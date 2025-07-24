CREATE TABLE channel_info (
    channel_id      INTEGER PRIMARY KEY,
    channel_name    VARCHAR(255) NOT NULL
);

CREATE TABLE channel_data (
    channel_id      INTEGER NOT NULL,
    timestamp       INTEGER,
    value           NUMERIC(10, 5),
    PRIMARY KEY (channel_id, timestamp)
    FOREIGN KEY (channel_id) REFERENCES channel_info(channel_id)
);
