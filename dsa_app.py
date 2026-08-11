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

def executar_automacao_evento(tipo_evento, dados_contexto=""):
    """Verifica no banco se a automação está ativa e executa."""
    conn = conectar()
    cursor = conn.cursor()
    
    mapa_eventos = {
        "novo_lead": "email_boas_vindas",
        "mudar_estagio": "tarefa_pipeline",
        "estagnado": "alerta_estagnado"
    }
    
    chave = mapa_eventos.get(tipo_evento)
    if not chave:
        conn.close()
        return
        
    cursor.execute("SELECT ativo FROM automacoes WHERE chave = ?", (chave,))
    res = cursor.fetchone()
    conn.close()
    
    if res and res[0] == 1:
        st.write(f"✅ Automação disparada: {tipo_evento} - {dados_contexto}")

st.set_page_config(
    page_title="CRM LMB Pro - Workspace v2.0", page_icon="📊", layout="wide" 
)

# --- INICIALIZAÇÃO DO ESTADO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro"
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

# Cor principal fixa do sistema
cor_hex = "#2563EB"
is_escuro = "Escuro" in st.session_state.tema_sistema

bg_app = "#0e1117" if is_escuro else "#ffffff"
text_app = "#ffffff" if is_escuro else "#1e293b"
sidebar_bg = "#12161f" if is_escuro else "#f8fafc"

# --- CSS E ESTILIZAÇÃO DO MENU E PAINEIS ---
st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_app}; color: {text_app}; }}
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg}; 
            border-right: 1px solid #1e293b;
            padding-top: 10px;
        }}
        h1, h2, h3, h4 {{ color: {text_app}; }}
        
        /* Letras maiores com sombra suave e elegante */
        [data-testid="stSidebar"] button div p {{
            font-size: 16px !important;
            font-weight: 600 !important;
            text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.7) !important;
        }}

        /* Estilo para os botões do menu */
        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; 
            text-align: left; 
            background-color: transparent !important;
            color: #f1f5f9 !important; 
            border: none !important; 
            border-radius: 10px !important;
            padding: 8px 12px !important; 
            margin-bottom: 2px;
            transition: all 0.25s ease-in-out;
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
            margin-top: 16px;
            margin-bottom: 4px;
            padding-left: 12px;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);
        }}
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS E CORREÇÃO DE ESQUEMA ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT, prioridade TEXT, ultimo_contato TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agendamentos (id INTEGER PRIMARY KEY, ativo INTEGER, frequencia TEXT, destinatario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    
    tinfo_clientes = [col[1] for col in cursor.execute("PRAGMA table_info(clientes)").fetchall()]
    if "prioridade" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN prioridade TEXT DEFAULT 'Média'")
    if "ultimo_contato" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN ultimo_contato TEXT DEFAULT '2026-08-08'")
    if "responsavel" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN responsavel TEXT DEFAULT 'Carlos'")
    if "empresa" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN empresa TEXT DEFAULT 'Empresa Exemplo'")
    if "email" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN email TEXT DEFAULT 'contato@empresa.com'")
    if "telefone" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN telefone TEXT DEFAULT '(11) 99999-9999'")

    conn.commit()
    conn.close()

inicializar_banco()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"""
        <div style="padding: 5px 4px 10px 4px; display: flex; align-items: center; gap: 10px;">
            <div>
                <div style="font-weight: 700; font-size: 15px; color: {text_app}; letter-spacing: 0.5px;">CRM PRO</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    def menu_button(label, icon, key):
        if st.button(f"{icon}  {label}", key=key, use_container_width=True):
            st.session_state.selected = label
            st.rerun()

    st.markdown('<p class="sidebar-section-title">Principal</p>', unsafe_allow_html=True)
    menu_button("Dashboard", "🏠", "nav_dashboard")
    menu_button("Clientes", "👥", "nav_clientes")
    menu_button("Leads", "🎯", "nav_leads")
    menu_button("Agenda", "📅", "nav_agenda")
    menu_button("Atividades", "📞", "nav_atividades")

    st.markdown('<p class="sidebar-section-title">Comercial</p>', unsafe_allow_html=True)
    menu_button("Pipeline", "📈", "nav_pipeline")
    menu_button("Vendas", "💰", "nav_vendas")
    menu_button("Propostas", "📄", "nav_propostas")
    menu_button("Relatórios", "📊", "nav_relatorios")
    menu_button("Metas", "🎯", "nav_metas")

    st.markdown('<p class="sidebar-section-title">Marketing</p>', unsafe_allow_html=True)
    menu_button("Campanhas", "📢", "nav_campanhas")
    menu_button("WhatsApp", "💬", "nav_whatsapp")

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
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame()
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame()
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame()
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- CONTEÚDO PRINCIPAL (EXEMPLO PARA AS NOVAS TELAS) ---
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    st.write("Bem-vindo ao painel principal.")
else:
    st.markdown(f"### ⚙️ Tela de {selected}")
    st.write(f"Conteúdo da seção **{selected}** em desenvolvimento.")
