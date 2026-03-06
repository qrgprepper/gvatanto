import json
import re


def extract_json(text):
    """Fallback robusto para extrair JSON de respostas verbosas de IAs locais."""
    try:
        # Tenta encontrar o bloco JSON entre chaves
        match = re.search(r'({.*})', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except Exception:
        return None