CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    equipment_type TEXT NOT NULL,
    image_path TEXT,
    location TEXT,
    area_type TEXT,
    severity TEXT,
    status TEXT DEFAULT 'unresolved' NOT NULL CHECK(status IN ('unresolved', 'resolved', 'investigating'))
);

-- creating indexes for faster querying if the table grows large
CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations (timestamp);
CREATE INDEX IF NOT EXISTS idx_violations_equipment_type ON violations (equipment_type);
CREATE INDEX IF NOT EXISTS idx_violations_location ON violations (location);
CREATE INDEX IF NOT EXISTS idx_violations_status ON violations (status);

-- Stats Table :
/*
CREATE TABLE IF NOT EXISTS equipment_stats (
    equipment_type TEXT PRIMARY KEY,
    violation_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP
);
*/

--user stuff

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0 NOT NULL, -- 0 for false, 1 for true
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
