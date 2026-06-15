import os
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")

# ---------------- BLOGGER AUTH ----------------

def get_service():
    creds = Credentials(
        None,
        refresh_token=os.environ.get("REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET")
    )
    creds.refresh(Request())
    return build("blogger", "v3", credentials=creds)

# ---------------- TMDB ----------------

def get_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    return requests.get(url, timeout=20).json().get("results", [])

def get_upcoming():
    url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={TMDB_API_KEY}"
    return requests.get(url, timeout=20).json().get("results", [])

# ---------------- DUPLICATE BLOCKER ----------------

def already_posted(service, movie_id):
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute()
        for post in posts.get("items", []):
            if f"TMDB-{movie_id}" in post.get("content", ""):
                return True
    except:
        pass
    return False

# ---------------- PRO POPUP TRAILER ----------------

def popup_trailer_ui(title):
    search_url = f"https://www.youtube.com/results?search_query={title}+official+trailer"

    return f"""
    <div style="margin-top:15px;">

    <button onclick="openTrailer()"
    style="background:#e50914;color:white;padding:10px 18px;
    border:none;border-radius:6px;font-weight:bold;cursor:pointer;">
    ▶ Watch Trailer
    </button>

    <div id="trailerPopup" style="
        display:none;
        position:fixed;
        top:0;
        left:0;
        width:100%;
        height:100%;
        background:rgba(0,0,0,0.9);
        z-index:9999;
        justify-content:center;
        align-items:center;">

        <div style="width:90%;max-width:800px;position:relative;">

            <iframe width="100%" height="450"
            src="https://www.youtube.com/embed?listType=search&list={title}+trailer"
            frameborder="0" allowfullscreen>
            </iframe>

            <button onclick="closeTrailer()"
            style="position:absolute;top:-15px;right:-15px;
            background:white;border:none;font-size:20px;
            border-radius:50%;width:35px;height:35px;cursor:pointer;">
            ✖
            </button>

        </div>
    </div>

    <script>
    function openTrailer() {{
        document.getElementById("trailerPopup").style.display = "flex";
    }}

    function closeTrailer() {{
        document.getElementById("trailerPopup").style.display = "none";
    }}
    </script>

    <a href="{search_url}" target="_blank"
    style="display:inline-block;margin-top:10px;
    background:#444;color:white;padding:8px 14px;
    border-radius:6px;text-decoration:none;">
    🔎 Search Trailer
    </a>

    </div>
    """

# ---------------- CATEGORY ----------------

def get_category(title):
    t = title.lower()
    if "hindi" in t:
        return "Hindi Dubbed"
    if "bollywood" in t:
        return "Bollywood Movies"
    if "web series" in t:
        return "Web Series"
    return "Hollywood Movies"

# ---------------- POST ----------------

def post(service, title, content, category):
    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": title,
            "content": content,
            "labels": [category]
        }
    ).execute()

# ---------------- MAIN ----------------

service = get_service()

movies = get_movies() + get_upcoming()

for movie in movies[:8]:

    movie_id = movie.get("id")
    title = movie.get("title", "Untitled")
    overview = movie.get("overview", "")
    poster = movie.get("poster_path")

    if already_posted(service, movie_id):
        print("Skipped:", title)
        continue

    poster_html = ""
    if poster:
        poster_html = f"""
        <img src="https://image.tmdb.org/t/p/w500{poster}"
        style="width:100%;border-radius:10px;">
        """

    trailer_ui = popup_trailer_ui(title)

    details_btn = f"""
    <a href="https://www.themoviedb.org/movie/{movie_id}"
    target="_blank"
    style="background:#2196F3;color:white;padding:10px 18px;
    text-decoration:none;border-radius:6px;margin-left:10px;">
    ℹ Details
    </a>
    """

    category = get_category(title)

    content = f"""
    <div style="font-family:Arial;">

    {poster_html}

    <h2>{title}</h2>

    <p>{overview}</p>

    <h3>🎬 Trailer</h3>

    {trailer_ui}

    <div style="margin-top:10px;">
    {details_btn}
    </div>

    <hr>

    <p><b>Category:</b> {category}</p>
    <p style="color:gray;">TMDB-{movie_id}</p>

    </div>
    """

    try:
        post(service, title, content, category)
        print("Posted:", title)
    except Exception as e:
        print("Error:", title, e)
