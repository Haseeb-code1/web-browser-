import os
import json
import requests
from typing import Generator

class GroqNotConfiguredError(Exception):
    """Raised when no Groq API key is configured."""
    pass

class GroqAPIError(Exception):
    """Raised when the Groq API returns an error or a network issue occurs."""
    pass

from src.utils.paths import get_data_file_path

def _load_key_from_config() -> str:
    """Read groq_api_key from data/config.json if it exists."""
    try:
        with open(get_data_file_path("config.json"), "r") as f:
            cfg = json.load(f)
            return cfg.get("groq_api_key", "")
    except Exception:
        return ""

def _load_model_from_config() -> str:
    """Read groq_model from config, default to a supported Llama model."""
    try:
        with open(get_data_file_path("config.json"), "r") as f:
            cfg = json.load(f)
            return cfg.get("groq_model", "llama-3.3-70b-versatile")
    except Exception:
        return "llama-3.3-70b-versatile"

class GroqClient:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str = None):
        # Environment variable overrides config file
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "") or _load_key_from_config()
        self.model = _load_model_from_config()

    def check_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _payload(self, prompt: str, stream: bool = False, context: str = "") -> dict:
        """Construct the request payload.
        * ``prompt`` – user query.
        * ``stream`` – whether we request a streaming response.
        * ``context`` – optional system message providing additional context.
        """
        messages = [{"role": "user", "content": prompt}]
        if context:
            messages.insert(0, {"role": "system", "content": context})
        return {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024,
            "stream": stream,
        }

    def stream(self, prompt: str, context: str = "") -> Generator[str, None, None]:
        """Yield streamed response chunks from Groq API."""
        if not self.check_configured():
            raise GroqNotConfiguredError(
                "Add your Groq API key in Settings → AI → Groq API Key"
            )
        payload = self._payload(prompt, stream=True, context=context)
        try:
            with requests.post(
                self.API_URL,
                headers=self._headers(),
                json=payload,
                stream=True,
                timeout=60,
            ) as response:
                if response.status_code != 200:
                    try:
                        err_msg = response.json().get("error", {}).get("message", response.text)
                    except Exception:
                        err_msg = response.text
                    raise GroqAPIError(
                        f"Groq API error {response.status_code}: {err_msg}"
                    )
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    if line == "[DONE]":
                        break
                    try:
                        data = json.loads(line)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except json.JSONDecodeError:
                        continue
        except requests.RequestException as e:
            raise GroqAPIError(f"Network error while contacting Groq: {e}")
