import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CineMind",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top right, rgba(255,107,0,0.12), transparent 30%),
        radial-gradient(circle at bottom left, rgba(255,107,0,0.06), transparent 25%),
        #080808;
    color: white;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

section[data-testid="stSidebar"] {
    background: #101010;
    border-right: 1px solid #242424;
}

.hero {
    padding: 55px 20px 45px 20px;
    border-radius: 24px;
    background:
        linear-gradient(
            90deg,
            rgba(8,8,8,0.98),
            rgba(8,8,8,0.78),
            rgba(8,8,8,0.35)
        );
    border: 1px solid #242424;
    margin-bottom: 35px;
}

.hero-title {
    font-size: 54px;
    font-weight: 900;
    line-height: 1.05;
    margin-bottom: 12px;
}

.hero-title span {
    color: #ff6b00;
}

.hero-text {
    color: #9ca3af;
    font-size: 18px;
    max-width: 650px;
}

.section-title {
    font-size: 27px;
    font-weight: 800;
    margin-top: 35px;
    margin-bottom: 18px;
}

.movie-card {
    background: #121212;
    border: 1px solid #252525;
    border-radius: 15px;
    padding: 10px;
    transition: 0.2s;
}

.movie-card:hover {
    border-color: #ff6b00;
    transform: translateY(-3px);
}

.movie-title {
    color: white;
    font-weight: 700;
    font-size: 15px;
    margin-top: 10px;
    min-height: 38px;
}

.movie-meta {
    color: #888;
    font-size: 13px;
}

.rating {
    color: #ffb000;
    font-weight: 700;
}

.detail-box {
    background: #121212;
    border: 1px solid #282828;
    border-radius: 20px;
    padding: 28px;
}

.search-box {
    margin-bottom: 25px;
}

div.stButton > button {
    background: #ff6b00;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 700;
}

div.stButton > button:hover {
    background: #ff8533;
    color: white;
}

div[data-baseweb="select"] > div {
    background-color: #151515;
    border-color: #292929;
}

div[data-baseweb="input"] > div {
    background-color: #151515;
    border-color: #292929;
}

</style>
""", unsafe_allow_html=True)


def tmdb_request(endpoint, params=None):

    if not TMDB_API_KEY:
        return None

    params = params or {}
    params["api_key"] = TMDB_API_KEY

    try:
        response = requests.get(
            f"{TMDB_BASE_URL}{endpoint}",
            params=params,
            timeout=20
        )

        if response.status_code == 200:
            return response.json()

    except requests.RequestException:
        pass

    return None


@st.cache_data(ttl=600)
def get_movies(category):

    endpoints = {
        "Popular": "/movie/popular",
        "Top Rated": "/movie/top_rated",
        "Now Playing": "/movie/now_playing",
        "Upcoming": "/movie/upcoming"
    }

    data = tmdb_request(
        endpoints[category],
        {"language": "en-US", "page": 1}
    )

    if data:
        return data.get("results", [])

    return []


@st.cache_data(ttl=600)
def search_movies(query):

    data = tmdb_request(
        "/search/movie",
        {
            "query": query,
            "language": "en-US",
            "page": 1,
            "include_adult": False
        }
    )

    if data:
        return data.get("results", [])

    return []


@st.cache_data(ttl=600)
def get_movie(movie_id):

    return tmdb_request(
        f"/movie/{movie_id}",
        {"language": "en-US"}
    )


def poster_url(path):

    if path:
        return f"{TMDB_IMAGE_URL}{path}"

    return None


def movie_grid(movies, key_prefix):

    if not movies:
        st.info("No movies found.")
        return

    cols = st.columns(6)

    for i, movie in enumerate(movies):

        with cols[i % 6]:

            st.markdown(
                '<div class="movie-card">',
                unsafe_allow_html=True
            )

            poster = poster_url(movie.get("poster_path"))

            if poster:
                st.image(
                    poster,
                    use_container_width=True
                )
            else:
                st.markdown(
                    "<div style='height:260px;text-align:center;padding-top:100px;'>"
                    "🎬<br>No Poster"
                    "</div>",
                    unsafe_allow_html=True
                )

            title = movie.get("title", "Unknown")

            release = movie.get("release_date", "")
            year = release[:4] if release else "N/A"

            rating = movie.get("vote_average", 0)

            st.markdown(
                f"""
                <div class="movie-title">{title}</div>
                <div class="movie-meta">
                    {year}
                    &nbsp; • &nbsp;
                    <span class="rating">★ {rating:.1f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "View",
                key=f"{key_prefix}_{movie.get('id')}_{i}"
            ):

                st.session_state.selected_movie = movie.get("id")
                st.session_state.page = "details"
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


