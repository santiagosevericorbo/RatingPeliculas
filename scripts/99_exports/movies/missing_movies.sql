COPY imdb_missing_movies
TO '../exports/imdb_missing_movies.csv'
WITH (HEADER, DELIMITER ',');