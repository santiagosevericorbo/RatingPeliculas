CREATE OR REPLACE TABLE global_activity_readlist_unique AS
SELECT DISTINCT display_title as title_norm
FROM global_activity_readlist
WHERE display_title IS NOT NULL;