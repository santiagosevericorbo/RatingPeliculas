CREATE OR REPLACE TABLE global_activity_unique AS
SELECT DISTINCT display_title as title_norm
FROM global_activity
WHERE display_title IS NOT NULL;