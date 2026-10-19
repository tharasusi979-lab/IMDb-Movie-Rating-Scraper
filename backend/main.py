
from contextlib import asynccontextmanager
from pathlib import Path
from io import BytesIO, StringIO
import csv

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from backend.database import initialize_database, get_connection
from backend.scraper import scrape_imdb_top_250


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "data" / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="CineScope AI",
    description="IMDb Movie Scraper and Movie Intelligence Dashboard",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend assets:
# /static/app.js and /static/style.css
app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


def fetch_movies():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, imdb_id, title, release_year,
                   rating, rank, genre, imdb_url, poster_url
            FROM movies
            ORDER BY rank ASC, title ASC
        """).fetchall()

    return [dict(row) for row in rows]


@app.get("/")
def home():
    index_file = FRONTEND_DIR / "index.html"

    if not index_file.is_file():
        raise HTTPException(
            status_code=404,
            detail="Frontend index.html not found",
        )

    return FileResponse(index_file)


@app.get("/api/health")
def health():
    with get_connection() as connection:
        connection.execute("SELECT 1").fetchone()

    return {
        "status": "healthy",
        "backend": "FastAPI",
        "database": "connected",
        "scraper": "integrated",
    }


@app.get("/api/stats")
def get_stats():
    with get_connection() as connection:
        total_movies = connection.execute(
            "SELECT COUNT(*) FROM movies"
        ).fetchone()[0]

        average_rating = connection.execute(
            "SELECT AVG(rating) FROM movies"
        ).fetchone()[0]

        total_scrapes = connection.execute(
            "SELECT COUNT(*) FROM scrape_history"
        ).fetchone()[0]

    return {
        "total_movies": total_movies,
        "average_rating": round(average_rating, 2)
        if average_rating is not None else 0,
        "total_scrapes": total_scrapes,
    }


@app.get("/api/movies")
def get_movies():
    movies = fetch_movies()
    return {
        "count": len(movies),
        "movies": movies,
    }


@app.get("/api/analytics")
def get_analytics():
    movies = fetch_movies()

    rated_movies = [
        movie for movie in movies
        if movie.get("rating") is not None
    ]

    top_movies = sorted(
        rated_movies,
        key=lambda movie: float(movie["rating"]),
        reverse=True,
    )[:10]

    year_counts = {}
    genre_counts = {}

    for movie in movies:
        year = movie.get("release_year")

        if year:
            year = str(year)
            year_counts[year] = year_counts.get(year, 0) + 1

        for genre in (movie.get("genre") or "").split(","):
            genre = genre.strip()

            if genre and genre.lower() != "unknown":
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return {
        "top_movies": top_movies,
        "highest_movie": top_movies[0] if top_movies else None,
        "year_distribution": [
            {"year": year, "count": count}
            for year, count in sorted(year_counts.items())
        ],
        "genre_distribution": sorted(
            [
                {"genre": genre, "count": count}
                for genre, count in genre_counts.items()
            ],
            key=lambda item: item["count"],
            reverse=True,
        ),
    }


@app.post("/api/scrape")
async def run_scraper():
    try:
        result = await run_in_threadpool(scrape_imdb_top_250)

        return {
            "message": "Scraping finished",
            "result": result,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(error)}",
        ) from error


@app.get("/api/export/csv")
def export_csv():
    movies = fetch_movies()

    if not movies:
        raise HTTPException(
            status_code=404,
            detail="No movie data available to export",
        )

    output = StringIO()

    columns = [
        "rank", "title", "release_year", "rating",
        "genre", "imdb_id", "imdb_url", "poster_url",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=columns,
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(movies)

    content = output.getvalue().encode("utf-8-sig")

    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
                'attachment; filename="IMDb_Top_250_Movies.csv"'
        },
    )


@app.get("/api/export/excel")
def export_excel():
    movies = fetch_movies()

    if not movies:
        raise HTTPException(
            status_code=404,
            detail="No movie data available to export",
        )

    columns = [
        "rank", "title", "release_year", "rating",
        "genre", "imdb_id", "imdb_url", "poster_url",
    ]

    dataframe = pd.DataFrame(movies).reindex(columns=columns)
    output = BytesIO()

    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            dataframe.to_excel(
                writer,
                index=False,
                sheet_name="IMDb Top 250",
            )

    except ImportError as error:
        raise HTTPException(
            status_code=500,
            detail="Install Excel support: pip install openpyxl",
        ) from error

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="IMDb_Top_250_Movies.xlsx"'
        },
    )
