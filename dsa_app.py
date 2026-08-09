import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="CRM Comercial Profissional", page_icon="📊", layout="wide"
)

# --- INICIALIZAÇÃO DO ESTADO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro"
if "cor_principal_sistema" not in st.session_state:
    st.session_state.cor_principal_sistema = "🔵 Azul"
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

mapa_cores = {"🔵 Azul": "#2563EB", "🟢 Verde": "#10B981", "🟣 Roxo": "#7C3AED"}
cor_hex = mapa_cores.get(st.session_state.cor_principal_sistema, "#2563EB")
is_escuro = "Escuro" in st.session_state.tema_sistema

bg_app = "#0e1117" if is_escuro else "#ffffff"
text_app = "#ffffff" if is_escuro else "#1e293b"
sidebar_bg = "#0b0f19" if is_escuro else "#f8fafc"

# --- CSS E ESTILIZAÇÃO ---
st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_app}; color: {text_app}; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; }}
        div.stButton > button:first-child {{ background-color: {cor_hex} !important; color: white !important; border: none !important; }}
        h1, h2, h3, h4 {{ color: {text_app}; }}
        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; text-align: left; background-color: transparent !important;
            color: #94a3b8 !important; border: none !important; border-radius: 10px !important;
            padding: 10px 14px !important; font-size: 14px !important; font-weight: 500 !important;
        }}
        [data-testid="stSidebar"] div.stButton > button:hover {{ background-color: rgba(255, 255, 255, 0.05) !important; color: #ffffff !important; }}
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    conn.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT)")
    conn.commit(); conn.close()

inicializar_banco()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"""<div style="padding: 10px 5px 20px 5px;"><div style="font-weight: bold; font-size: 20px; color: {text_app};">CRM COMERCIAL</div></div>""", unsafe_allow_html=True)
    menu_itens = [("Dashboard", "📊"), ("Clientes", "👥"), ("Leads", "👤"), ("Pipeline", "📈"), ("Vendas", "🏆"), ("Relatórios", "📄"), ("Integrações", "🔌"), ("Configurações", "⚙️")]
    for nome, icone in menu_itens:
        if st.button(f"{icone} {nome}", use_container_width=True):
            st.session_state.selected = nome
            st.rerun()

selected = st.session_state.selected

@st.cache_data(ttl=1)
def carregar_dados():
    conn = sqlite3.connect("crm.db")
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- DASHBOARD ---
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    
    # Métricas Topo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads", len(df_clientes))
    c2.metric("Pipeline", f"R$ {df_pipeline['valor'].sum():,.2f}")
    c3.metric("Receita", f"R$ {df_vendas['valor'].sum():,.2f}")
    c4.metric("Ticket Médio", f"R$ {df_vendas['valor'].mean():,.2f}" if not df_vendas.empty else "R$ 0")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráfico 1 e 2
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### 📊 1. Vendas por mês")
        fig_v = px.bar(df_vendas.groupby(pd.to_datetime(df_vendas['data']).dt.strftime('%b'))["valor"].sum().reset_index(), x="data", y="valor", color_discrete_sequence=[cor_hex])
        fig_v.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
        st.plotly_chart(fig_v, use_container_width=True)
    
    with col_g2:
        st.markdown("#### 🥧 2. Pizza do Pipeline")
        fig_p = px.pie(df_pipeline, names="estagio", values="valor", hole=0.4, color_discrete_sequence=[cor_hex, "#10B981", "#F59E0B", "#EF4444", "#BE185D"])
        fig_p.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
        st.plotly_chart(fig_p, use_container_width=True)

    # NOVO GRÁFICO: 3. Valor por Etapa
    st.markdown("#### 📈 3. Valor do Pipeline por Etapa")
    if not df_pipeline.empty:
        df_pipe_bar = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
        fig_bar = px.bar(df_pipe_bar, x="valor", y="estagio", orientation="h", color_discrete_sequence=[cor_hex])
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bar, use_container_width=True)

# --- OUTRAS PÁGINAS (Mantidas como no seu original) ---
elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    with st.form("form_pipeline", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        p_titulo = c1.text_input("Título")
        p_estagio = c2.selectbox("Estágio", ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"])
        p_valor = c3.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            conn = sqlite3.connect("crm.db")
            conn.execute("INSERT INTO pipeline (titulo, estagio, valor) VALUES (?,?,?)", (p_titulo, p_estagio, p_valor))
            conn.commit(); conn.close(); st.rerun()

# ... (Você pode adicionar os outros elifs das outras páginas aqui abaixo)
