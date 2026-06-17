import os
import json
import time
import requests
from googleapiclient.discovery import build

# =====================
# CONFIG
# =====================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

POST_FILE = "posted.json"

# 🔥 DAILY LIMIT (IMPORTANT)
DAILY_LIMIT = 5

# delay between posts (seconds)
DELAY_BETWEEN_POSTS = 10

# =====================
# LOAD POSTED VIDEOS
# =====================
if os.path.exists(POST_FILE):
    posted = set(json.load(open(POST_FILE)))
else:
    posted = set()

# =====================
# ACCESS TOKEN
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
        raise Exception(res)

    return res["access_token"]

ACCESS_TOKEN = get_access_token()

# =====================
# YOUTUBE
# =====================
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_videos():
    return youtube.search().list(
        q="official football highlights fifa euro champions league premier league",
        part="snippet",
        maxResults=10,
        order="date",
        type="video"
    ).execute()

# =====================
# FILTER
# =====================
BAD_WORDS = ["funny", "meme", "prank", "shorts", "edit", "comedy"]

def is_bad(title):
    t = title.lower()
    return any(w in t for w in BAD_WORDS) or len(title) < 25

# =====================
# CATEGORY SYSTEM
# =====================
def get_category(title):
    t = title.lower()

    if "world cup" in t or "fifa" in t:
        return "fifa"
    elif "euro" in t or "european championship" in t:
        return "euro"
    elif "champions league" in t or "ucl" in t:
        return "ucl"
    else:
        return "premierleague"

# =====================
# BLOG POST
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

    r = requests.post(url, headers=headers, json=data)
    print("Posted:", title)
    print("Status:", r.status_code)

# =====================
# MAIN
# =====================
def main():
    global posted

    videos = get_videos()
    count = 0

    for item in videos["items"]:
        if count >= DAILY_LIMIT:
            break

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
        count += 1

        # delay (important for spam safety)
        time.sleep(DELAY_BETWEEN_POSTS)

    # save file
    with open(POST_FILE, "w") as f:
        json.dump(list(posted), f)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    main()
