import os
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")

# YouTube API optional (no crash if missing)
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

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

# ---------------- TMDB MOVIES ----------------

def get_movies():
    if not TMDB_API_KEY:
        return []

    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    return requests.get(url, timeout=20).json().get("results", [])

# ---------------- DUPLICATE CHECK (SAFE) ----------------

def already_posted(service, movie_id):
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute()

        for post in posts.get("items", []):
            if f"TMDB-{movie_id}" in post.get("content", ""):
                return True
    except:
        pass

    return False

# ---------------- TRAILER ----------------

def get_trailer(title):
    if not YOUTUBE_API_KEY:
        return None

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": f"{title} official trailer",
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY
    }

    try:
        res = requests.get(url, params=params, timeout=20).json()
        return res["items"][0]["id"]["videoId"]
    except:
        return None

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
movies = get_movies()

for movie in movies[:5]:

    movie_id = movie.get("id")
    title = movie.get("title", "Untitled")
    overview = movie.get("overview", "")
    poster = movie.get("poster_path")

    if already_posted(service, movie_id):
        print("Skipped duplicate:", title)
        continue

    # Poster
    poster_html = ""
    if poster:
        poster_html = f"""
        <img src="https://image.tmdb.org/t/p/w500{poster}"
        style="width:100%;border-radius:10px;">
        """

    # Trailer
    video_id = get_trailer(title)

    if video_id:
        trailer_html = f"""
        <iframe width="100%" height="400"
        src="https://www.youtube.com/embed/{video_id}"
        frameborder="0" allowfullscreen></iframe>
        """
        watch_link = f"https://www.youtube.com/watch?v={video_id}"
    else:
        trailer_html = "<p>No trailer found</p>"
        watch_link = f"https://www.youtube.com/results?search_query={title}+trailer"

    # Buttons
    watch_btn = f"""
    <a href="{watch_link}" target="_blank"
    style="background:#e50914;color:white;padding:10px 18px;
    text-decoration:none;border-radius:5px;">
    ▶ Watch Trailer
    </a>
    """

    details_btn = f"""
    <a href="https://www.themoviedb.org/movie/{movie_id}" target="_blank"
    style="background:#2196F3;color:white;padding:10px 18px;
    text-decoration:none;border-radius:5px;margin-left:10px;">
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
    {trailer_html}

    <div style="margin-top:10px;">
    {watch_btn}
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
