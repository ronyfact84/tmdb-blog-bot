import requests
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TMDB_API_KEY = os.environ["TMDB_API_KEY"]
BLOG_ID = os.environ["BLOG_ID"]

def get_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    return requests.get(url).json()["results"]

def post_to_blogger(title, content):

    creds = Credentials(
        None,
        refresh_token=os.environ["REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"]
    )

    creds.refresh(Request())

    service = build("blogger", "v3", credentials=creds)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": title,
            "content": content
        }
    ).execute()

movies = get_movies()

for m in movies[:3]:
    title = m["title"]
    content = f"<img src='https://image.tmdb.org/t/p/w500{m['poster_path']}'><br>{m['overview']}"
    post_to_blogger(title, content)
