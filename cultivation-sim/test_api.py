import requests
import json

url = "http://localhost:8001/game/new"
data = {
    "player_name": "Test Player",
    "character_data": {
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên"
    }
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
