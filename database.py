import sqlite3

def conectar():
    return sqlite3.connect("crm_vendas.db")

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            empresa TEXT,
            email TEXT,
            telefone TEXT,
            regiao TEXT,
            data_cadastro TEXT
        )
    ''')
    
    # Tabela de Pipeline
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            titulo TEXT,
            estagio TEXT,
            valor REAL
        )
    ''')
    
    # Tabela de Interações com a coluna 'cliente'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            tipo TEXT,
            descricao TEXT
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            produto_servico TEXT,
            valor REAL,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
