DROP TABLE IF EXISTS global_activity_readlist;

CREATE TABLE global_activity_readlist AS
SELECT 
    *
FROM goodreads_user_activity
WHERE activity = 'to-read';