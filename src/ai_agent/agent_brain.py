import json
import re
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from src.ai_agent.ollama_client import OllamaClient
from src.ai_agent.action_executor import ActionExecutor
from src.ai_agent.tool_definitions import SYSTEM_PROMPT
from PyQt6.QtWebEngineWidgets import QWebEngineView

class AgentWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, messages, model_choice="auto"):
        super().__init__()
        self.messages = messages
        self.model_choice = model_choice
        
    def run(self):
        response_text = OllamaClient.generate(self.messages, self.model_choice)
        self.finished.emit(response_text)

class AgentBrain(QObject):
    def __init__(self, web_view: QWebEngineView, ui_callback, model_choice="auto"):
        super().__init__()
        self.executor = ActionExecutor(web_view)
        self.ui_callback = ui_callback
        self.model_choice = model_choice
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.worker = None
        self.step_count = 0
        
    def start_task(self, task: str):
        self.step_count = 0
        self.ui_callback(f"<br><b>You:</b> {task}")
        self.messages.append({"role": "user", "content": task})
        self._step()
        
    def _step(self):
        self.step_count += 1
        self.ui_callback("<br><i>Agent is thinking...</i>")
        self.worker = AgentWorker(self.messages, self.model_choice)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()
        
    def _on_worker_finished(self, response_text: str):
        # Try to parse JSON tool call
        try:
            clean_text = response_text.strip()
            
            # Try to extract JSON block using regex
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', clean_text, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                # Fallback: Find the first { and last }
                start_idx = clean_text.find('{')
                end_idx = clean_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = clean_text[start_idx:end_idx+1]
                else:
                    json_str = clean_text
            
            tool_call = json.loads(json_str)
            tool_name = tool_call.get("tool")
            
            self.messages.append({"role": "assistant", "content": clean_text})
            
            if not tool_name:
                # The AI generated JSON, but it didn't have a 'tool' key.
                # This often happens if the AI hallucinates or Pollinations returns an error JSON.
                # Just print the raw text and stop to prevent infinite error loops.
                self.ui_callback(f"<br><b style='color:#00f0ff;'>Agent:</b> {clean_text}")
                return
            
            if tool_name == "answer":
                ans = tool_call.get("params", {}).get("message", "")
                self.ui_callback(f"<br><b style='color:#00f0ff;'>Agent:</b> {ans}")
                return # Task complete
            
            # Execute tool
            self.ui_callback(f"<br><i style='color:#a855f7;'>Executing: {tool_name}...</i>")
            result = self.executor.execute(tool_call)
            
            self.messages.append({"role": "user", "content": f"Tool '{tool_name}' result: {result}"})
            
            # Recurse
            if self.step_count < 10:
                self._step()
            else:
                self.ui_callback("<br><b style='color:#ef4444;'>Agent stopped (max steps reached).</b>")
            
        except json.JSONDecodeError:
            # Not valid JSON, meaning it answered normally or hallucinated
            self.ui_callback(f"<br><b style='color:#00f0ff;'>Agent:</b> {response_text}")
            self.messages.append({"role": "assistant", "content": response_text})
