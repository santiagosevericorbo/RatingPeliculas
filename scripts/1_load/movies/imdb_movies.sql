-- =====================================
-- LOAD IMDB DATASETS
-- =====================================

CREATE OR REPLACE TABLE imdb_basics_raw AS
SELECT *
-- FROM read_csv_auto('../data/imdb/title.basics.tsv.gz', delim='\t');
FROM read_csv_auto('data/movies/imdb/title.basics.tsv.gz', delim='\t');
CREATE OR REPLACE TABLE imdb_ratings_raw AS
SELECT *
-- FROM read_csv_auto('../data/imdb/title.ratings.tsv.gz', delim='\t');
FROM read_csv_auto('data/movies/imdb/title.ratings.tsv.gz', delim='\t');