from typing import Generator
from src.ai_assistant.groq_client import GroqClient
from src.ai_assistant.ollama_client import OllamaClient

SYSTEM_PROMPT = """
You are a fast, helpful AI assistant built into a web browser.
You can control the browser and help users with web tasks.

Browser actions you can trigger (include these in your response when relevant):
- [OPEN: url] — opens a website
- [SEARCH: query] — searches Google
- [CLOSE TAB] — closes current tab
- [NEW TAB] — opens new tab
- [SCROLL DOWN] — scrolls the page

Rules:
1. Be concise and fast. Lead with the answer, not the explanation.
2. If the user asks to open a site, include [OPEN: url] in your response.
3. If you mention URLs, format them as clickable: [Title](url)
4. For page summaries, use bullet points.
5. For comparisons, use a short table.
6. Never say "As an AI language model..." — just answer directly.
7. Response max length: 300 words unless user asks for more.
"""

class ModelRouter:
    def __init__(self, groq_client: GroqClient, ollama_client: OllamaClient):
        self.selected_model: str = "auto"
        self.groq_client = groq_client
        self.ollama_client = ollama_client

    def ask(self, prompt: str, context: str = "") -> Generator[str, None, None]:
        full_prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser: {prompt}" if context else f"{SYSTEM_PROMPT}\n\nUser: {prompt}"
        
        if self.selected_model == "groq":
            yield from self.groq_client.stream(full_prompt)
        elif self.selected_model == "phi3":
            yield from self.ollama_client.stream(full_prompt)
        elif self.selected_model == "auto":
            if self.ollama_client.check_running():
                yield from self.ollama_client.stream(full_prompt)
            else:
                yield from self.groq_client.stream(full_prompt)

    def set_model(self, model: str):
        self.selected_model = model

    def get_available_models(self) -> list[str]:
        available = ["auto"]
        if self.ollama_client.check_running():
            available.append("phi3")
        if self.groq_client.check_configured():
            available.append("groq")
        return available
