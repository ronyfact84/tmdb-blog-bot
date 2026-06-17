import os
import json
import requests
from googleapiclient.discovery import build

# =========================
# ENV VARIABLES
# =========================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

POSTED_FILE = "posted.json"

# =========================
# LOAD POSTED VIDEOS
# =========================
if os.path.exists(POSTED_FILE):
    posted_videos = set(json.load(open(POSTED_FILE)))
else:
    posted_videos = set()

# =========================
# GET ACCESS TOKEN
# =========================
def get_access_token():
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    res = requests.post(url, data=data)
    token = res.json()

    if "access_token" not in token:
        raise Exception(f"Token Error: {token}")

    return token["access_token"]

access_token = get_access_token()

# =========================
# YOUTUBE API
# =========================
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_videos():
    request = youtube.search().list(
        q="official football match highlights premier league ucl world cup",
        part="snippet",
        maxResults=5,
        order="date",
        type="video"
    )
    return request.execute()

# =========================
# FILTER SYSTEM
# =========================
bad_words = ["funny", "meme", "prank", "fail", "comedy", "edit"]

def is_bad_video(title):
    t = title.lower()
    return any(word in t for word in bad_words)

# =========================
# CATEGORY SYSTEM
# =========================
def get_category(title):
    t = title.lower()

    if "world cup" in t:
        return "worldcup"
    elif "champions league" in t or "ucl" in t:
        return "ucl"
    else:
        return "premierleague"

# =========================
# POST TO BLOGGER
# =========================
def post_to_blogger(title, video_id, desc, label):
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
        "content": content,
        "labels": [label]
    }

    res = requests.post(url, headers=headers, json=data)
    print("Status:", res.status_code)
    print(res.text)

# =========================
# MAIN
# =========================
def main():
    global posted_videos

    videos = get_videos()

    for item in videos["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        desc = item["snippet"]["description"][:150]

        # ❌ duplicate check
        if video_id in posted_videos:
            continue

        # ❌ filter bad videos
        if is_bad_video(title):
            continue

        # category
        label = get_category(title)

        # post
        post_to_blogger(title, video_id, desc, label)

        # save
        posted_videos.add(video_id)

    # save file
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted_videos), f)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
