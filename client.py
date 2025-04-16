import base64
import json
import requests

# Path to your audio file
audio_file_path = 'test.wav'

# Read and encode the audio file
with open(audio_file_path, 'rb') as audio_file:
    encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

# Prepare the JSON payload
payload = {
    'title': 'This problem is really complicated.',
    'base64Audio': f'data:audio/wav;base64,{encoded_audio}',
    'language': 'en'
}

# Send the POST request
url = 'http://localhost:8080/GetAccuracyFromRecordedAudio'  # Change if needed
headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(payload), headers=headers)

# Print the response
print(f"Status code: {response.status_code}")
print("Response:")

parsed = json.loads(response.text)
for key, value in parsed.items():
    print(f"{key}: {value}")
