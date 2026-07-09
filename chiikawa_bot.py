import os
import requests
from bs4 import BeautifulSoup
import sys

# === 設定 ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')
LAST_INFO_FILE = "last_chiikawa.txt"
TARGET_URL = "https://chiikawa-info.jp/news/"

def send_line(message):
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(line_url, headers=headers, json=payload)

# === メイン処理 ===
response = requests.get(TARGET_URL)
# サイト側の文字化け対策
response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, 'html.parser')

# ★ここが重要！ニュースリストの場所を特定します
# 現在のサイト構造から「ニュース記事のタイトル一覧」を抜き出します
news_list = soup.select('.news-list li a') 

if news_list:
    # 一番新しい記事（リストの先頭）を取得
    latest_item = news_list[0]
    latest_title = latest_item.get_text().strip()
    latest_link = "https://chiikawa-info.jp" + latest_item.get('href')
    
    # 前回の記録と比較
    if os.path.exists(LAST_INFO_FILE):
        with open(LAST_INFO_FILE, "r") as f:
            last_info = f.read().strip()
    else:
        last_info = ""

    if latest_title != last_info:
        print(f"新しいちいかわ情報発見: {latest_title}")
        message = f"📢【ちいかわ情報局】\n\n{latest_title}\n\n{latest_link}"
        send_line(message)
        
        with open(LAST_INFO_FILE, "w") as f:
            f.write(latest_title)
    else:
        print("新しい情報なし")
else:
    print("情報を取得できませんでした")
