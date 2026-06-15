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

# ---------------- DUPLICATE BLOCK ----------------

def already_posted(service, movie_id):
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute()
        for post in posts.get("items", []):
            if f"TMDB-{movie_id}" in post.get("content", ""):
                return True
    except:
        pass
    return False

# ---------------- TRAILER POPUP SYSTEM ----------------

def trailer_system(title):
    search_url = f"https://www.youtube.com/results?search_query={title}+official+trailer"

    return f"""
    <div id="popup" style="
        display:none;
        position:fixed;
        top:0;left:0;
        width:100%;height:100%;
        background:rgba(0,0,0,0.95);
        z-index:9999;
        justify-content:center;
        align-items:center;">

        <div style="width:90%;max-width:900px;position:relative;">

            <iframe width="100%" height="500"
            src="{search_url}"
            style="border:none;background:white;">
            </iframe>

            <button onclick="closeTrailer()"
            style="position:absolute;top:-20px;right:-20px;
            background:white;border:none;
            font-size:22px;width:40px;height:40px;
            border-radius:50%;cursor:pointer;">
            ✖
            </button>

        </div>
    </div>

    <script>
    function openTrailer() {{
        document.getElementById("popup").style.display = "flex";
    }}

    function closeTrailer() {{
        document.getElementById("popup").style.display = "none";
    }}
    </script>
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

for movie in movies[:10]:

    movie_id = movie.get("id")
    title = movie.get("title", "Untitled")
    overview = movie.get("overview", "")
    poster = movie.get("poster_path")

    if already_posted(service, movie_id):
        print("Skipped:", title)
        continue

    # clickable poster (OPEN TRAILER)
    poster_html = ""
    if poster:
        poster_html = f"""
        <img src="https://image.tmdb.org/t/p/w500{poster}"
        style="width:100%;border-radius:10px;cursor:pointer;"
        onclick="openTrailer()">
        """

    category = get_category(title)

    content = f"""
    <div style="font-family:Arial;">

    {poster_html}

    <h2>{title}</h2>

    <p>{overview}</p>

    <h3>🎬 Trailer</h3>

    <p>Click poster to watch trailer</p>

    {trailer_system(title)}

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
