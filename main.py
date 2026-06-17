import os
from googleapiclient.discovery import build
import requests

# ===== ENV VARIABLES =====
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

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

def post_to_blogger(title, video_id, desc):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    content = f"""
    <h2>{title}</h2>
    <iframe width="100%" height="315"
    src="https://www.youtube.com/embed/{video_id}"
    frameborder="0" allowfullscreen></iframe>
    <p>{desc}</p>
    """

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": content
    }

    res = requests.post(url, headers=headers, json=data)
    print(res.status_code, res.text)

def main():
    videos = get_videos()

    for item in videos["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        desc = item["snippet"]["description"][:150]

        post_to_blogger(title, video_id, desc)

if __name__ == "__main__":
    main()
