import requests
from ai.instructions.instructions import SYSTEM_INSTRUCTION
from ai.providers.llm_provider import LLMProvider
from ai.util.extract_json import extract_json


class OllamaProvider(LLMProvider):
    def __init__(self, url, model_name):
        self.url = f"{url}/api/generate"
        self.model = model_name

    def analyze(self, text):
        prompt = f"{SYSTEM_INSTRUCTION}\n\nNotícia: {text}"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(self.url, json=payload)
        return extract_json(response.json().get("response", "{}"))

    def synthesize(self, summaries):
        combined = "\n".join([f"- {s}" for s in summaries])
        prompt = f"Gere um SitRep (Diagnóstico e Ações Recomendadas):\n{combined}"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        response = requests.post(self.url, json=payload)
        return response.json().get("response", "Erro ao processar.")