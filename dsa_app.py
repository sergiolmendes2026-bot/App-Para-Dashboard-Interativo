import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(
    page_title="CRM Pro - Workspace v2.0", page_icon="📊", layout="wide" 
)

# --- INICIALIZAÇÃO DO ESTADO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro"
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

cor_hex = "#2563EB"
is_escuro = "Escuro" in st.session_state.tema_sistema

bg_app = "#0e1117" if is_escuro else "#ffffff"
text_app = "#ffffff" if is_escuro else "#1e293b"
sidebar_bg = "#0b0f19" if is_escuro else "#f8fafc"

# --- CSS GLOBAL ---
st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_app}; color: {text_app}; }}
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg}; 
            border-right: 1px solid #1e293b;
            padding-top: 10px;
        }}
        h1, h2, h3, h4 {{ color: {text_app}; }}
        
        [data-testid="stSidebar"] button div p {{
            font-size: 15px !important;
            font-weight: 600 !important;
        }}

        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; 
            text-align: left; 
            background-color: transparent !important;
            color: #f1f5f9 !important; 
            border: none !important; 
            border-radius: 8px !important;
            padding: 6px 10px !important; 
            margin-bottom: 2px;
            transition: all 0.2s ease-in-out;
        }}
        
        [data-testid="stSidebar"] div.stButton > button:hover {{ 
            background-color: rgba(37, 99, 235, 0.15) !important; 
            color: #ffffff !important;
            transform: translateX(4px);
        }}
        
        .sidebar-section-title {{
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 14px;
            margin-bottom: 4px;
            padding-left: 10px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT, prioridade TEXT, ultimo_contato TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, horario TEXT, cliente TEXT, responsavel TEXT, tipo TEXT, local TEXT, status TEXT, observacoes TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS atividades (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, atividade TEXT, responsavel TEXT, data TEXT, hora TEXT, prioridade TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS propostas (id INTEGER PRIMARY KEY AUTOINCREMENT, numero TEXT, cliente TEXT, produto TEXT, valor REAL, data TEXT, validade TEXT, responsavel TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor TEXT, meta_mensal REAL, valor_vendido REAL, comissao REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS campanhas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, canal TEXT, inicio TEXT, fim TEXT, investimento REAL, leads_gerados INTEGER, conversoes INTEGER, roi REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS whatsapp (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, ultima_mensagem TEXT, status TEXT, responsavel TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cargo TEXT, email TEXT, perfil TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS permissoes (id INTEGER PRIMARY KEY AUTOINCREMENT, modulo TEXT, admin TEXT, gerente TEXT, vendedor TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS notificacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, mensagem TEXT, data TEXT, lida INTEGER)")

    # Dados padrão
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO usuarios (nome, cargo, email, perfil, status) VALUES (?, ?, ?, ?, ?)", [
            ("João Silva", "Administrador", "joao@crm.com", "Admin", "Ativo"),
            ("Ana Souza", "Gerente Comercial", "ana@crm.com", "Gerente", "Ativo"),
            ("Carlos Lima", "Vendedor", "carlos@crm.com", "Vendedor", "Ativo"),
        ])

    conn.commit()
    conn.close()

inicializar_banco()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"""
        <div style="padding: 5px 4px 15px 4px; display: flex; align-items: center; gap: 10px;">
            <div style="background-color: {cor_hex}; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">📊</div>
            <div>
                <div style="font-weight: 700; font-size: 16px; color: {text_app}; line-height: 1.2;">CRM PRO</div>
                <div style="font-size: 11px; color: #64748b; font-weight: 500;">Workspace v2.0</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    def menu_button(label, icon, key):
        if st.button(f"{icon}  {label}", key=key, use_container_width=True):
            st.session_state.selected = label
            st.rerun()

    # PRINCIPAL
    st.markdown('<p class="sidebar-section-title">Principal</p>', unsafe_allow_html=True)
    menu_button("Dashboard", "🏠", "nav_dashboard")
    menu_button("Clientes", "👥", "nav_clientes")
    menu_button("Leads", "🎯", "nav_leads")
    menu_button("Agenda", "📅", "nav_agenda")
    menu_button("Atividades", "📞", "nav_atividades")

    # COMERCIAL
    st.markdown('<p class="sidebar-section-title">Comercial</p>', unsafe_allow_html=True)
    menu_button("Pipeline", "📈", "nav_pipeline")
    menu_button("Vendas", "💰", "nav_vendas")
    menu_button("Propostas", "📄", "nav_propostas")
    menu_button("Relatórios", "📊", "nav_relatorios")
    menu_button("Metas", "🎯", "nav_metas")

    # MARKETING
    st.markdown('<p class="sidebar-section-title">Marketing</p>', unsafe_allow_html=True)
    menu_button("Campanhas", "📧", "nav_campanhas")
    menu_button("WhatsApp", "💬", "nav_whatsapp")

    # SISTEMA
    st.markdown('<p class="sidebar-section-title">Sistema</p>', unsafe_allow_html=True)
    menu_button("Integrações", "🔌", "nav_integracoes")
    menu_button("Usuários", "👤", "nav_usuarios")
    menu_button("Permissões", "🔒", "nav_permissoes")
    menu_button("Notificações", "🔔", "nav_notificacoes")
    menu_button("Configurações", "⚙️", "nav_configuracoes")

selected = st.session_state.selected

def conectar():
    return sqlite3.connect("crm.db")

@st.cache_data(ttl=1)
def carregar_dados():
    conn = conectar()
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- HEADER SUPERIOR ---
col_b1, col_b2, col_b3 = st.columns([6, 1, 1])
with col_b1:
    st.text_input("Busca Global", placeholder="🔍 Pesquisar no CRM...", label_visibility="collapsed")
with col_b2:
    st.markdown("🔔", help="Notificações")
with col_b3:
    st.markdown("👤", help="Perfil")

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-color: #334155;'>", unsafe_allow_html=True)

# --- ROTAS DAS PÁGINAS ---
if selected == "Dashboard":
    st.markdown("### 🏠 Dashboard Geral")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Clientes", len(df_clientes))
    col2.metric("Pipeline Ativo", f"R$ {df_pipeline['valor'].sum() if not df_pipeline.empty else 0:,.2f}")
    col3.metric("Vendas Realizadas", f"R$ {df_vendas['valor'].sum() if not df_vendas.empty else 0:,.2f}")

elif selected == "Clientes":
    st.markdown("### 👥 Clientes")
    st.dataframe(df_clientes, use_container_width=True, hide_index=True)

elif selected == "Leads":
    st.markdown("### 🎯 Leads")
    st.dataframe(df_clientes, use_container_width=True, hide_index=True)

elif selected == "Agenda":
    st.markdown("### 📅 Agenda de Compromissos")
    conn = conectar()
    df_agenda = pd.read_sql("SELECT * FROM agenda", conn)
    conn.close()
    st.dataframe(df_agenda, use_container_width=True, hide_index=True)

elif selected == "Atividades":
    st.markdown("### 📞 Atividades e Histórico")
    conn = conectar()
    df_ativ = pd.read_sql("SELECT * FROM atividades", conn)
    conn.close()
    st.dataframe(df_ativ, use_container_width=True, hide_index=True)

elif selected == "Pipeline":
    st.markdown("### 📈 Pipeline Comercial")
    st.dataframe(df_pipeline, use_container_width=True, hide_index=True)

elif selected == "Vendas":
    st.markdown("### 💰 Vendas")
    st.dataframe(df_vendas, use_container_width=True, hide_index=True)

elif selected == "Propostas":
    st.markdown("### 📄 Propostas Comerciais")
    conn = conectar()
    df_prop = pd.read_sql("SELECT * FROM propostas", conn)
    conn.close()
    st.dataframe(df_prop, use_container_width=True, hide_index=True)

elif selected == "Relatórios":
    st.markdown("### 📊 Relatórios e Exportações")
    st.info("Módulo de relatórios integrado com sucesso.")

elif selected == "Metas":
    st.markdown("### 🎯 Metas da Equipe")
    conn = conectar()
    df_metas = pd.read_sql("SELECT * FROM metas", conn)
    conn.close()
    st.dataframe(df_metas, use_container_width=True, hide_index=True)

elif selected == "Campanhas":
    st.markdown("### 📧 Campanhas de Marketing")
    conn = conectar()
    df_camp = pd.read_sql("SELECT * FROM campanhas", conn)
    conn.close()
    st.dataframe(df_camp, use_container_width=True, hide_index=True)

elif selected == "WhatsApp":
    st.markdown("### 💬 WhatsApp CRM")
    conn = conectar()
    df_wpp = pd.read_sql("SELECT * FROM whatsapp", conn)
    conn.close()
    st.dataframe(df_wpp, use_container_width=True, hide_index=True)

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações")
    st.text_input("API Key", value="api_live_secure_token")

elif selected == "Usuários":
    st.markdown("### 👤 Usuários do Sistema")
    conn = conectar()
    df_user = pd.read_sql("SELECT * FROM usuarios", conn)
    conn.close()
    st.dataframe(df_user, use_container_width=True, hide_index=True)

elif selected == "Permissões":
    st.markdown("### 🔒 Controle de Permissões")
    df_perm = pd.DataFrame([
        {"Módulo": "Dashboard", "Admin": "✅", "Gerente": "✅", "Vendedor": "✅"},
        {"Módulo": "Relatórios", "Admin": "✅", "Gerente": "✅", "Vendedor": "❌"},
    ])
    st.dataframe(df_perm, use_container_width=True, hide_index=True)

elif selected == "Notificações":
    st.markdown("### 🔔 Central de Notificações")
    st.success("Nenhuma nova notificação pendente.")

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    novo_tema = st.selectbox("Tema", ["🌙 Escuro", "☀️ Claro"], index=0 if "Escuro" in st.session_state.tema_sistema else 1)
    if novo_tema != st.session_state.tema_sistema:
        st.session_state.tema_sistema = novo_tema
        st.rerun()
