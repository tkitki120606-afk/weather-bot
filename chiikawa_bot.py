import os
import requests
import feedparser
import sys
import time
from datetime import datetime, timedelta, timezone

# === 設定エリア ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
# ★ここを今回発行したGASのURLにしてください
GAS_URL = "https://script.google.com/macros/s/AKfycbyizm4KlixMLVMsjD5b2C57pfsMejv5WyIeFz0b6GLREUeHiCfsJYQSVsW2CJ9Y9ns9Gw/exec"

FEEDS = [
    {"name": "公式ニュース", "file": "last_chiikawa_official.txt", "url": "https://chiikawa.jp/feed"},
    {"name": "ちいかわ情報RSS", "file": "last_chiikawa_rssapp.txt", "url": "https://rss.app/feeds/ieXLGys59HQY5HaB.xml"}
]

# === 🌟 配信関数（Multicast用） ===
def send_to_subscribers(target_users, message):
    if not target_users: return
    line_url = "https://api.line.me/v2/bot/message/multicast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": target_users, "messages": [{"type": "text", "text": message}]}
    requests.post(line_url, headers=headers, json=payload)
    time.sleep(1) # API制限回避用

# === メイン処理 ===
# 1. 配信対象者リストをGASから取得
try:
    response = requests.get(GAS_URL).json()
    target_users = response.get("chiikawa", []) # 「ちいかわ」をONにしている人のリスト
    
    if not target_users:
        print("ちいかわニュースを購読している人がいません。終了します。")
        sys.exit()
except Exception as e:
    print(f"GASからの取得に失敗しました: {e}")
    sys.exit()

# 2. 記事のチェックと送信
seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

for feed_info in FEEDS:
    name = feed_info["name"]
    filename = feed_info["file"]
    url = feed_info["url"]

    sent_links = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            sent_links = [line.strip() for line in f.readlines()]

    feed = feedparser.parse(url)
    
    for entry in reversed(feed.entries):
        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        
        if pub_date >= seven_days_ago and entry.link not in sent_links:
            print(f"[{name}] 新しい記事送信中: {entry.title}")
            message = f"📢【ちいかわ {name}】\n\n{entry.title}\n\n{entry.link}"
            
            # 🌟 ここでマルチキャスト送信
            send_to_subscribers(target_users, message)
            
            with open(filename, "a") as f:
                f.write(entry.link + "\n")
