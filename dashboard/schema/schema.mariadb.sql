-- Production schema (MariaDB). Not executed by Claude; deployment is run manually.
-- Keep in sync with schema.sqlite.sql.

CREATE TABLE IF NOT EXISTS activity (
    id          BIGINT       NOT NULL PRIMARY KEY,   -- Garmin activityId
    start_time  DATETIME     NOT NULL,               -- local time
    type        VARCHAR(64)  NOT NULL,               -- Garmin type key
    duration_s  DOUBLE       NULL,
    distance_m  DOUBLE       NULL,
    avg_hr      DOUBLE       NULL,
    max_hr      DOUBLE       NULL,
    source      VARCHAR(32)  NULL,
    KEY idx_activity_start (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_entry (
    entry_date      DATE         NOT NULL PRIMARY KEY,
    knee_l          SMALLINT     NULL,
    knee_r          SMALLINT     NULL,
    quad_tightness  SMALLINT     NULL,
    strength_done   TINYINT(1)   NOT NULL DEFAULT 0,
    mobility_done   TINYINT(1)   NOT NULL DEFAULT 0,
    energy          SMALLINT     NULL,
    mood            SMALLINT     NULL,
    weight_kg       DECIMAL(5,2) NULL,
    gut_status      SMALLINT     NULL,
    notes           TEXT         NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE OR REPLACE VIEW strength_day AS
SELECT day,
       MAX(garmin) AS garmin_strength,
       MAX(form)   AS form_strength
FROM (
    SELECT DATE(start_time) AS day, 1 AS garmin, 0 AS form
    FROM activity WHERE type = 'strength_training'
    UNION ALL
    SELECT entry_date AS day, 0 AS garmin, 1 AS form
    FROM daily_entry WHERE strength_done = 1
) AS s
GROUP BY day;
