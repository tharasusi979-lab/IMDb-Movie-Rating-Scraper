
import csv
import gzip
import heapq
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from backend.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RATINGS_FILE = DATA_DIR / "title.ratings.tsv.gz"
BASICS_FILE = DATA_DIR / "title.basics.tsv.gz"

MIN_VOTES = 25000
MIN_RATING = 7.0
TOP_COUNT = 250
WEIGHT = 7.0
MINIMUM_VOTES_FOR_WEIGHTED_RATING = 7000


def scrape_imdb_top_250(headless=True):
    """Scrape live IMDb Top 250 movies using Selenium."""

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = None

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        driver.get("https://www.imdb.com/chart/top/")
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
            )
        )
        time.sleep(2)

        movies = []

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "li.ipc-metadata-list-summary-item",
        )

        for card in cards:
            try:
                link = card.find_element(
                    By.CSS_SELECTOR,
                    "a[href*='/title/tt']",
                )
                title = link.text.strip()
                href = link.get_attribute("href")

                if not title or not href:
                    continue

                imdb_id = href.split("/title/")[1].split("/")[0]

                text = card.text
                lines = [line.strip() for line in text.splitlines() if line.strip()]

                year = None
                rating = None
                rank = len(movies) + 1

                for line in lines:
                    if line.isdigit() and len(line) == 4:
                        year = int(line)

                    try:
                        value = float(line)
                        if 0 <= value <= 10:
                            rating = value
                    except ValueError:
                        pass

                try:
                    poster = card.find_element(By.CSS_SELECTOR, "img")
                    poster_url = poster.get_attribute("src")
                except Exception:
                    poster_url = None

                if rating is not None:
                    movies.append({
                        "imdb_id": imdb_id,
                        "title": title,
                        "release_year": year,
                        "rating": rating,
                        "rank": rank,
                        "genre": "",
                        "imdb_url": f"https://www.imdb.com/title/{imdb_id}/",
                        "poster_url": poster_url,
                    })

            except Exception as error:
                print(f"Skipping a movie card: {error}")
                continue

        if not movies:
            raise RuntimeError(
                "No movies were extracted. IMDb page structure may have changed."
            )

        with get_connection() as conn:
            for movie in movies:
                conn.execute(
                    """
                    INSERT INTO movies (
                        imdb_id, title, release_year, rating,
                        rank, genre, imdb_url, poster_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(imdb_id) DO UPDATE SET
                        title = excluded.title,
                        release_year = excluded.release_year,
                        rating = excluded.rating,
                        rank = excluded.rank,
                        imdb_url = excluded.imdb_url,
                        poster_url = excluded.poster_url,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        movie["imdb_id"],
                        movie["title"],
                        movie["release_year"],
                        movie["rating"],
                        movie["rank"],
                        movie["genre"],
                        movie["imdb_url"],
                        movie["poster_url"],
                    ),
                )

        export_path = DATA_DIR / "imdb_top_250.csv"
        columns = [
            "rank", "title", "release_year", "rating",
            "genre", "imdb_id", "imdb_url", "poster_url",
        ]

        with export_path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(movies)

        print(f"Success! Scraped {len(movies)} live IMDb movies.")
        print(f"CSV saved to: {export_path}")
        return len(movies)

    except Exception as error:
        print(f"IMDb scraping failed: {error}")
        raise

    finally:
        if driver is not None:
            driver.quit()


def scrape_imdb_from_dataset():
    """Build a Top 250 list from the downloaded IMDb datasets."""

    if not RATINGS_FILE.exists() or not BASICS_FILE.exists():
        raise FileNotFoundError("IMDb dataset files are missing in data/.")

    initialize_database()
    ratings = {}

    with gzip.open(RATINGS_FILE, "rt", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            votes = int(row["numVotes"])
            rating = float(row["averageRating"])
            if votes >= MIN_VOTES and rating >= MIN_RATING:
                ratings[row["tconst"]] = (rating, votes)

    candidates = []

    with gzip.open(BASICS_FILE, "rt", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            imdb_id = row["tconst"]

            if imdb_id not in ratings:
                continue
            if row["titleType"] != "movie" or row["isAdult"] != "0":
                continue

            title = row["primaryTitle"]
            if not title or title == r"\N":
                continue

            year_text = row["startYear"]
            year = int(year_text) if year_text.isdigit() else None
            rating, votes = ratings[imdb_id]

            weighted = (
                votes / (votes + MINIMUM_VOTES_FOR_WEIGHTED_RATING) * rating
                + MINIMUM_VOTES_FOR_WEIGHTED_RATING
                / (votes + MINIMUM_VOTES_FOR_WEIGHTED_RATING) * WEIGHT
            )

            genre = row.get("genres", "")
            if genre == r"\N":
                genre = ""

            candidates.append(
                (imdb_id, title, year, rating, weighted, genre)
            )

    top_movies = heapq.nlargest(
        TOP_COUNT, candidates, key=lambda movie: movie[4]
    )

    with get_connection() as conn:
        for rank, movie in enumerate(top_movies, start=1):
            imdb_id, title, year, rating, weighted, genre = movie
            conn.execute(
                """
                INSERT INTO movies (
                    imdb_id, title, release_year, rating,
                    rank, genre, imdb_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(imdb_id) DO UPDATE SET
                    title = excluded.title,
                    release_year = excluded.release_year,
                    rating = excluded.rating,
                    rank = excluded.rank,
                    genre = excluded.genre,
                    imdb_url = excluded.imdb_url,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    imdb_id, title, year, rating, rank, genre,
                    f"https://www.imdb.com/title/{imdb_id}/",
                ),
            )

    print(f"Dataset processing complete: {len(top_movies)} movies.")
    return len(top_movies)


# Keep the existing function name used by main.py.
scrape_imdb_top250 = scrape_imdb_top_250
