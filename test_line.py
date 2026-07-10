import os
import requests

# Secretsから読み込み
LINE_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('GROUP_ID')

def send_test():
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": "テスト送信です。届いたら成功！"}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    # 応答の中身を表示（これが重要！）
    print(f"ステータスコード: {response.status_code}")
    print(f"サーバーの応答: {response.text}")

if __name__ == "__main__":
    send_test()
