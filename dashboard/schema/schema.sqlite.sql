-- Local development schema (SQLite, synthetic data only). Keep in sync with schema.mariadb.sql;
-- dashboard/tests/test_schema.py checks that table and column names match.

CREATE TABLE IF NOT EXISTS activity (
    id          INTEGER PRIMARY KEY,   -- Garmin activityId
    start_time  TEXT    NOT NULL,      -- local time, 'YYYY-MM-DD HH:MM:SS'
    type        TEXT    NOT NULL,      -- Garmin type key, e.g. running, strength_training, cycling
    duration_s  REAL,
    distance_m  REAL,
    avg_hr      REAL,
    max_hr      REAL,
    source      TEXT                   -- e.g. garmin_export, fit_drop
);
CREATE INDEX IF NOT EXISTS idx_activity_start ON activity (start_time);

-- One row per day from the input form. Rating scales are not yet defined (TBC), so integers are
-- unconstrained; nullable so a partly filled day is valid.
CREATE TABLE IF NOT EXISTS daily_entry (
    entry_date      TEXT PRIMARY KEY,  -- 'YYYY-MM-DD'
    knee_l          INTEGER,
    knee_r          INTEGER,
    quad_tightness  INTEGER,
    strength_done   INTEGER NOT NULL DEFAULT 0,  -- 0/1
    mobility_done   INTEGER NOT NULL DEFAULT 0,  -- 0/1
    energy          INTEGER,
    mood            INTEGER,
    weight_kg       REAL,
    gut_status      INTEGER,
    notes           TEXT
);

-- A strength day counts once, whichever source reports it. Both flags are kept so disagreements
-- stay visible. form_strength = 0 means "not ticked or no entry that day".
DROP VIEW IF EXISTS strength_day;
CREATE VIEW strength_day AS
SELECT day,
       MAX(garmin) AS garmin_strength,
       MAX(form)   AS form_strength
FROM (
    SELECT date(start_time) AS day, 1 AS garmin, 0 AS form
    FROM activity WHERE type = 'strength_training'
    UNION ALL
    SELECT entry_date AS day, 0 AS garmin, 1 AS form
    FROM daily_entry WHERE strength_done = 1
) AS s
GROUP BY day;