def get_ml_recommendations(title, number):

    try:

        response = requests.get(
            f"{API_BASE}/recommend/{title}",
            params={"n": number},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

    except requests.RequestException:
        return None

    return None


if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None


with st.sidebar:

    st.markdown("## 🎬 CineMind")

    st.markdown(
        "<p style='color:#777;'>Your intelligent movie discovery system.</p>",
        unsafe_allow_html=True
    )

    st.divider()

    if st.button("🏠 Home", use_container_width=True):

        st.session_state.page = "home"
        st.rerun()

    if st.button("🔥 Popular", use_container_width=True):

        st.session_state.page = "category"
        st.session_state.category = "Popular"
        st.rerun()

    if st.button("⭐ Top Rated", use_container_width=True):

        st.session_state.page = "category"
        st.session_state.category = "Top Rated"
        st.rerun()

    if st.button("🆕 Now Playing", use_container_width=True):

        st.session_state.page = "category"
        st.session_state.category = "Now Playing"
        st.rerun()

    if st.button("🚀 Upcoming", use_container_width=True):

        st.session_state.page = "category"
        st.session_state.category = "Upcoming"
        st.rerun()

    st.divider()

    st.caption("ML Engine")
    st.caption("TF-IDF + Cosine Similarity")


if st.session_state.page == "home":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                Discover your next<br>
                <span>favorite movie.</span>
            </div>
            <div class="hero-text">
                Search thousands of movies, explore what's popular,
                and get intelligent recommendations powered by
                TF-IDF and cosine similarity.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    search = st.text_input(
        "Search Movies",
        placeholder="Search for Batman, Avengers, Interstellar..."
    )

    if search.strip():

        results = search_movies(search.strip())

        st.markdown(
            f'<div class="section-title">Search Results</div>',
            unsafe_allow_html=True
        )

        movie_grid(results[:18], "search")

    else:

        st.markdown(
            '<div class="section-title">🔥 Popular Movies</div>',
            unsafe_allow_html=True
        )

        movie_grid(
            get_movies("Popular")[:12],
            "popular"
        )

        st.markdown(
            '<div class="section-title">⭐ Top Rated</div>',
            unsafe_allow_html=True
        )

        movie_grid(
            get_movies("Top Rated")[:12],
            "rated"
        )


elif st.session_state.page == "category":

    category = st.session_state.category

    st.markdown(
        f'<div class="section-title">{category} Movies</div>',
        unsafe_allow_html=True
    )

    movies = get_movies(category)

    movie_grid(
        movies[:24],
        category.lower().replace(" ", "_")
    )


elif st.session_state.page == "details":

    movie_id = st.session_state.selected_movie

    if st.button("← Back"):

        st.session_state.page = "home"
        st.rerun()

    movie = get_movie(movie_id)

    if movie:

        left, right = st.columns([1, 2.2], gap="large")

        with left:

            poster = poster_url(movie.get("poster_path"))

            if poster:
                st.image(
                    poster,
                    use_container_width=True
                )

        with right:

            st.markdown(
                '<div class="detail-box">',
                unsafe_allow_html=True
            )

            st.markdown(
                f"# {movie.get('title', 'Unknown')}"
            )

            release = movie.get("release_date", "N/A")
            rating = movie.get("vote_average", 0)

            st.markdown(
                f"""
                **Release:** {release}

                **Rating:** ⭐ {rating:.1f}/10

                **Runtime:** {movie.get("runtime", "N/A")} minutes
                """
            )

            genres = movie.get("genres", [])

            if genres:

                genre_names = " • ".join(
                    genre["name"]
                    for genre in genres
                )

                st.markdown(
                    f"**Genres:** {genre_names}"
                )

            st.divider()

            st.markdown("### Overview")

            st.write(
                movie.get(
                    "overview",
                    "No overview available."
                )
            )

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        st.markdown(
            '<div class="section-title">🤖 AI Recommendations</div>',
            unsafe_allow_html=True
        )

        title = movie.get("title")

        recommendation_count = st.slider(
            "Number of similar movies",
            5,
            20,
            10
        )

        if st.button("✨ Find Similar Movies"):

            with st.spinner(
                "Analyzing movie similarity..."
            ):

                result = get_ml_recommendations(
                    title,
                    recommendation_count
                )

            if result:

                recommendations = result.get(
                    "recommendations",
                    []
                )

                if "Movie Not Found" not in recommendations:

                    st.markdown(
                        f"### Movies similar to **{title}**"
                    )

                    recommendation_movies = []

                    for recommendation in recommendations:

                        found = search_movies(
                            recommendation
                        )

                        if found:
                            recommendation_movies.append(
                                found[0]
                            )

                    movie_grid(
                        recommendation_movies,
                        "recommendations"
                    )

                else:

                    st.warning(
                        "This movie isn't available in the ML dataset."
                    )

            else:

                st.error(
                    "Could not connect to the recommendation API."
                )