import json
from openai import OpenAI
from ai.instructions.instructions import SYSTEM_INSTRUCTION
from ai.providers.llm_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, model_name):
        self.client = OpenAI(api_key=api_key)
        self.model = model_name

    def analyze(self, text):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"Notícia: {text}"}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)

    def synthesize(self, summaries):
        combined = "\n".join([f"- {s}" for s in summaries])
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"Gere um SitRep para:\n{combined}"}]
        )
        return response.choices[0].message.content