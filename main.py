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

service = get_service()

# ---------------- TMDB ----------------

def get_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    return requests.get(url, timeout=20).json().get("results", [])

# ---------------- DUPLICATE CHECK ----------------

def already_posted(movie_id):
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute()
        for post in posts.get("items", []):
            if f"TMDB-{movie_id}" in post.get("content", ""):
                return True
    except:
        pass
    return False

# ---------------- TRAILER (STABLE LINK) ----------------

def trailer_system(title):
    url = f"https://www.youtube.com/results?search_query={title}+official+trailer"

    return f"""
    <div style="margin-top:10px;">

    <a href="{url}" target="_blank"
    style="
        display:block;
        padding:15px;
        background:#e50914;
        color:white;
        text-align:center;
        border-radius:8px;
        text-decoration:none;
        font-weight:bold;">
        ▶ Watch Trailer
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

def post(title, content, category):
    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": title,
            "content": content,
            "labels": [category]
        }
    ).execute()

# ---------------- MAIN ----------------

movies = get_movies()

for movie in movies[:10]:

    movie_id = movie.get("id")
    title = movie.get("title", "Untitled")
    overview = movie.get("overview", "")
    poster = movie.get("poster_path")

    if already_posted(movie_id):
        print("Skipped:", title)
        continue

    poster_html = ""
    if poster:
        poster_html = f"""
        <img src="https://image.tmdb.org/t/p/w500{poster}"
        style="width:100%;border-radius:10px;">
        """

    category = get_category(title)

    content = f"""
    <div style="font-family:Arial;line-height:1.6;">

    {poster_html}

    <h2>{title}</h2>

    <p>{overview}</p>

    <h3>🎬 Trailer</h3>

    {trailer_system(title)}

    <hr>

    <p><b>Category:</b> {category}</p>
    <p style="color:gray;font-size:12px;">TMDB-{movie_id}</p>

    </div>
    """

    try:
        post(title, content, category)
        print("Posted:", title)
    except Exception as e:
        print("Error:", title, e)
