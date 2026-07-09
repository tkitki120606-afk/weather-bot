import os
import requests
import json
import datetime
import sys

# === 🛠️ 設定情報 ===
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')

# 八潮市の場所データ
LAT = "35.8217"
LON = "139.8444"

# 🌤️ 絵文字辞書
WEATHER_EMOJI = {
    0: "☀️ 晴れ", 1: "🌤️ ほぼ晴れ", 2: "⛅ 時々曇り", 3: "☁️ 曇り",
    45: "🌫️ 霧", 48: "🌫️ 霧", 51: "🌦️ 小雨", 53: "🌦️ 小雨", 55: "🌦️ 小雨",
    61: "🌧️ 雨", 63: "🌧️ 雨", 65: "🌧️ 激しい雨", 71: "❄️ 雪", 73: "❄️ 雪",
    75: "❄️ 豪雪", 80: "🌦️ にわか雨", 81: "🌧️ にわか雨", 82: "🌧️ 激しいにわか雨", 95: "⚡ 雷雨",
}

def get_weather_emoji(code):
    return WEATHER_EMOJI.get(code, "❓ 不明")

try:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&minutely_15=temperature_2m,precipitation_probability,weather_code&timezone=Asia%2FTokyo"
    response = requests.get(url).json()
    min_data = response["minutely_15"]
    times, temps, probs, codes = min_data["time"], min_data["temperature_2m"], min_data["precipitation_probability"], min_data["weather_code"]

    JST = datetime.timezone(datetime.timedelta(hours=+9))
    now = datetime.datetime.now(JST).replace(tzinfo=None)
    
    print(f" ➔ 現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    pop_text = ""
    max_temp = -100
    max_prob = 0
    count = 0

    for i in range(len(times)):
        data_time = datetime.datetime.strptime(times[i], "%Y-%m-%dT%H:%M")
        if data_time >= now and data_time.minute in [0, 30]:
            time_label = data_time.strftime("%H:%M")
            emoji = get_weather_emoji(codes[i])
            temp, prob = temps[i], probs[i]
            
            pop_text += f"🕒 {time_label} ➔ {emoji} | {temp}°C | ☔ {prob}%\n"
            if temp > max_temp: max_temp = temp
            if prob > max_prob: max_prob = prob
            
            count += 1
            if count >= 10: break

    # 💡 アドバイス作成
    advice = "🧥【お出かけアドバイス】\n"
    if max_temp < 15: advice += "・少し肌寒いです。上着を持って出かけましょう。\n"
    elif max_temp < 25: advice += "・過ごしやすい気温ですが、念のため羽織るものがあると安心です。\n"
    else: advice += "・暑いです。熱中症に気をつけて、こまめに水分補給を！\n"
    
    advice += "🌂【傘の備え】: "
    advice += "必要です！" if max_prob >= 30 else "今のところ傘は不要です。"

    message_text = f"📢【八潮市のピンポイント天気】\n(今後5時間・30分刻み)\n\n{pop_text}\n{advice}"

    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message_text}]}
    requests.post(line_url, headers=headers, data=json.dumps(payload))

except Exception as e:
    print(f"エラー: {e}")
