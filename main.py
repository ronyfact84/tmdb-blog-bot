
import requests
from googleapiclient.discovery import build

TMDB_API_KEY = "7472337f81f4ea2baea17e6253bc1077"
BLOG_ID = "4894620542423770622"

# GET POPULAR MOVIE
def get_movie():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    return data["results"][0]

# GET TRAILER
def get_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()

    for v in data.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return v["key"]
    return None

# BUILD POST
def build_post(movie, trailer):
    title = movie["title"]
    poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

    content = f"""
    <h1>{title}</h1>
    <img src="{poster}" width="300"/>

    <p>{movie.get('overview','')}</p>

    <h3>Trailer</h3>
    <iframe width="100%" height="450"
    src="https://www.youtube.com/embed/{trailer}"
    frameborder="0" allowfullscreen></iframe>
    """

    return title, content

# POST TO BLOGGER
def post_to_blogger(title, content):
    service = build("blogger", "v3", developerKey=TMDB_API_KEY)

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": title, "content": content}
    ).execute()

    print("Posted Successfully!")

# MAIN
movie = get_movie()
trailer = get_trailer(movie["id"])

title, content = build_post(movie, trailer)
post_to_blogger(title, content)
