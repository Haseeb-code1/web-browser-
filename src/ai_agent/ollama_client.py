import requests
import json
from src.utils.exception_logger import log_exception

class OllamaClient:
    OLLAMA_URL = "http://localhost:11434"
    OLLAMA_MODEL = "phi3:mini"
    @classmethod
    def check_ollama_running(cls) -> bool:
        try:
            res = requests.get(f"{cls.OLLAMA_URL}/api/tags", timeout=2)
            return res.status_code == 200
        except:
            return False
            
    @classmethod
    def generate(cls, messages: list, model_choice: str = "auto") -> str:
        # Route to Groq if selected or Auto and Ollama offline
        if model_choice == "groq" or (model_choice == "auto" and not cls.check_ollama_running()):
            import json
            from src.utils.paths import get_data_file_path
            import os
            try:
                with open(get_data_file_path("config.json"), "r") as f:
                    cfg = json.load(f)
                    key = cfg.get("groq_api_key", "")
                    model = cfg.get("groq_model", "llama-3.3-70b-versatile")
            except:
                key = ""
                model = "llama-3.3-70b-versatile"
            
            key = key or os.getenv("GROQ_API_KEY", "")
                
            if key:
                try:
                    payload = {"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 1024}
                    res = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                        json=payload, timeout=60
                    )
                    if res.status_code == 200:
                        return res.json()["choices"][0]["message"]["content"]
                    else:
                        import json as temp_json
                        err_msg = temp_json.dumps(f"Groq API Error {res.status_code}: {res.text}")
                        return f'{{"tool": "answer", "params": {{"message": {err_msg}}}}}'
                except Exception as e:
                    import json as temp_json
                    err_msg = temp_json.dumps(f"Groq API unreachable ({str(e)})")
                    return f'{{"tool": "answer", "params": {{"message": {err_msg}}}}}'

        # 1. Try Pollinations.ai (Online) directly to save time
                
        # 2. Fallback to Ollama (Offline / Local)
        if not cls.check_ollama_running():
            return '{"tool": "answer", "params": {"message": "You are offline and Ollama was not detected. Please connect to the internet or run: ollama serve"}}'
            
        try:
            payload = {
                "model": cls.OLLAMA_MODEL,
                "stream": False,
                "messages": messages,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 4096
                }
            }
            # Local AI can be slow, using timeout=None
            res = requests.post(f"{cls.OLLAMA_URL}/api/chat", json=payload, timeout=None)
            if res.status_code == 200:
                data = res.json()
                return data["message"]["content"]
            else:
                return f'{{"tool": "answer", "params": {{"message": "Ollama Error: {res.status_code}"}}}}'
        except Exception as e:
            log_exception(e)
            return f'{{"tool": "answer", "params": {{"message": "Ollama Exception: {str(e)}"}}}}'
