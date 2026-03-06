FROM python:3.12-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias para compilar algumas libs se necessário
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Garante que o diretório de dados existe para o SQLite
RUN mkdir -p /app/data

# Comando padrão (ajustável via docker-compose ou docker run)
CMD ["python", "main.py", "--help"]
