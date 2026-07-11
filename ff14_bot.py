import os
import requests
import feedparser
import sys
import time
from datetime import datetime, timedelta, timezone

# === 設定エリア ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
# ★ここをあなたのGASのURLに書き換えてください！
GAS_URL = "https://script.google.com/macros/s/AKfycbyizm4KlixMLVMsjD5b2C57pfsMejv5WyIeFz0b6GLREUeHiCfsJYQSVsW2CJ9Y9ns9Gw/exec"

FEEDS = [
    {"name": "全般ニュース", "file": "last_atom.txt", "url": "https://jp.finalfantasyxiv.com/lodestone/news/atom/"},
    {"name": "ニュース", "file": "last_news.txt", "url": "https://jp.finalfantasyxiv.com/lodestone/news/news.xml"},
    {"name": "トピックス", "file": "last_topics.txt", "url": "https://jp.finalfantasyxiv.com/lodestone/news/topics.xml"}
]

# === 🌟 変更点: Multicast API を使う関数に変更 ===
def send_to_subscribers(target_users, message):
    if not target_users: return
    line_url = "https://api.line.me/v2/bot/message/multicast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": target_users, "messages": [{"type": "text", "text": message}]}
    requests.post(line_url, headers=headers, json=payload)
    time.sleep(1) 

# === メイン処理 ===
# 1. 配信対象者リストをGASから取得
try:
    response = requests.get(GAS_URL).json()
    target_users = response.get("ff14", []) # ff14をONにしている人だけ取得
    
    if not target_users:
        print("FF14ニュースを購読している人がいません。終了します。")
        sys.exit()
except Exception as e:
    print(f"GASからの取得に失敗しました: {e}")
    sys.exit()

# 2. 記事のチェックと送信
one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

for feed_info in FEEDS:
    name = feed_info["name"]
    filename = feed_info["file"]
    url = feed_info["url"]

    last_link = ""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            last_link = f.read().strip()

    feed = feedparser.parse(url)
    entries = list(reversed(feed.entries))
    latest_link_for_this_feed = last_link

    for entry in entries:
        published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        
        if published_time >= one_week_ago:
            if last_link == "" or (entry.link != last_link and published_time > datetime.fromtimestamp(time.mktime(feedparser.parse(last_link).entries[0].published_parsed) if last_link else 0, tz=timezone.utc) - timedelta(days=999)):
                if entry.link == last_link:
                    continue
                
                print(f"[{name}] 送信中: {entry.title}")
                image_url = entry.media_thumbnail[0]['url'] if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail else ""
                
                message = f"📢【FF14 {name}】\n\n{entry.title}\n\n{entry.link}"
                if image_url:
                    message += f"\n\n{image_url}"
                
                # 🌟 変更点: ここでマルチキャスト送信
                send_to_subscribers(target_users, message)
                latest_link_for_this_feed = entry.link

    with open(filename, "w") as f:
        f.write(latest_link_for_this_feed)
