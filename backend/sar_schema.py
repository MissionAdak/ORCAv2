import sqlite3

conn = sqlite3.connect("orca_cache.db")

conn.executescript("""
CREATE TABLE IF NOT EXISTS sar_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL DEFAULT 'active',
    last_known_latitude REAL NOT NULL,
    last_known_longitude REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sar_location_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES sar_incidents(id)
);

CREATE TABLE IF NOT EXISTS sar_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    predicted_latitude REAL NOT NULL,
    predicted_longitude REAL NOT NULL,
    uncertainty_km REAL,
    predicted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES sar_incidents(id)
);

CREATE TABLE IF NOT EXISTS sar_search_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    geometry TEXT NOT NULL,
    probability REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES sar_incidents(id)
);

CREATE TABLE IF NOT EXISTS sar_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    evidence_type TEXT,
    description TEXT,
    source TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES sar_incidents(id)
);
""")

conn.commit()
conn.close()

print("SAR schema created successfully")
