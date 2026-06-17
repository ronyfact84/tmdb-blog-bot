import os
import requests
from googleapiclient.discovery import build

# ===== ENV VARIABLES =====
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

# ===== GET ACCESS TOKEN =====
def get_access_token():
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    res = requests.post(url, data=data)
    token_data = res.json()

    if "access_token" not in token_data:
        raise Exception(f"Token Error: {token_data}")

    return token_data["access_token"]

access_token = get_access_token()

# ===== YOUTUBE API =====
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_videos():
    request = youtube.search().list(
        q="football highlights",
        part="snippet",
        maxResults=3,
        order="date",
        type="video"
    )
    return request.execute()

# ===== POST TO BLOGGER =====
def post_to_blogger(title, video_id, desc):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    content = f"""
    <h2>{title}</h2>
    <iframe width="100%" height="315"
    src="https://www.youtube.com/embed/{video_id}"
    allowfullscreen></iframe>
    <p>{desc}</p>
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": content
    }

    response = requests.post(url, headers=headers, json=data)
    print("Status:", response.status_code)
    print(response.text)

# ===== MAIN =====
def main():
    videos = get_videos()

    for item in videos["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        desc = item["snippet"]["description"][:150]

        post_to_blogger(title, video_id, desc)

if __name__ == "__main__":
    main()
