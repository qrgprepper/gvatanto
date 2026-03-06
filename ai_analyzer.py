# Métodos helper para manter compatibilidade com o main.py antigo
from ai.analyzer.ai_analyzer_factory import AIAnalyzerFactory


def analyze_risk(text):
    provider = AIAnalyzerFactory.get_provider()
    result = provider.analyze(text)
    if not result:
        return {"nivel_risco": "AMARELO", "resumo_tatico": "Erro na análise. Verifique o motor de IA."}
    return result

def generate_sitrep(summaries):
    provider = AIAnalyzerFactory.get_provider()
    return provider.synthesize(summaries)
