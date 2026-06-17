import os
import json
import requests
from googleapiclient.discovery import build

# =====================
# ENV
# =====================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

POST_FILE = "posted.json"

# =====================
# LOAD POSTED VIDEOS
# =====================
if os.path.exists(POST_FILE):
    posted = set(json.load(open(POST_FILE)))
else:
    posted = set()

# =====================
# GET ACCESS TOKEN
# =====================
def get_access_token():
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    r = requests.post(url, data=data)
    res = r.json()

    if "access_token" not in res:
        raise Exception(f"Token Error: {res}")

    return res["access_token"]

ACCESS_TOKEN = get_access_token()

# =====================
# YOUTUBE API
# =====================
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_videos():
    return youtube.search().list(
        q="official football match highlights premier league ucl world cup",
        part="snippet",
        maxResults=5,
        order="date",
        type="video"
    ).execute()

# =====================
# FILTER SYSTEM
# =====================
BAD_WORDS = [
    "funny", "meme", "prank", "edit",
    "shorts", "comedy", "reaction", "tiktok"
]

def is_bad(title):
    t = title.lower()
    return any(w in t for w in BAD_WORDS) or len(title) < 25

# =====================
# CATEGORY SYSTEM
# =====================
def get_category(title):
    t = title.lower()

    if "world cup" in t:
        return "worldcup"
    elif "champions league" in t or "ucl" in t:
        return "ucl"
    else:
        return "premierleague"

# =====================
# BLOGGER POST
# =====================
def post(title, video_id, desc, label):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    content = f"""
    <h2>{title}</h2>
    <iframe width="100%" height="315"
    src="https://www.youtube.com/embed/{video_id}"
    allowfullscreen></iframe>
    <p>{desc}</p>
    """

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": content,
        "labels": [label]
    }

    res = requests.post(url, headers=headers, json=data)
    print("Status:", res.status_code)

# =====================
# MAIN LOGIC
# =====================
def main():
    global posted

    videos = get_videos()

    for item in videos["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        desc = item["snippet"]["description"][:150]

        # duplicate check
        if video_id in posted:
            continue

        # filter check
        if is_bad(title):
            continue

        # category
        label = get_category(title)

        # post
        post(title, video_id, desc, label)

        # save
        posted.add(video_id)

    # save file
    with open(POST_FILE, "w") as f:
        json.dump(list(posted), f)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    main()
