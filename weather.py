import os
import requests
import json
import datetime
import sys

# === 🛠️ 設定情報 ===
# 直書きをやめて、GitHubの秘密箱から読み込む形にします
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')
# ===================

print("--- [1] タイムリー詳細お天気システム 起動 ---")

if "ここに" in LINE_TOKEN or "ここに" in USER_ID:
    print("❌ エラー: 鍵の書き換えができていません！")
    sys.exit()

# 🌤️ 天気コード（数字）を分かりやすい絵文字に変換する辞書
WEATHER_EMOJI = {
    0: "☀️ 晴れ",
    1: "🌤️ ほぼ晴れ",
    2: "⛅ 時々曇り",
    3: "☁️ 曇り",
    45: "🌫️ 霧",
    48: "🌫️ 霧",
    51: "🌦️ 小雨",
    53: "🌦️ 小雨",
    55: "🌦️ 小雨",
    61: "🌧️ 雨",
    63: "🌧️ 雨",
    65: "🌧️ 激しい雨",
    71: "❄️ 雪",
    73: "❄️ 雪",
    75: "❄️ 豪雪",
    80: "🌦️ にわか雨",
    81: "🌧️ にわか雨",
    82: "🌧️ 激しいにわか雨",
    95: "⚡ 雷雨",
}


def get_weather_emoji(code):
    return WEATHER_EMOJI.get(code, "❓ 不明")


try:
    print("[2] Open-Meteo APIから超詳細データを取得中...")
    url = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&minutely_15=temperature_2m,precipitation_probability,weather_code&timezone=Asia%2FTokyo"
    response = requests.get(url).json()

    # 取得したデータボックスを取り出す
    min_data = response["minutely_15"]
    times = min_data["time"]
    temps = min_data["temperature_2m"]
    probs = min_data["precipitation_probability"]
    codes = min_data["weather_code"]

    # ⏰ 今現在の時間を基準にする
    now = datetime.datetime.now()
    print(f" ➔ 現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # 📋 メッセージの本文を組み立てる
    pop_text = ""
    count = 0

    for i in range(len(times)):
        data_time = datetime.datetime.strptime(times[i], "%Y-%m-%dT%H:%M")

        # 「今の時間以降」かつ「30分間隔」のデータだけをピックアップ
        if data_time >= now and data_time.minute in [0, 30]:
            time_label = data_time.strftime("%H:%M")
            emoji = get_weather_emoji(codes[i])
            temp = temps[i]
            prob = probs[i]

            pop_text += f"🕒 {time_label} ➔ {emoji} | {temp}°C | ☔ {prob}%\n"

            count += 1
            if count >= 10:  # 5時間分（10枠）でストップ
                break

    # 💌 LINEに送る文章
    message_text = (
        f"📢【これからのピンポイント天気】\n" f"（ここから5時間分・30分刻み）\n\n" f"{pop_text}"
    )

    print("[3] LINEのサーバーにスマートに送信中...")
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}",
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message_text}],
    }

    res = requests.post(line_url, headers=headers, data=json.dumps(payload))

    print(f"[4] 送信結果確認 (コード: {res.status_code})")
    if res.status_code == 200:
        print("🎉 大成功！スマホに見やすく届いたか確認してね！")
    else:
        print(f"❌ エラー: {res.text}")

except Exception as e:
    print(f"❌ エラーが発生しました:\n{e}")