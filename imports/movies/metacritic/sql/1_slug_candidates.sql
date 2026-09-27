    CREATE OR REPLACE TABLE metacritic_slug_candidates(
        imdb_id VARCHAR,
        title_norm VARCHAR,
        year INT,
        slug VARCHAR,
        confidence DOUBLE
    )