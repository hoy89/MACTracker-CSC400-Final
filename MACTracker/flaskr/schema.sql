-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS macAddressPool;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS nodes;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE macAddressPool (
  macAddress TEXT PRIMARY KEY,
  deviceType TEXT DEFAULT 'Unknown',
  areaName TEXT DEFAULT 'Default',
  nodeName TEXT NOT NULL,
  lastDetectTime TEXT,
  lastDetectDate TEXT,
  previousAliveDate TEXT,
  lastAliveTime TEXT,
  timeSpentLive INTEGER NOT NULL,
  live BOOLEAN NOT NULL,
  detectionCount INTEGER NOT NULL,
  previousArea TEXT,
  previousNode TEXT,
  detectedNetwork TEXT,
  FOREIGN KEY (areaName) REFERENCES areas (areaName)
);

CREATE TABLE areas (
	areaName TEXT PRIMARY KEY,
	metricsSelection INTEGER,
	detectionCounter INTEGER,
	averageTimeSpent INTEGER
);

CREATE TABLE nodes (
	nodeIP TEXT PRIMARY KEY,
  nodeName TEXT NOT NULL,
	areaName TEXT DEFAULT 'Default',
	FOREIGN KEY (areaName) REFERENCES areas (areaName)
);
