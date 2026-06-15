import os
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ---------------- ENV ----------------

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
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

# ---------------- REAL TRAILER (YOUTUBE API) ----------------

def get_trailer(title):
    query = f"{title} official trailer"

    url = f"https://www.googleapis.com/youtube/v3/search?part=id&q={query}&key={YOUTUBE_API_KEY}&maxResults=1&type=video"

    try:
        res = requests.get(url, timeout=20).json()
        video_id = res["items"][0]["id"]["videoId"]

        embed = f"https://www.youtube.com/embed/{video_id}"

        return f"""
        <iframe width="100%" height="500"
        src="{embed}"
        frameborder="0"
        allowfullscreen></iframe>
        """

    except:
        return "<p>Trailer not available</p>"

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

# ---------------- POST TO BLOGGER ----------------

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

    trailer_html = get_trailer(title)
    category = get_category(title)

    content = f"""
    <div style="font-family:Arial;line-height:1.6;">

    {poster_html}

    <h2>{title}</h2>

    <p>{overview}</p>

    <h3>🎬 Official Trailer</h3>

    {trailer_html}

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
