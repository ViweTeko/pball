-- schema.sql
-- SQLite3 script to create the Powerball draws database schema.

-- Enable foreign key enforcement.
-- This must be set for each connection to the database.
PRAGMA foreign_keys = ON;

-- Table: dates
-- Stores unique draw dates along with associated metadata for each draw event.
CREATE TABLE IF NOT EXISTS dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TEXT NOT NULL UNIQUE,          -- Date of the draw (YYYY-MM-DD format)
    is_powerball_plus INTEGER NOT NULL,      -- 0 for False (regular Powerball), 1 for True (Powerball Plus)
    draw_sequence_num INTEGER UNIQUE         -- A unique sequential number for each draw
);

-- Table: draws
-- Stores the actual numbers drawn for each Powerball event and links back to the 'dates' table.
CREATE TABLE IF NOT EXISTS draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER NOT NULL UNIQUE,         -- Foreign Key to dates.id (ensures one set of numbers per draw date)
    n1 INTEGER NOT NULL,              -- First main number (1-50, sorted ascending)
    n2 INTEGER NOT NULL,              -- Second main number (1-50, sorted ascending)
    n3 INTEGER NOT NULL,              -- Third main number (1-50, sorted ascending)
    n4 INTEGER NOT NULL,              -- Fourth main number (1-50, sorted ascending)
    n5 INTEGER NOT NULL,              -- Fifth main number (1-50, sorted ascending)
    powerball_num INTEGER NOT NULL,          -- Powerball number (1-20)
    FOREIGN KEY (date_id) REFERENCES dates(id)
);

-- Index: idx_main_numbers
-- Composite index on the five main number columns for efficient lookup of specific combinations.
CREATE INDEX IF NOT EXISTS idx_main_numbers
ON draws (n1, n2, n3, n4, n5);

-- Optional: Sample data insertion (for demonstration purposes only)
-- You would typically populate this using your Python script or by importing real data.

-- Insert sample dates
INSERT INTO dates (draw_date, is_powerball_plus, draw_sequence_num) VALUES ('2023-01-01', 0, 1001) ON CONFLICT(draw_date) DO NOTHING;
INSERT INTO dates (draw_date, is_powerball_plus, draw_sequence_num) VALUES ('2023-01-04', 1, 1002) ON CONFLICT(draw_date) DO NOTHING;
INSERT INTO dates (draw_date, is_powerball_plus, draw_sequence_num) VALUES ('2024-06-19', 0, 999999999) ON CONFLICT(draw_date) DO NOTHING; -- Your target date
INSERT INTO dates (draw_date, is_powerball_plus, draw_sequence_num) VALUES ('2025-06-18', 1, 999999998) ON CONFLICT(draw_date) DO NOTHING;

-- Insert sample draws, referencing the dates
-- Note: The date_id must match an existing id in the 'dates' table.
-- The ON CONFLICT(date_id) DO NOTHING handles cases where the draw for a date might already exist.
INSERT INTO draws (date_id, n1, n2, n3, n4, n5, powerball_num)
SELECT id, 1, 5, 10, 15, 20, 3
FROM dates WHERE draw_date = '2023-01-01'
ON CONFLICT(date_id) DO NOTHING;

INSERT INTO draws (date_id, n1, n2, n3, n4, n5, powerball_num)
SELECT id, 7, 14, 21, 28, 35, 7
FROM dates WHERE draw_date = '2023-01-04'
ON CONFLICT(date_id) DO NOTHING;

INSERT INTO draws (date_id, n1, n2, n3, n4, n5, powerball_num)
SELECT id, 2, 18, 35, 41, 46, 1
FROM dates WHERE draw_date = '2024-06-19'
ON CONFLICT(date_id) DO NOTHING;

INSERT INTO draws (date_id, n1, n2, n3, n4, n5, powerball_num)
SELECT id, 10, 20, 30, 40, 50, 15
FROM dates WHERE draw_date = '2025-06-18'
ON CONFLICT(date_id) DO NOTHING;