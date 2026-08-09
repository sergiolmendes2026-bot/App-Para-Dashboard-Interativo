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

mapa_cores = {
    "🔵 Azul": "#2563EB", 
    "🟢 Verde": "#10B981", 
    "🟣 Roxo": "#7C3AED"
}
cor_hex = mapa_cores.get(st.session_state.cor_principal_sistema, "#2563EB")
is_escuro = "Escuro" in st.session_state.tema_sistema

bg_app = "#0e1117" if is_escuro else "#ffffff"
text_app = "%23ffffff" if is_escuro else "#1e293b" # Corrigido string
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
    conn.commit()
    conn.close()

inicializar_banco()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"""<div style="padding: 10px 5px 20px 5px;"><div style="font-weight: bold; font-size: 20px; color: {text_app};">CRM COMERCIAL</div></div>""", unsafe_allow_html=True)
    menu_itens = [
        ("Dashboard", "📊"), ("Clientes", "👥"), ("Leads", "👤"), 
        ("Pipeline", "📈"), ("Vendas", "🏆"), ("Relatórios", "📄"), 
        ("Integrações", "🔌"), ("Configurações", "⚙️")
    ]
    for nome, icone in menu_itens:
        if st.button(f"{icone} {nome}", key=f"nav_{nome}", use_container_width=True):
            st.session_state.selected = nome
            st.rerun()

# Recupera a página selecionada com segurança
selected = st.session_state.selected

@st.cache_data(ttl=1)
def carregar_dados():
    conn = sqlite3.connect("crm.db")
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- DASHBOARD ---
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    
    # 1. KPIs no Topo (Cards)
    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and "valor" in df_vendas.columns and len(df_vendas) > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Leads", f"{total_leads}")
    c2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    c3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    c4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Abas para organizar os gráficos e não sobrecarregar a tela
    tab1, tab2, tab3 = st.tabs(["📈 Visão Geral & Vendas", "🎯 Funil & Pipeline", "👥 Equipe & Leads"])

    with tab1:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("#### Evolução das Vendas (Linha)")
            if not df_vendas.empty and "data" in df_vendas.columns:
                df_v_linha = df_vendas.groupby("data")["valor"].sum().reset_index()
                fig_linha = px.line(df_v_linha, x="data", y="valor", color_discrete_sequence=[cor_hex])
                fig_linha.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_linha, use_container_width=True)
            else:
                st.info("Sem dados de vendas suficientes.")

        with col_2:
            st.markdown("#### Meta x Realizado (Gauge)")
            meta_exemplo = 100000.0
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=receita_realizada,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Progresso da Meta"},
                gauge={'axis': {'range': [None, meta_exemplo]}, 'bar': {'color': cor_hex}}
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), height=250)
            st.plotly_chart(fig_gauge, use_container_width=True)

    with tab2:
        col_3, col_4 = st.columns(2)
        with col_3:
            st.markdown("#### Funil de Vendas")
            if not df_pipeline.empty and "estagio" in df_pipeline.columns:
                fig_funil = px.funnel(df_pipeline, x="valor", y="estagio", color_discrete_sequence=[cor_hex])
                fig_funil.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_funil, use_container_width=True)
            else:
                st.info("Sem dados no pipeline.")

        with col_4:
            st.markdown("#### Valor do Pipeline por Etapa (Barras)")
            if not df_pipeline.empty and "estagio" in df_pipeline.columns:
                df_pipe_bar = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
                fig_bar_pipe = px.bar(df_pipe_bar, x="valor", y="estagio", orientation="h", color_discrete_sequence=[cor_hex])
                fig_bar_pipe.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_bar_pipe, use_container_width=True)
            else:
                st.info("Sem dados no pipeline.")

    with tab3:
        col_5, col_6 = st.columns(2)
        with col_5:
            st.markdown("#### Origem dos Leads (Pizza)")
            if not df_clientes.empty and "origem" in df_clientes.columns:
                fig_origem = px.pie(df_clientes, names="origem", hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
                fig_origem.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_origem, use_container_width=True)
            else:
                st.info("Sem dados de clientes.")

        with col_6:
            st.markdown("#### Clientes por Status (Donut)")
            if not df_clientes.empty and "status" in df_clientes.columns:
                fig_status = px.pie(df_clientes, names="status", hole=0.6, color_discrete_sequence=px.colors.qualitative.Safe)
                fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Sem dados de status.")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    with st.form("form_pipeline", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        p_titulo = c1.text_input("Título")
        p_estagio = c2.selectbox("Estágio", ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"])
        p_valor = c3.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar Negócio"):
            conn = sqlite3.connect("crm.db")
            conn.execute("INSERT INTO pipeline (titulo, estagio, valor) VALUES (?,?,?)", (p_titulo, p_estagio, p_valor))
            conn.commit()
            conn.close()
            st.success("Adicionado com sucesso!")
            st.rerun()

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    st.radio("Tema", ["🌙 Escuro", "☀️ Claro"], key="tema_sistema")
    st.radio("Cor principal", ["🔵 Azul", "🟢 Verde", "🟣 Roxo"], key="cor_principal_sistema")
    if st.button("Salvar Preferências"):
        st.success("Atualizado!")
        st.rerun()
