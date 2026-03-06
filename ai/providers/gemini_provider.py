from ai.providers.llm_provider import LLMProvider
from ai.util.extract_json import extract_json
from ai.instructions.instructions import SYSTEM_INSTRUCTION
from google.genai import Client


class GeminiProvider(LLMProvider):
    """Implementação usando o novo SDK oficial google-genai."""
    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model = model_name
        self.client = Client(api_key=self.api_key)

    def analyze(self, text):
        prompt = f"{SYSTEM_INSTRUCTION}\n\nNotícia: {text}"
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return extract_json(response.text)

    def synthesize(self, summaries):
        combined = "\n".join([f"- {s}" for s in summaries])
        prompt = f"Analise estes resumos táticos e gere um SitRep (Diagnóstico e Ações Recomendadas):\n{combined}"
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text