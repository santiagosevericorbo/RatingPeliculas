-- MovieLens 32M: retain compact tables needed for rating analysis.
CREATE OR REPLACE TABLE movielens_links_raw AS
SELECT *
FROM read_csv_auto('data/movies/movielens/ml-32m/links.csv');

CREATE OR REPLACE TABLE movielens_ratings_raw AS
SELECT *
FROM read_csv_auto('data/movies/movielens/ml-32m/ratings.csv');

CREATE OR REPLACE TABLE movielens_tags_raw AS
SELECT *
FROM read_csv_auto('data/movies/movielens/ml-32m/tags.csv');

CREATE OR REPLACE TABLE movielens_movies_raw AS
SELECT *
FROM read_csv_auto('data/movies/movielens/ml-32m/movies.csv');
