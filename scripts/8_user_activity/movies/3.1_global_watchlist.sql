DROP TABLE IF EXISTS global_user_activity_watchlist;

CREATE TABLE global_user_activity_watchlist AS
SELECT * FROM global_user_activity
WHERE source = 'watchlist';