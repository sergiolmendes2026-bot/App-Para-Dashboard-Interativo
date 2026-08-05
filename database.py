import sqlite3
import pandas as pd

DB_NAME = "crm_database.db"

def conectar():
    """Cria e retorna a conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def inicializar_banco():
    """Cria as tabelas necessárias para o CRM caso elas não existam."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Tabela de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            empresa TEXT,
            email TEXT,
            telefone TEXT,
            regiao TEXT,
            data_cadastro TEXT
        )
    """)

    # 2. Tabela de Pipeline (Funil de Vendas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            titulo_negocio TEXT NOT NULL,
            valor REAL,
            etapa TEXT,  -- Ex: Prospecção, Qualificação, Proposta, Fechado, Perdido
            responsavel TEXT,
            data_criacao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    """)

    # 3. Tabela de Interações (Histórico de Atividades)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            tipo TEXT,  -- Ex: Ligação, Reunião, WhatsApp, E-mail
            descricao TEXT,
            data_interacao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    """)

    # 4. Tabela de Vendas Concluídas (Alimenta o seu Dashboard Analítico)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            produto TEXT,
            categoria TEXT,
            quantidade INTEGER,
            faturamento REAL,
            data_venda TEXT,
            regiao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados e tabelas criados com sucesso!")
