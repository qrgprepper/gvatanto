# Gvatanto - Inteligência Tática para Sobrevivencialismo

O **Gvatanto** (Esperanto para "Aquele que vigia" ou "Observador") é um sistema de monitoramento de fontes abertas (OSINT) projetado para fornecer inteligência estratégica e análise de risco em tempo real. Utilizando a API do Google Gemini, o sistema filtra o ruído de feeds RSS globais e entrega diagnósticos acionáveis focados em resiliência e segurança física.

## 🚀 Funcionalidades Principais

- **Motor de Scan Inteligente**: Coleta e analisa notícias de múltiplas fontes RSS simultaneamente.
- **Análise Cognitiva (IA)**: Classifica riscos (Verde, Amarelo, Laranja, Vermelho) e gera resumos táticos frios e diretos.
- **Gestão de Fontes via CLI**: Adicione ou remova feeds RSS diretamente pelo terminal, sem editar arquivos.
- **Relatórios Situacionais (SitRep)**: IA sintetiza alertas das últimas 24/48h para identificar padrões de crise e recomendar ações.
- **Persistência Robusta**: Banco de dados SQLite com controle de estado (lido/não lido) e histórico de análises.
- **Interface de Terminal Avançada**: Tabelas e painéis formatados com a biblioteca `rich`.

## 🛠️ Pré-requisitos

- Python 3.10+
- Chave de API do [Google Gemini](https://aistudio.google.com/) configurada como variável de ambiente `GEMINI_API_KEY`.

## 📦 Instalação

```bash
# Clone o repositório
pip install -r requirements.txt
```

## ⚙️ Guia de Comandos (CLI)

O Gvatanto opera através de subcomandos modulares:

### 1. Gestão de Fontes (`source`)
Gerencie quais sites o sistema deve monitorar.
- **Adicionar fonte**: `python main.py source add "URL_RSS" --nome "Nome da Fonte"`
- **Listar fontes**: `python main.py source list`
- **Remover fonte**: `python main.py source remove <ID>`

### 2. Monitoramento e Scan (`scan`)
Busca novas notícias e gera inteligência.
- **Executar Scan**: `python main.py scan`

### 3. Consulta de Alertas (`list`, `show`, `open`)
Revise o que foi capturado.
- **Listar alertas**: `python main.py list` (Flags: `--unread`, `--nivel`, `--limit`)
- **Ver detalhes**: `python main.py show <ID>` (Exibe conteúdo completo e marca como lido)
- **Abrir link**: `python main.py open <ID>` (Abre a fonte original no navegador)

### 4. Inteligência Estratégica (`sitrep`)
Diagnóstico agregado sobre o estado atual.
- **Gerar SitRep**: `python main.py sitrep` (Analisa alertas das últimas 24h)
- **Ver histórico**: `python main.py sitrep --history`

## 📂 Estrutura do Banco de Dados
O sistema utiliza um schema resiliente com três tabelas principais:
- `source`: Cadastro de feeds monitorados.
- `alert`: Alertas processados com nível de risco e resumo tatico.
- `sitrep`: Histórico de diagnósticos estratégicos agregados.

---
*Focado em resiliência, soberania de informação e prontidão.*
