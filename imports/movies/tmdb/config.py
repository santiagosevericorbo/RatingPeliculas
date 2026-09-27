import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if TMDB_API_KEY is None:
    raise ValueError("TMDB_API_KEY not found")
