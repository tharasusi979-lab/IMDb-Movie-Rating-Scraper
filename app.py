import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------
# CineScope AI — self-contained Streamlit movie discovery demo
# Requirements: streamlit, pandas, plotly
# Run: python -m streamlit run app.py
# ------------------------------------------------------------

st.set_page_config(
    page_title="CineScope AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

MOVIES = [
    {"title": "Interstellar", "year": 2014, "genre": "Sci-Fi", "rating": 8.7, "runtime": 169, "director": "Christopher Nolan", "language": "English", "overview": "A team travels beyond this galaxy to find a future for humanity.", "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "votes": 2300000},
    {"title": "Inception", "year": 2010, "genre": "Sci-Fi", "rating": 8.8, "runtime": 148, "director": "Christopher Nolan", "language": "English", "overview": "A skilled thief enters dreams to steal secrets and attempts the impossible.", "poster": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg", "votes": 2600000},
    {"title": "The Dark Knight", "year": 2008, "genre": "Action", "rating": 9.0, "runtime": 152, "director": "Christopher Nolan", "language": "English", "overview": "Batman faces a chaotic criminal who pushes Gotham into darkness.", "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "votes": 2900000},
    {"title": "Dune: Part Two", "year": 2024, "genre": "Sci-Fi", "rating": 8.5, "runtime": 166, "director": "Denis Villeneuve", "language": "English", "overview": "Paul Atreides joins the Fremen while seeking justice and a difficult destiny.", "poster": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg", "votes": 650000},
    {"title": "The Shawshank Redemption", "year": 1994, "genre": "Drama", "rating": 9.3, "runtime": 142, "director": "Frank Darabont", "language": "English", "overview": "Two prisoners build an enduring friendship through hope and hardship.", "poster": "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg", "votes": 3000000},
    {"title": "Parasite", "year": 2019, "genre": "Thriller", "rating": 8.5, "runtime": 132, "director": "Bong Joon-ho", "language": "Korean", "overview": "A struggling family becomes entangled with a wealthy household.", "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "votes": 1000000},
    {"title": "Everything Everywhere All at Once", "year": 2022, "genre": "Sci-Fi", "rating": 7.8, "runtime": 139, "director": "Daniel Kwan, Daniel Scheinert", "language": "English", "overview": "An exhausted laundromat owner discovers the multiverse and her own potential.", "poster": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg", "votes": 550000},
    {"title": "Spider-Man: Across the Spider-Verse", "year": 2023, "genre": "Animation", "rating": 8.6, "runtime": 140, "director": "Joaquim Dos Santos", "language": "English", "overview": "Miles Morales journeys across dimensions and meets other Spider-heroes.", "poster": "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5XjIGA8x.jpg", "votes": 400000},
    {"title": "Joker", "year": 2019, "genre": "Drama", "rating": 8.4, "runtime": 122, "director": "Todd Phillips", "language": "English", "overview": "A lonely comedian's life spirals into a disturbing transformation.", "poster": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg", "votes": 1500000},
    {"title": "Avengers: Endgame", "year": 2019, "genre": "Action", "rating": 8.4, "runtime": 181, "director": "Anthony Russo, Joe Russo", "language": "English", "overview": "The Avengers unite for one final mission to reverse a cosmic catastrophe.", "poster": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "votes": 1300000},
    {"title": "Vikram", "year": 2022, "genre": "Action", "rating": 8.3, "runtime": 175, "director": "Lokesh Kanagaraj", "language": "Tamil", "overview": "A covert operation uncovers a dangerous network of crime and corruption.", "poster": "https://image.tmdb.org/t/p/w500/7B2V2f6a5h7G6f4f3k7x7G8J6fT.jpg", "votes": 75000},
    {"title": "Jai Bhim", "year": 2021, "genre": "Drama", "rating": 8.8, "runtime": 164, "director": "T. J. Gnanavel", "language": "Tamil", "overview": "A lawyer fights for justice for a tribal couple facing systemic injustice.", "poster": "https://image.tmdb.org/t/p/w500/3J8v1X2e2wK3m4f5k6n7o8p9q0r.jpg", "votes": 60000},
    {"title": "96", "year": 2018, "genre": "Romance", "rating": 8.5, "runtime": 158, "director": "C. Prem Kumar", "language": "Tamil", "overview": "Two former classmates reconnect and revisit memories from their school days.", "poster": "https://image.tmdb.org/t/p/w500/placeholder96.jpg", "votes": 45000},
    {"title": "Kaithi", "year": 2019, "genre": "Action", "rating": 8.5, "runtime": 145, "director": "Lokesh Kanagaraj", "language": "Tamil", "overview": "An ex-prisoner races through one night to help police and see his daughter.", "poster": "https://image.tmdb.org/t/p/w500/placeholderkaithi.jpg", "votes": 50000},
    {"title": "The Batman", "year": 2022, "genre": "Crime", "rating": 7.8, "runtime": 176, "director": "Matt Reeves", "language": "English", "overview": "A young Batman investigates corruption and a series of cryptic murders.", "poster": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg", "votes": 850000},
    {"title": "Whiplash", "year": 2014, "genre": "Drama", "rating": 8.5, "runtime": 107, "director": "Damien Chazelle", "language": "English", "overview": "A young drummer is pushed to extremes by a demanding music instructor.", "poster": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeeda4o.jpg", "votes": 1000000},
    {"title": "Coco", "year": 2017, "genre": "Animation", "rating": 8.4, "runtime": 105, "director": "Lee Unkrich", "language": "English", "overview": "A boy who dreams of music visits the Land of the Dead to uncover family history.", "poster": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg", "votes": 600000},
    {"title": "The Grand Budapest Hotel", "year": 2014, "genre": "Comedy", "rating": 8.1, "runtime": 99, "director": "Wes Anderson", "language": "English", "overview": "A hotel concierge and lobby boy become involved in a curious mystery.", "poster": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg", "votes": 900000},
    {"title": "Get Out", "year": 2017, "genre": "Horror", "rating": 7.8, "runtime": 104, "director": "Jordan Peele", "language": "English", "overview": "A weekend visit reveals unsettling secrets beneath a friendly facade.", "poster": "https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg", "votes": 700000},
    {"title": "Spirited Away", "year": 2001, "genre": "Animation", "rating": 8.6, "runtime": 125, "director": "Hayao Miyazaki", "language": "Japanese", "overview": "A young girl enters a spirit world to rescue her transformed parents.", "poster": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg", "votes": 850000},
    {"title": "La La Land", "year": 2016, "genre": "Romance", "rating": 8.0, "runtime": 128, "director": "Damien Chazelle", "language": "English", "overview": "A musician and an aspiring actor pursue their dreams in Los Angeles.", "poster": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg", "votes": 700000},
]

df = pd.DataFrame(MOVIES)
GENRES = ["All genres"] + sorted(df["genre"].unique().tolist())

# ----------------------------- Styling -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    :root { --bg:#090b10; --surface:#11151d; --surface2:#171d27; --border:#252d3a; --text:#f2f5fa; --muted:#96a0b2; --cyan:#68e1f5; --violet:#a78bfa; }
    html, body, [class*="css"] { font-family:'Inter',sans-serif; }
    .stApp { background:radial-gradient(ellipse at 12% 0%, #17232e 0%, transparent 38%), var(--bg); color:var(--text); }
    h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.5px; color:var(--text); }
    p, label, li { color:var(--muted); }
    section[data-testid="stSidebar"] { background:#0c0f15; border-right:1px solid var(--border); }
    section[data-testid="stSidebar"] .stRadio label { color:#d9dfeb; }
    div[data-testid="stMetric"] { background:linear-gradient(145deg,#151b25,#10141c); border:1px solid var(--border); border-radius:15px; padding:18px; }
    div[data-testid="stMetricLabel"] { color:var(--muted); }
    div[data-testid="stMetricValue"] { font-family:'Space Grotesk',sans-serif; color:var(--text); }
    .hero { padding:26px 28px; border:1px solid #283544; border-radius:20px; background:linear-gradient(115deg,rgba(24,39,51,.96),rgba(15,18,28,.96)); margin-bottom:22px; }
    .eyebrow { color:var(--cyan); text-transform:uppercase; letter-spacing:2.4px; font-size:11px; font-weight:700; }
    .hero-title { font-family:'Space Grotesk',sans-serif; font-size:34px; line-height:1.15; font-weight:700; color:#f5f7fb; margin:9px 0; }
    .hero-copy { color:#a9b4c5; font-size:14px; max-width:760px; line-height:1.7; }
    .movie-card { background:linear-gradient(180deg,#151a23,#10131a); border:1px solid #27303d; border-radius:15px; padding:10px; margin-bottom:8px; transition:transform .18s ease,border-color .18s ease; }
    .movie-card:hover { transform:translateY(-3px); border-color:#4c8795; }
    .movie-title { color:#f3f5fa; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:15px; margin-top:9px; line-height:1.35; }
    .movie-meta { color:#929bad; font-size:12px; margin-top:4px; }
    .rating { color:#f6c76b; font-size:13px; font-weight:700; margin-top:8px; }
    .pill { display:inline-block; padding:4px 8px; background:#1a2730; border:1px solid #2b4652; border-radius:30px; color:#8de5f4; font-size:10px; letter-spacing:.4px; }
    .section-head { display:flex; align-items:center; justify-content:space-between; margin:12px 0 16px; }
    .section-head h2 { margin:0; }
    .small-muted { color:#929bad; font-size:12px; }
    .stButton > button { border-radius:9px; border:1px solid #34414f; background:#151b25; color:#eaf0f7; font-weight:600; }
    .stButton > button:hover { border-color:var(--cyan); color:var(--cyan); }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] { background:#11151d !important; color:#f2f5fa !important; border-color:#2a3340 !important; border-radius:9px !important; }
    hr { border-color:var(--border); }
    #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Helpers -----------------------------
def movie_card(movie):
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
    st.image(movie["poster"], use_container_width=True)
    st.markdown(f'<div class="movie-title">{movie["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="movie-meta">{movie["year"]} · {movie["genre"]} · {movie["runtime"]} min</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rating">★ {movie["rating"]:.1f} <span style="color:#788397;font-weight:400;">/ 10</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Movie details", key=f"details_{movie['title']}", use_container_width=True):
        st.session_state["selected_movie"] = movie["title"]

def render_grid(movies, columns=4):
    if not movies:
      .compare-controls {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 24px 0;
    flex-wrap: wrap;
}

.compare-controls select {
    flex: 1;
    min-width: 200px;
    padding: 14px;
    border: 1px solid #334155;
    border-radius: 12px;
    background: #111827;
    color: #f8fafc;
    font: inherit;
}

.versus {
    color: #67e8f9;
    font-family: Orbitron, sans-serif;
    font-weight: 700;
}

.comparison-result {
    margin-top: 24px;
    overflow-x: auto;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
}

.comparison-table th,
.comparison-table td {
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #334155;
}

.comparison-table th {
    color: #67e8f9;
    background: #172554;
}

.comparison-table tr:hover td {
    background: rgba(103, 232, 249, 0.06);
}  
function populateComparison() {
    const first = document.getElementById("compareMovie1");
    const second = document.getElementById("compareMovie2");

    if (!first || !second) return;

    [first, second].forEach((select, index) => {
        select.replaceChildren(
            new Option(
                index === 0 ? "Select first movie" : "Select second movie",
                ""
            )
        );

        movies.forEach(movie => {
            select.add(new Option(movie.title, movie.id));
        });
    });
}

document.getElementById("compareButton")?.addEventListener("click", () => {
    const id1 = document.getElementById("compareMovie1").value;
    const id2 = document.getElementById("compareMovie2").value;
    const output = document.getElementById("comparisonResult");

    if (!id1 || !id2) {
        output.textContent = "Please select both movies.";
        return;
    }

    if (id1 === id2) {
        output.textContent = "Please select two different movies.";
        return;
    }

    const a = movies.find(m => String(m.id) === id1);
    const b = movies.find(m => String(m.id) === id2);

    if (!a || !b) {
        output.textContent = "Movie data not found.";
        return;
    }

    output.replaceChildren();

    const heading = document.createElement("h3");
    heading.textContent =
        Number(a.rating) === Number(b.rating)
            ? "Both movies have the same rating!"
            : `${Number(a.rating) > Number(b.rating) ? a.title : b.title} has the higher rating!`;

    output.appendChild(heading);

    const table = document.createElement("table");
    table.className = "comparison-table";

    const rows = [
        ["Feature", a.title, b.title],
        ["IMDb Rating", a.rating ?? "N/A", b.rating ?? "N/A"],
        ["Release Year", a.release_year ?? "N/A", b.release_year ?? "N/A"],
        ["Genre", a.genre || "N/A", b.genre || "N/A"],
        ["IMDb Rank", a.rank ?? "N/A", b.rank ?? "N/A"]
    ];

    rows.forEach((row, i) => {
        const tr = document.createElement("tr");

        row.forEach(value => {
            const cell = document.createElement(i === 0 ? "th" : "td");
            cell.textContent = value;
            tr.appendChild(cell);
        });

        table.appendChild(tr);
    });

    output.appendChild(table);
});

function updateAnalytics() {
    const output = document.getElementById("ratingChart");

    if (!Array.isArray(movies) || movies.length === 0) {
        output.textContent = "No movie data available.";
        return;
    }

    const sorted = [...movies].sort(
        (a, b) => (Number(b.rating) || 0) - (Number(a.rating) || 0)
    );

    const highest = sorted[0];

    document.getElementById("highestMovie").textContent =
        highest.title || "Unknown";

    document.getElementById("highestRating").textContent =
        Number(highest.rating || 0).toFixed(1);

    document.getElementById("analyticsMovieCount").textContent =
        movies.length;

    output.replaceChildren();

    sorted.slice(0, 10).forEach((movie, index) => {
        const item = document.createElement("div");
        item.style.margin = "16px 0";

        const label = document.createElement("div");
        label.style.display = "flex";
        label.style.justifyContent = "space-between";
        label.style.gap = "12px";
        label.style.marginBottom = "6px";

        const name = document.createElement("span");
        name.textContent = `${index + 1}. ${movie.title}`;

        const rating = document.createElement("strong");
        rating.textContent = `${Number(movie.rating || 0).toFixed(1)} / 10`;

        label.append(name, rating);

        const bar = document.createElement("div");
        bar.style.height = "8px";
        bar.style.background = "#263449";
        bar.style.borderRadius = "8px";
        bar.style.overflow = "hidden";

        const fill = document.createElement("div");
        fill.style.width = `${Math.min(100, Math.max(0, Number(movie.rating) || 0) * 10)}%`;
        fill.style.height = "100%";
        fill.style.background = "linear-gradient(90deg, #22d3ee, #818cf8)";
        fill.style.borderRadius = "8px";

        bar.appendChild(fill);
        item.append(label, bar);
        output.appendChild(item);
    });
}
