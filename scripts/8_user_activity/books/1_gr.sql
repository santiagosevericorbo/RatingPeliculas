DROP TABLE IF EXISTS goodreads_user_activity;

CREATE TABLE goodreads_user_activity AS

SELECT 
    *,
    title_norm || ' (' || year || ')' AS display_title
FROM goodreads_activity_clean;