import requests
from bs4 import BeautifulSoup
import os

KEYWORDS = ["售", "滅火器"]
PTT_URL = "https://www.ptt.cc/bbs/Drama-Ticket/index.html"
SEEN_FILE = "seen.txt"

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

def send_discord(title, url):
    requests.post(WEBHOOK, json={
        "embeds": [{
            "title": "🎫 PTT 出現符合文章！",
            "description": f"**{title}**\n{url}",
            "color": 0x5865F2
        }]
    })

def get_titles():
    res = requests.get(PTT_URL, cookies={"over18": "1"})
    soup = BeautifulSoup(res.text, "html.parser")
    titles = []
    for a in soup.select(".title a"):
        titles.append((a.text.strip(), "https://www.ptt.cc" + a["href"]))
    return titles

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(f.read().splitlines())
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(seen))

titles = get_titles()
seen = load_seen()
new_seen = set(seen)

for title, url in titles:
    if url not in seen:
        new_seen.add(url)
        if all(k in title for k in KEYWORDS):
            send_discord(title, url)

save_seen(new_seen)
