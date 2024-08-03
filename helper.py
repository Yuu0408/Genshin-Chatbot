import json

# Helper functions
def read_device(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:  # Specify encoding here
        content = file.read()
    return json.loads(content)

def get_device_id(device):
    devices = read_device('data/devices.txt')
    for controller in devices:
        if controller["remoteType"] == device:
            return controller["deviceId"]
    return None

def can_be_encoded_cp932(char):
    try:
        char.encode('cp932')
        return True
    except UnicodeEncodeError:
        return False

labels_to_emotions = {
  'LABEL_0': 'anger',
 'LABEL_1': 'disgust',
 'LABEL_2': 'fear',
 'LABEL_3': 'joy',
 'LABEL_4': 'love',
 'LABEL_5': 'sadness',
 'LABEL_6': 'surprise',
 'LABEL_7': 'neutral'
 }
