import os
import requests
from bs4 import BeautifulSoup
import sys

# === 設定 ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')
LAST_INFO_FILE = "last_chiikawa.txt"
TARGET_URL = "https://chiikawa-info.jp/news/"

# === メイン処理 ===
response = requests.get(TARGET_URL)
response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, 'html.parser')

# ★ここを変更：すべてのタイトルを表示させて確認します
news_list = soup.select('.news-list li a') 

print(f"DEBUG: {len(news_list)} 個の記事を見つけました")

if news_list:
    latest_item = news_list[0]
    latest_title = latest_item.get_text().strip()
    print(f"DEBUG: 最新のタイトルは『{latest_title}』です") # 何を拾ったかログに出す

    # 前回の記録を読み込み
    last_info = ""
    if os.path.exists(LAST_INFO_FILE):
        with open(LAST_INFO_FILE, "r") as f:
            last_info = f.read().strip()

    if latest_title != last_info:
        print("新しい情報なので送信します！")
        # (LINE送信処理はそのまま)
        # ... (中略: 送信処理) ...
        # (最後に記録を保存)
        with open(LAST_INFO_FILE, "w") as f:
            f.write(latest_title)
    else:
        print("前回の情報と同じなので送信しません。")
else:
    print("DEBUG: 記事が1つも見つかりませんでした（HTMLの指定が間違っているかも）")
