
import os
import time
import sqlite3
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "cinescope.db"

load_dotenv(BASE_DIR / ".env")
API_KEY = os.getenv("OMDB_API_KEY")

if not API_KEY:
    raise SystemExit(
        "OMDB_API_KEY missing. Check the .env file in the project folder."
    )

if not DB_PATH.exists():
    raise SystemExit(f"Database not found: {DB_PATH}")

updated = 0
missing = 0
failed = 0

with sqlite3.connect(DB_PATH) as conn:
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(movies)")
    }

    if not {"imdb_id", "poster_url"}.issubset(columns):
        raise SystemExit(
            "The movies table must contain imdb_id and poster_url columns."
        )

    movies = conn.execute(
        """
        SELECT imdb_id, title
        FROM movies
        WHERE poster_url IS NULL
           OR TRIM(poster_url) = ''
           OR poster_url = 'N/A'
        """
    ).fetchall()

    print(f"Movies needing posters: {len(movies)}")

    for imdb_id, title in movies:
        try:
            response = requests.get(
                "https://www.omdbapi.com/",
                params={"i": imdb_id, "apikey": API_KEY},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "True":
                poster = data.get("Poster")

                if poster and poster != "N/A":
                    conn.execute(
                        """
                        UPDATE movies
                        SET poster_url = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE imdb_id = ?
                        """,
                        (poster, imdb_id),
                    )
                    updated += 1
                    print(f"Poster saved: {title}")
                else:
                    missing += 1
                    print(f"No poster available: {title}")
            else:
                print(f"OMDb response for {title}: {data.get('Error')}")
                missing += 1

        except requests.RequestException as error:
            failed += 1
            print(f"Request failed for {title}: {error}")

        time.sleep(0.25)

print("\nPoster update finished.")
print(f"Posters saved: {updated}")
print(f"No poster found: {missing}")
print(f"Request failures: {failed}")
