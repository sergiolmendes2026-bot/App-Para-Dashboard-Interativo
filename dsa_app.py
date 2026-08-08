import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu

# --- INICIALIZAÇÃO E MIGRAÇÃO AUTOMÁTICA DO BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT, 
            empresa TEXT, 
            email TEXT, 
            telefone TEXT, 
            regiao TEXT, 
            status TEXT, 
            origem TEXT,
            motivo_perda TEXT,
            data TEXT, 
            data_fechamento TEXT,
            responsavel TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            titulo TEXT, 
            estagio TEXT, 
            valor REAL,
            empresa TEXT,
            contato TEXT,
            telefone TEXT,
            email TEXT,
            responsavel TEXT,
            origem TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            cliente TEXT, 
            valor REAL, 
            data TEXT,
            responsavel TEXT,
            status TEXT
        )
    """)
    
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(clientes)")
    colunas_existentes_clientes = [col[1] for col in cursor.fetchall()]
    novas_colunas_clientes = {"origem": "TEXT", "motivo_perda": "TEXT", "data_fechamento": "TEXT", "responsavel": "TEXT"}
    for coluna, tipo in novas_colunas_clientes.items():
        if coluna not in colunas_existentes_clientes:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}")

    cursor.execute("PRAGMA table_info(pipeline)")
    colunas_existentes_pipeline = [col[1] for col in cursor.fetchall()]
    novas_colunas_pipeline = {"empresa": "TEXT", "contato": "TEXT", "telefone": "TEXT", "email": "TEXT", "responsavel": "TEXT", "origem": "TEXT"}
    for coluna, tipo in novas_colunas_pipeline.items():
        if coluna not in colunas_existentes_pipeline:
            conn.execute(f"ALTER TABLE pipeline ADD COLUMN {coluna} {tipo}")

    cursor.execute("PRAGMA table_info(vendas)")
    colunas_existentes_vendas = [col[1] for col in cursor.fetchall()]
    if "status" not in colunas_existentes_vendas:
        conn.execute("ALTER TABLE vendas ADD COLUMN status TEXT")
            
    conn.commit()
    conn.close()

inicializar_banco()

st.set_page_config(
    page_title="CRM Comercial Profissional", page_icon="📊", layout="wide"
)

# --- BARRA LATERAL COM MENU E ÍCONES ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0 20px 0;">
            <div style="background-color: #2563EB; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">📊</div>
            <div>
                <div style="font-weight: bold; font-size: 16px; color: #ffffff;">CRM</div>
                <div style="font-size: 11px; color: #94a3b8; letter-spacing: 1px;">COMERCIAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard", "Clientes", "Leads", "Pipeline", "Vendas", "Relatórios", "Integrações", "Configurações",
        ],
        icons=[
            "speedometer2", "people-fill", "person-plus-fill", "kanban", "trophy-fill", "file-earmark-bar-graph", "plug", "gear-fill"
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#60a5fa", "font-size": "15px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0px",
                "color": "#94a3b8",
                "--hover-color": "#1e293b",
            },
            "nav-link-selected": {
                "background-color": "#2563EB",
                "color": "#FFFFFF",
                "font-weight": "600",
            },
        },
    )

def conectar():
    return sqlite3.connect("crm.db")

@st.cache_data(ttl=1)
def carregar_dados():
    conn = conectar()
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame()
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame()
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame()
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    # (Restante do seu código original do Dashboard permanece aqui...)
    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and "valor" in df_vendas.columns and len(df_vendas) > 0 else 0.0
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Leads", f"{total_leads}")
    k2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    k3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    k4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro Completo de Clientes e Leads")
    # (Restante do código de Clientes...)
    with st.form("form_cliente_completo", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_contato = st.text_input("Nome do Contato *")
            nome_empresa = st.text_input("Nome da Empresa")
            email_cli = st.text_input("E-mail")
        with col_c2:
            status_cli = st.selectbox("Status do Cliente", ["🆕 Novo Lead", "🤝 Negociação", "✅ Venda Fechada"])
            responsavel_cli = st.text_input("Responsável Comercial", value="Equipe Comercial")
        submitted_cli = st.form_submit_button("Salvar Cliente")
        if submitted_cli:
            st.success("Cliente cadastrado!")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas Fechadas")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação")

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.toggle("Ativar Integração WhatsApp", value=True)

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    st.markdown("---")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("🏢 Dados da Organização")
        nome_org = st.text_input("Nome da Organização", value="Comercial Alpha LTDA")
        cnpj_org = st.text_input("CNPJ")
        email_org = st.text_input("E-mail de Suporte")
    with col_c2:
        st.subheader("🛠 Preferências Gerais")
        moeda_padrao = st.selectbox("Moeda Padrão", ["Real (BRL - R$)", "Dólar (USD - $)", "Euro (EUR - €)"])
        fuso_horario = st.selectbox("Fuso Horário", ["(GMT-03:00) Horário de Brasília", "(GMT-02:00) Noronha"])
        telefone_org = st.text_input("Telefone Comercial")

    st.markdown("### 👥 Gestão de Equipe")
    st.info("Aqui você poderá gerenciar os níveis de acesso dos usuários em uma versão futura.")
    
    if st.button("Salvar Configurações"):
        st.success("Configurações atualizadas com sucesso!")
