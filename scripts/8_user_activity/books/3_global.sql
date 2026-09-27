DROP TABLE IF EXISTS global_activity;

CREATE TABLE global_activity AS
SELECT
    *
FROM goodreads_user_activity;