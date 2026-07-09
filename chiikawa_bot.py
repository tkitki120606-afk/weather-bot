import os
import requests
import feedparser

# === 設定エリア ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')

# 監視したいURLリスト
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
for feed_info in FEEDS:
    name = feed_info["name"]
    filename = feed_info["file"]
    url = feed_info["url"]

    # RSSを取得
    feed = feedparser.parse(url)
    if len(feed.entries) == 0:
        print(f"[{name}] 記事が取得できませんでした")
        continue

    latest_entry = feed.entries[0]
    
    # 前回の記録を読み込む
    last_link = ""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            last_link = f.read().strip()

    # 新しい記事か判定
    if latest_entry.link != last_link:
        print(f"[{name}] 新しい記事発見: {latest_entry.title}")
        message = f"📢【ちいかわ {name}】\n\n{latest_entry.title}\n\n{latest_entry.link}"
        send_line(message)
        
        # 記録を更新
        with open(filename, "w") as f:
            f.write(latest_entry.link)
    else:
        print(f"[{name}] 更新なし")
