import os
import requests
import feedparser
from datetime import datetime, timedelta, timezone

# === 設定エリア ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')
FEEDS = [
    {"name": "公式ニュース", "file": "last_chiikawa_official.txt", "url": "https://chiikawa.jp/feed"},
    {"name": "ちいかわ情報RSS", "file": "last_chiikawa_rssapp.txt", "url": "https://rss.app/feeds/ieXLGys59HQY5HaB.xml"}
]

def send_line(message):
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(line_url, headers=headers, json=payload)

# === メイン処理 ===
# 7日前を計算
seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

for feed_info in FEEDS:
    name = feed_info["name"]
    filename = feed_info["file"]
    url = feed_info["url"]

    feed = feedparser.parse(url)
    
    # 送信済みリストを読み込み
    sent_links = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            sent_links = [line.strip() for line in f.readlines()]

    # 新しい順にチェック（リストを逆順にする）
    for entry in reversed(feed.entries):
        # 記事の日付を変換
        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        
        # 1. 7日以内の記事か？ 2. まだ送っていないか？
        if pub_date >= seven_days_ago and entry.link not in sent_links:
            print(f"[{name}] 新しい記事発見: {entry.title}")
            message = f"📢【ちいかわ {name}】\n\n{entry.title}\n\n{entry.link}"
            send_line(message)
            
            # 送信済みとして記録に追加
            with open(filename, "a") as f:
                f.write(entry.link + "\n")
