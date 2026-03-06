import os
import sqlite3
from datetime import datetime

# Caminho do banco de dados configurável via variável de ambiente
DB_PATH = os.environ.get("GVATANTO_DB_PATH", "gvatanto.db")

def setup_database(db_name=DB_PATH):
    """Cria as tabelas de alertas e fontes se não existirem e atualiza estrutura."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Tabela de Fontes (Sources)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                url TEXT UNIQUE,
                ativo INTEGER DEFAULT 1
            )
        ''')

        # Tabela de SitReps (Histórico de Relatórios)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sitreps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_geracao DATETIME,
                periodo_horas INTEGER,
                conteudo TEXT
            )
        ''')

        # Tabela de Alertas com novos campos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_coleta DATETIME,
                source_id INTEGER,
                fonte TEXT,
                titulo TEXT,
                link TEXT UNIQUE,
                nivel_risco TEXT,
                resumo_tatico TEXT,
                full_content TEXT,
                read_status INTEGER DEFAULT 0,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        ''')
        
        # Migração simples: Adiciona colunas se estiverem faltando (para bancos já criados)
        cursor.execute("PRAGMA table_info(alertas)")
        columns = [col[1] for col in cursor.fetchall()]
        if "source_id" not in columns:
            cursor.execute("ALTER TABLE alertas ADD COLUMN source_id INTEGER")
        if "full_content" not in columns:
            cursor.execute("ALTER TABLE alertas ADD COLUMN full_content TEXT")
        if "read_status" not in columns:
            cursor.execute("ALTER TABLE alertas ADD COLUMN read_status INTEGER DEFAULT 0")

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")

# --- Funções de Alertas ---

def link_exists(link, db_name=DB_PATH):
    """Verifica se um link já foi processado."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM alertas WHERE link = ?", (link,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except sqlite3.Error as e:
        print(f"Erro ao verificar duplicidade: {e}")
        return False

def save_alerta(source_id, fonte, titulo, link, nivel_risco, resumo_tatico, full_content, db_name=DB_PATH):
    """Salva um novo alerta no banco de dados."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO alertas (data_coleta, source_id, fonte, titulo, link, nivel_risco, resumo_tatico, full_content, read_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (data_coleta, source_id, fonte, titulo, link, nivel_risco, resumo_tatico, full_content))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao salvar alerta: {e}")

def get_alerts(limit=10, nivel=None, only_unread=False, db_name=DB_PATH):
    """Busca alertas com filtros de nível e status de leitura."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        query = "SELECT id, data_coleta, nivel_risco, titulo, read_status FROM alertas WHERE 1=1"
        params = []

        if nivel:
            query += " AND nivel_risco = ?"
            params.append(nivel.upper())
        if only_unread:
            query += " AND read_status = 0"
        
        query += " ORDER BY data_coleta DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Erro ao buscar alertas: {e}")
        return []

def get_alert_by_id(alert_id, db_name=DB_PATH):
    """Retorna os dados completos de um alerta pelo ID."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, data_coleta, fonte, titulo, link, nivel_risco, resumo_tatico, full_content, read_status 
            FROM alertas WHERE id = ?
        ''', (alert_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Erro ao buscar alerta por ID: {e}")
        return None

def mark_as_read(alert_id, db_name=DB_PATH):
    """Marca um alerta como lido."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE alertas SET read_status = 1 WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao marcar como lido: {e}")
        return False

def get_recent_alerts(hours=24, db_name=DB_PATH):
    """Busca resumos táticos recentes para o SitRep."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        from datetime import timedelta
        limit_time = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT resumo_tatico, nivel_risco FROM alertas WHERE data_coleta >= ?", (limit_time,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Erro ao buscar alertas recentes: {e}")
        return []

# --- Funções de SitRep ---

def save_sitrep(periodo_horas, conteudo, db_name=DB_PATH):
    """Salva um relatório situacional no banco de dados."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        data_geracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO sitreps (data_geracao, periodo_horas, conteudo)
            VALUES (?, ?, ?)
        ''', (data_geracao, periodo_horas, conteudo))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar SitRep: {e}")
        return False

def get_latest_sitreps(limit=5, db_name=DB_PATH):
    """Busca os últimos SitReps gerados."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, data_geracao, periodo_horas, conteudo FROM sitreps ORDER BY data_geracao DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Erro ao buscar SitReps: {e}")
        return []

# --- Funções de Sources (CRUD) ---

def insert_source(nome, url, db_name=DB_PATH):
    """Adiciona uma nova fonte de feed."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sources (nome, url) VALUES (?, ?)", (nome, url))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        print(f"Erro ao inserir fonte: {e}")
        return False

def get_active_sources_info(db_name=DB_PATH):
    """Retorna IDs e URLs das fontes ativas."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, url FROM sources WHERE ativo = 1")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Erro ao buscar fontes ativas: {e}")
        return []

def get_all_sources(db_name=DB_PATH):
    """Retorna todas as fontes (ativas e inativas)."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, url, ativo FROM sources")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Erro ao buscar fontes: {e}")
        return []

def remove_source(source_id, db_name=DB_PATH):
    """Remove uma fonte do banco de dados pelo ID."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        conn.commit()
        exists = cursor.rowcount > 0
        conn.close()
        return exists
    except sqlite3.Error as e:
        print(f"Erro ao remover fonte: {e}")
        return False
