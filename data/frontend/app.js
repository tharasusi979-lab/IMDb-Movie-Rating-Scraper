
console.log("CineScope AI — JARVIS system initialized");

const API = window.location.origin;
const $ = (id) => document.getElementById(id);

let movies = [];
let searchQuery = "";
let sortMode = "rank";

async function getJSON(path) {
    const response = await fetch(`${API}${path}`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${path}`);
    }

    return response.json();
}

function setText(id, value) {
    const element = $(id);
    if (element) element.textContent = value ?? "—";
}

function getMovieList(data) {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.movies)) return data.movies;
    if (Array.isArray(data?.results)) return data.results;
    return [];
}

function getRating(movie) {
    return Number(movie.rating ?? movie.imdb_rating ?? 0);
}

function getYear(movie) {
    return Number(movie.release_year ?? movie.year ?? 0);
}

function getPoster(movie) {
    return (
        movie.poster_url ||
        movie.poster ||
        movie.poster_path ||
        movie.image_url ||
        movie.image ||
        ""
    );
}

function applyFilters() {
    let result = movies.filter(movie => {
        const text = [
            movie.title,
            movie.genre,
            movie.release_year,
            movie.year
        ].join(" ").toLowerCase();

        return text.includes(searchQuery);
    });

    if (sortMode === "rating") {
        result.sort((a, b) => getRating(b) - getRating(a));
    } else if (sortMode === "year") {
        result.sort((a, b) => getYear(b) - getYear(a));
    } else {
        result.sort(
            (a, b) =>
                Number(a.rank ?? 999999) -
                Number(b.rank ?? 999999)
        );
    }

    renderMovies(result);
}

async function loadDashboard() {
    setText("apiStatus", "CONNECTING TO CORE...");

    try {
        const [stats, movieData] = await Promise.all([
            getJSON("/api/stats"),
            getJSON("/api/movies")
        ]);

        movies = getMovieList(movieData);

        setText("apiStatus", "SYSTEM ONLINE");
        setText(
            "totalMovies",
            stats.total_movies ?? movieData.count ?? movies.length
        );

        const average = Number(stats.average_rating);

        setText(
            "avgRating",
            Number.isFinite(average) ? average.toFixed(2) : "—"
        );

        setText("totalScrapes", stats.total_scrapes ?? 0);
        setText("analyticsMovieCount", movies.length);

        const highest = [...movies].sort(
            (a, b) => getRating(b) - getRating(a)
        )[0];

        setText(
            "highestMovie",
            highest?.title || "No movies available"
        );

        setText(
            "highestRating",
            highest ? getRating(highest).toFixed(1) : "—"
        );

        setupComparison();
        renderChart();
        applyFilters();

    } catch (error) {
        console.error("CineScope API error:", error);
        setText("apiStatus", "API CONNECTION ERROR");

        const grid = $("movieGrid");

        if (grid) {
            grid.replaceChildren();

            const message = document.createElement("p");
            message.textContent =
                "Cannot connect to the API. Check that the backend is running.";

            grid.appendChild(message);
        }
    }
}

function renderMovies(list) {
    const grid = $("movieGrid");
    if (!grid) return;

    setText("movieCount", `${list.length} movies`);
    grid.replaceChildren();

    if (!list.length) {
        grid.textContent = "No matching movies found.";
        return;
    }

    list.forEach(movie => {
        const card = document.createElement("article");
        card.className = "movie-card";

        const posterBox = document.createElement("div");
        posterBox.className = "movie-poster";

        const posterURL = getPoster(movie);

        if (posterURL) {
            const image = document.createElement("img");

            image.src = posterURL;
            image.alt = `${movie.title || "Movie"} poster`;
            image.loading = "lazy";

            image.onerror = () => {
                image.remove();
                posterBox.textContent = "POSTER UNAVAILABLE";
                posterBox.classList.add("poster-missing");
            };

            posterBox.appendChild(image);
        } else {
            posterBox.textContent = "POSTER UNAVAILABLE";
            posterBox.classList.add("poster-missing");
        }

        const content = document.createElement("div");
        content.className = "movie-card-content";

        const title = document.createElement("h3");
        title.textContent = movie.title || "Untitled Movie";

        const details = document.createElement("p");
        details.className = "movie-details";
        details.textContent =
            `${getYear(movie) || "Year unknown"} • ` +
            `${movie.genre || "Genre unknown"}`;

        const rating = document.createElement("p");
        rating.className = "movie-rating";
        rating.textContent = `★ ${getRating(movie).toFixed(1)} / 10`;

        content.append(title, details, rating);

        const link = document.createElement("a");
        link.className = "movie-link";
        link.href = movie.imdb_url || "#";
        link.textContent = "View on IMDb ↗";
        link.target = "_blank";
        link.rel = "noopener noreferrer";

        if (!movie.imdb_url) {
            link.addEventListener("click", event => {
                event.preventDefault();
            });
        }

        content.appendChild(link);
        card.append(posterBox, content);
        grid.appendChild(card);
    });
}

/* JARVIS TOP 10 FULL-WIDTH RATING CHART */
function renderChart() {
    const chart = $("ratingChart");
    if (!chart) return;

    chart.replaceChildren();

    // Full-width chart container
    Object.assign(chart.style, {
        display: "flex",
        flexDirection: "column",
        width: "100%",
        maxWidth: "100%",
        minWidth: "0",
        boxSizing: "border-box",
        gap: "22px",
        overflow: "visible"
    });

    const topMovies = [...movies]
        .filter(movie => Number.isFinite(getRating(movie)))
        .sort((a, b) => getRating(b) - getRating(a))
        .slice(0, 10);

    if (!topMovies.length) {
        chart.textContent = "No rating data available.";
        return;
    }

    topMovies.forEach((movie, index) => {
        const rating = Math.max(
            0,
            Math.min(10, getRating(movie))
        );

        // One movie row
        const row = document.createElement("div");

        Object.assign(row.style, {
            display: "flex",
            flexDirection: "column",
            width: "100%",
            maxWidth: "100%",
            minWidth: "0",
            gap: "10px",
            boxSizing: "border-box"
        });

        // Movie name and rating
        const heading = document.createElement("div");

        Object.assign(heading.style, {
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: "12px",
            width: "100%",
            minWidth: "0",
            boxSizing: "border-box"
        });

        const name = document.createElement("span");
        name.textContent =
            `${String(index + 1).padStart(2, "0")}  ` +
            `${movie.title || "Untitled Movie"}`;

        Object.assign(name.style, {
            flex: "1 1 auto",
            minWidth: "0",
            color: "#e5faff",
            fontSize: "14px",
            lineHeight: "1.6",
            overflowWrap: "anywhere"
        });

        const value = document.createElement("span");
        value.textContent = `${rating.toFixed(1)} / 10`;

        Object.assign(value.style, {
            flex: "0 0 auto",
            color: "#00e5ff",
            fontSize: "14px",
            fontWeight: "700",
            whiteSpace: "nowrap",
            textShadow: "0 0 10px rgba(0,229,255,0.35)"
        });

        // Full-width rating track
        const track = document.createElement("div");

        Object.assign(track.style, {
            display: "block",
            position: "relative",
            width: "100%",
            maxWidth: "100%",
            minWidth: "0",
            height: "14px",
            overflow: "hidden",
            background: "rgba(0,229,255,0.10)",
            border: "1px solid rgba(0,229,255,0.25)",
            borderRadius: "5px",
            boxSizing: "border-box"
        });

        // Cyan glowing bar based on the actual rating
        const bar = document.createElement("div");

        Object.assign(bar.style, {
            display: "block",
            width: `${rating * 10}%`,
            maxWidth: "100%",
            height: "100%",
            background: "linear-gradient(90deg, #0879b8, #00e5ff)",
            borderRadius: "4px",
            boxShadow: "0 0 12px rgba(0,229,255,0.45)",
            transition: "width 0.7s ease"
        });

        track.appendChild(bar);
        heading.append(name, value);
        row.append(heading, track);
        chart.appendChild(row);
    });
}

function setupComparison() {
    ["compareMovie1", "compareMovie2"].forEach(id => {
        const select = $(id);
        if (!select) return;

        select.replaceChildren();

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select a movie";
        select.appendChild(placeholder);

        movies.forEach((movie, index) => {
            const option = document.createElement("option");

            option.value = String(movie.id ?? movie.rank ?? index);
            option.textContent = movie.title || "Untitled";

            select.appendChild(option);
        });
    });

    const button = $("compareButton");

    if (button) {
        button.onclick = () => {
            const firstSelect = $("compareMovie1");
            const secondSelect = $("compareMovie2");
            const output = $("comparisonResult");

            if (!firstSelect || !secondSelect || !output) return;

            const findSelected = value =>
                movies.find((movie, index) =>
                    String(movie.id ?? movie.rank ?? index) === value
                );

            const first = findSelected(firstSelect.value);
            const second = findSelected(secondSelect.value);

            if (!first || !second) {
                output.textContent = "Please select both movies.";
                return;
            }

            if (first === second) {
                output.textContent = "Choose two different movies.";
                return;
            }

            const a = getRating(first);
            const b = getRating(second);

            const winner = a === b
                ? "Both movies have the same rating."
                : `${a > b ? first.title : second.title} has the higher rating.`;

            output.textContent =
                `${first.title}: ${a.toFixed(1)}/10 | ` +
                `${second.title}: ${b.toFixed(1)}/10. ${winner}`;
        };
    }
}

// Search
const searchInput = $("searchInput");

if (searchInput) {
    searchInput.addEventListener("input", () => {
        searchQuery = searchInput.value.trim().toLowerCase();
        applyFilters();
    });
}

// Sorting
const sortSelect = $("sortSelect");

if (sortSelect) {
    sortSelect.addEventListener("change", () => {
        const value = sortSelect.value.toLowerCase();

        if (value.includes("rating")) {
            sortMode = "rating";
        } else if (value.includes("year")) {
            sortMode = "year";
        } else {
            sortMode = "rank";
        }

        applyFilters();
    });
}

// Start dashboard
loadDashboard();
