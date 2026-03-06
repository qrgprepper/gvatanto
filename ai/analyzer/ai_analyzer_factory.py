import os
from dotenv import load_dotenv

from ai.providers.gemini_provider import GeminiProvider
from ai.providers.ollama_provider import OllamaProvider
from ai.providers.openai_provider import OpenAIProvider

load_dotenv()
# Configurações padrão via Variáveis de Ambiente
DEFAULT_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
DEFAULT_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")

class AIAnalyzerFactory:
    _instance = None

    @staticmethod
    def get_provider():
        if AIAnalyzerFactory._instance is not None:
            return AIAnalyzerFactory._instance

        provider_type = DEFAULT_PROVIDER.lower()
        model_name = DEFAULT_MODEL
        
        if provider_type == "gemini":
            AIAnalyzerFactory._instance = GeminiProvider(os.environ.get("AI_API_KEY"), model_name)
        elif provider_type == "openai":
            AIAnalyzerFactory._instance = OpenAIProvider(os.environ.get("AI_API_KEY"), model_name)
        elif provider_type == "ollama":
            url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
            AIAnalyzerFactory._instance = OllamaProvider(url, model_name)
        else:
            raise ValueError(f"Provedor {provider_type} desconhecido.")
            
        return AIAnalyzerFactory._instance