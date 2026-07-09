import os
import requests
import feedparser
import sys
import time
from datetime import datetime, timedelta, timezone

# === 設定エリア ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')

FEEDS = [
    {"name": "全般ニュース", "file": "last_atom.txt", "url": "https://jp.finalfantasyxiv.com/lodestone/news/atom/"},
    {"name": "ニュース", "file": "last_news.txt", "url": "https://jp.finalfantasyxiv.com/lodestone/news/news.xml"},
    {"name": "トピックス", "file": "last_topics.txt", "url": "https://jp.finalfantasyxiv.com/lodestone/news/topics.xml"}
]

def send_line(message):
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(line_url, headers=headers, json=payload)
    time.sleep(1) # 連投による制限を避けるための1秒待機

# === メイン処理 ===
# 7日前を計算
one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

for feed_info in FEEDS:
    name = feed_info["name"]
    filename = feed_info["file"]
    url = feed_info["url"]

    # 前回のリンクを読み込む
    last_link = ""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            last_link = f.read().strip()

    feed = feedparser.parse(url)
    
    # 記事を古い順（日付が古い順）に処理するため、reversedを使用
    entries = list(reversed(feed.entries))

    latest_link_for_this_feed = last_link

    for entry in entries:
        # 記事の日付を取得
        published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        
        # チェック条件：7日以内 かつ last_linkより新しい(または初回)
        # ※初回のlast_linkが空の場合は、とりあえず7日以内のものを全部送る
        if published_time >= one_week_ago:
            if last_link == "" or (entry.link != last_link and published_time > datetime.fromtimestamp(time.mktime(feedparser.parse(last_link).entries[0].published_parsed) if last_link else 0, tz=timezone.utc) - timedelta(days=999)):
                # ※シンプルにリンク比較で処理します
                if entry.link == last_link:
                    continue
                
                print(f"[{name}] 送信中: {entry.title}")
                image_url = entry.media_thumbnail[0]['url'] if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail else ""
                
                message = f"📢【FF14 {name}】\n\n{entry.title}\n\n{entry.link}"
                if image_url:
                    message += f"\n\n{image_url}"
                
                send_line(message)
                latest_link_for_this_feed = entry.link # 最新を更新

    # 今回の最新リンクを記録
    with open(filename, "w") as f:
        f.write(latest_link_for_this_feed)
