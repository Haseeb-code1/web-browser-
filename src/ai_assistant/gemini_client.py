import os
import json
import requests
from typing import Generator

class GeminiNotConfiguredError(Exception):
    pass

class GeminiClient:
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    STREAM_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
            
    def check_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def _get_headers(self):
        return {"Content-Type": "application/json"}

    def _get_payload(self, prompt: str) -> dict:
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
                "topP": 0.8
            }
        }

    def ask(self, prompt: str) -> str:
        if not self.check_configured():
            raise GeminiNotConfiguredError("Add your Gemini API key in Settings → AI → Gemini API Key")
            
        url = f"{self.API_URL}?key={self.api_key}"
        payload = self._get_payload(prompt)
        
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Error parsing response from Gemini."

    def stream(self, prompt: str) -> Generator[str, None, None]:
        if not self.check_configured():
            yield "Add your Gemini API key in Settings → AI → Gemini API Key"
            return
            
        url = f"{self.STREAM_URL}?alt=sse&key={self.api_key}"
        payload = self._get_payload(prompt)
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload, stream=True, timeout=30)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        json_str = decoded[6:]
                        if json_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(json_str)
                            text = data["candidates"][0]["content"]["parts"][0]["text"]
                            yield text
                        except (KeyError, IndexError, json.JSONDecodeError):
                            continue
        except Exception as e:
            yield f"Error streaming from Gemini: {str(e)}"
