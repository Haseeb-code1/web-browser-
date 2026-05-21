import ollama
from typing import Optional
from src.utils.exception_logger import log_exception
from src.aiengine.prompts import AIPrompts

class AIEngine:
    """Interface for local AI analysis using Ollama and Phi-3 Mini."""
    
    def __init__(self, model_name: str = "phi3"):
        self.model_name = model_name

    def _generate(self, prompt: str) -> str:
        """Helper to send prompt to Ollama."""
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {"role": "user", "content": prompt}
            ])
            return response['message']['content']
        except Exception as e:
            log_exception(e)
            return f"Error communicating with local AI: {str(e)}\nMake sure Ollama is installed and running."

    def summarize_page(self, title: str, content: str) -> str:
        """Ask AI to summarize a webpage."""
        prompt = AIPrompts.SUMMARIZE_PAGE.format(title=title, content=content)
        return self._generate(prompt)

    def explain_code(self, code_snippet: str) -> str:
        """Ask AI to explain a code snippet."""
        prompt = AIPrompts.EXPLAIN_CODE.format(code_snippet=code_snippet)
        return self._generate(prompt)
