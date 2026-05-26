import requests
from bs4 import BeautifulSoup
import os
import time
 
KEYWORDS = [
    ["售", "滅火器"],
    ["售", "如蝶翩翩"],
    ["售", "五月天"]
]
PTT_URL = "https://www.ptt.cc/bbs/Drama-Ticket/index.html"
SEEN_FILE = "seen.txt"
WEBHOOK = os.environ["DISCORD_WEBHOOK"]
 
SESSION = requests.Session()
SESSION.cookies.set("over18", "1")
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.ptt.cc/bbs/Drama-Ticket/index.html"
})
 
def send_discord(title, url):
    requests.post(WEBHOOK, json={
        "embeds": [{
            "title": "🎫 PTT 出現符合文章！",
            "description": f"**{title}**\n{url}",
            "color": 0x5865F2
        }]
    })
 
def get_titles():
    for attempt in range(3):
        try:
            res = SESSION.get(PTT_URL, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            titles = []
            for a in soup.select(".r-ent .title a"):
                titles.append((a.text.strip(), "https://www.ptt.cc" + a["href"]))
            return titles
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(3)
    raise Exception("Failed to fetch PTT after 3 attempts")
 
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(f.read().splitlines())
    return set()
 
def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(seen))
 
titles = get_titles()
print(f"Fetched {len(titles)} articles")
 
seen = load_seen()
new_seen = set(seen)
 
for title, url in titles:
    if url not in seen:
        new_seen.add(url)
        print(f"New article: {title}")
        if any(all(k in title for k in group) for group in KEYWORDS):
            print(f"MATCH: {title}")
            send_discord(title, url)
 
save_seen(new_seen)
print("Done")
