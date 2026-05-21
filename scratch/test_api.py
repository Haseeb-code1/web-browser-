import requests
import json

payload = {
    "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "hello"}],
    "model": "openai"
}
try:
    res = requests.post("https://text.pollinations.ai/openai", json=payload, timeout=20)
    print("Status:", res.status_code)
    data = res.json()
    print("Response JSON:", json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)
