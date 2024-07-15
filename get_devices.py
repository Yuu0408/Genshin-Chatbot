import json
import requests
from cloud_api import create_header
from setup import YOUR_SWITCHBOT_TOKEN, YOUR_SWITCHBOT_CLIENT_SECRET

header = create_header(YOUR_SWITCHBOT_TOKEN, YOUR_SWITCHBOT_CLIENT_SECRET)

def get_devices():
    url = 'https://api.switch-bot.com/v1.1/devices'
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        data = response.json()
        # Extract the infraredRemoteList from the response
        if 'body' in data and 'infraredRemoteList' in data['body']:
            return data['body']['infraredRemoteList']
        else:
            return []  # Return an empty list if the specific key is not found
    else:
        return {"Error": f"{response.status_code}, {response.text}"}
    
infrared_devices_list = get_devices()

with open('data/devices.txt', 'w', encoding='utf-8') as f:
    # Convert the list of devices to a JSON formatted string with proper encoding
    f.write(json.dumps(infrared_devices_list, ensure_ascii=False, indent=4))