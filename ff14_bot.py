import os
import requests
import feedparser
import json

# 設定（環境変数は既存の天気botと同じものを使います！）
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')
RSS_URL = "https://ja.finalfantasyxiv.com/lodestone/news/atom/"
LAST_LINK_FILE = "last_link.txt"

# 前回のニュースリンクを読み込む
last_link = ""
if os.path.exists(LAST_LINK_FILE):
    with open(LAST_LINK_FILE, "r") as f:
        last_link = f.read().strip()

# LodestoneのRSSを取得
feed = feedparser.parse(RSS_URL)
latest_entry = feed.entries[0]  # 最新の1件

# 新しいニュースかチェック（前回とリンクが違えば通知）
if latest_entry.link != last_link:
    print("新しいニュースを発見！送信します。")
    
    # LINEに送るメッセージ
    message = f"📢【FF14公式ニュース】\n\n{latest_entry.title}\n{latest_entry.link}"
    
    # LINE送信
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(line_url, headers=headers, data=json.dumps(payload))
    
    # 今回のリンクを「last_link.txt」に保存
    with open(LAST_LINK_FILE, "w") as f:
        f.write(latest_entry.link)
else:
    print("新しいニュースはありません。")
