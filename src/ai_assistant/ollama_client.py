import requests
import json
from typing import Generator

class OllamaClient:
    OLLAMA_URL = "http://localhost:11434"
    
    def __init__(self, ollama_url: str = None):
        if ollama_url:
            self.OLLAMA_URL = ollama_url

    def check_running(self) -> bool:
        try:
            res = requests.get(f"{self.OLLAMA_URL}/api/tags", timeout=2)
            return res.status_code == 200
        except:
            return False

    def stream(self, prompt: str) -> Generator[str, None, None]:
        if not self.check_running():
            yield "Ollama is not running. Start Ollama and download phi3:mini."
            return
            
        payload = {
            "model": "phi3:mini",
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.3, "num_ctx": 2048}
        }
        
        try:
            res = requests.post(f"{self.OLLAMA_URL}/api/generate", json=payload, stream=True, timeout=45)
            res.raise_for_status()
            
            for line in res.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        if data.get("response"):
                            yield data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f"Error streaming from Ollama: {str(e)}"
