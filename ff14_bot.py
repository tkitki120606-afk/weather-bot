import os
import requests
import feedparser
import json
import sys

# === 設定エリア ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')
# トピックスを取得するURL
RSS_URL = "https://jp.finalfantasyxiv.com/lodestone/news/topics.xml"
LAST_LINK_FILE = "last_link.txt"

# === 読み込み処理 ===
last_link = ""
if os.path.exists(LAST_LINK_FILE):
    with open(LAST_LINK_FILE, "r") as f:
        last_link = f.read().strip()

# === RSSの取得 ===
feed = feedparser.parse(RSS_URL)

# もしニュースが取れなかったら終了（エラー回避）
if len(feed.entries) == 0:
    print("ニュースが見つかりません。スキップします。")
    sys.exit(0)

latest_entry = feed.entries[0]

# === 新しいニュースかチェック ===
if latest_entry.link != last_link:
    print(f"新しいトピックス発見: {latest_entry.title}")

    # 記事内の画像URLがあれば取得する
    image_url = ""
    if hasattr(latest_entry, 'media_thumbnail') and len(latest_entry.media_thumbnail) > 0:
        image_url = latest_entry.media_thumbnail[0]['url']

    # LINEに送るメッセージ作成
    message = f"📢【FF14公式トピックス】\n\n{latest_entry.title}\n\n{latest_entry.link}"
    
    # 画像URLがあれば追記（LINEが自動でプレビューを出してくれます）
    if image_url:
        message += f"\n\n{image_url}"

    # LINE送信処理
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": USER_ID, 
        "messages": [{"type": "text", "text": message}]
    }
    
    requests.post(line_url, headers=headers, data=json.dumps(payload))
    
    # 今回のリンクを記録（次回、同じものを送らないため）
    with open(LAST_LINK_FILE, "w") as f:
        f.write(latest_entry.link)
else:
    print("新しいニュースはありません。")
