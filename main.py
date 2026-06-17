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

DAILY_LIMIT = 5
DELAY = 8

# =====================
# LOAD POST HISTORY
# =====================
if os.path.exists(POST_FILE):
    posted = set(json.load(open(POST_FILE)))
else:
    posted = set()

# =====================
# ACCESS TOKEN
# =====================
def get_token():
    r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )
    data = r.json()

    if "access_token" not in data:
        raise Exception(data)

    return data["access_token"]

ACCESS_TOKEN = get_token()

# =====================
# YOUTUBE SEARCH (STRICT)
# =====================
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_videos():
    return youtube.search().list(
        q="official match highlights fifa world cup euro champions league premier league",
        part="snippet",
        maxResults=10,
        order="date",
        type="video"
    ).execute()

# =====================
# CLEAN FILTER (IMPORTANT)
# =====================
BAD_WORDS = [
    "funny", "meme", "prank", "shorts",
    "comedy", "reaction", "edit", "tiktok"
]

FOOTBALL_WORDS = [
    "goal", "match", "highlights",
    "fifa", "world cup", "euro",
    "ucl", "champions", "premier"
]

def is_clean(title):
    t = title.lower()

    if any(b in t for b in BAD_WORDS):
        return False

    if len(title) < 30:
        return False

    if not any(f in t for f in FOOTBALL_WORDS):
        return False

    return True

# =====================
# CATEGORY SYSTEM
# =====================
def category(title):
    t = title.lower()

    if "world cup" in t or "fifa" in t:
        return "FIFA"
    elif "euro" in t:
        return "EURO"
    elif "champions league" in t or "ucl" in t:
        return "UCL"
    else:
        return "EPL"

# =====================
# BLOG POST
# =====================
def post(title, vid, desc, label):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    content = f"""
    <h2>{title}</h2>
    <iframe width="100%" height="315"
    src="https://www.youtube.com/embed/{vid}"
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
    print("POSTED:", title, r.status_code)

# =====================
# MAIN ENGINE
# =====================
def main():
    global posted

    videos = get_videos()
    count = 0

    for v in videos["items"]:
        if count >= DAILY_LIMIT:
            break

        vid = v["id"]["videoId"]
        title = v["snippet"]["title"]
        desc = v["snippet"]["description"][:150]

        # duplicate check
        if vid in posted:
            continue

        # clean filter
        if not is_clean(title):
            continue

        # category
        label = category(title)

        # post
        post(title, vid, desc, label)

        # save
        posted.add(vid)
        count += 1

        time.sleep(DELAY)

    with open(POST_FILE, "w") as f:
        json.dump(list(posted), f)

if __name__ == "__main__":
    main()
