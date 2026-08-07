import pandas as pd
import sqlite3
import streamlit as st
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu

# --- CONFIGURAÇÃO DA PÁGINA E BANCO ---
st.set_page_config(page_title="CRM Comercial", page_icon="📊", layout="wide")

def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    conn.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, data TEXT, responsavel TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT)")
    conn.commit()
    conn.close()

inicializar_banco()

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

# --- BARRA LATERAL ---
with st.sidebar:
    selected = option_menu(None, ["Dashboard", "Clientes", "Leads", "Pipeline", "Vendas", "Relatórios", "Integrações", "Configurações"],
                           icons=["speedometer2", "people-fill", "person-plus-fill", "kanban", "trophy-fill", "file-earmark-bar-graph", "plug", "gear-fill"],
                           default_index=0)

# --- DASHBOARD ---
if selected == "Dashboard":
    st.markdown("### Visão Geral")
    
    total_clientes = len(df_clientes)
    leads_cadastrados = len(df_clientes[df_clientes["status"] == "Lead"]) if not df_clientes.empty and "status" in df_clientes.columns else 0
    clientes_ativos = len(df_clientes[df_clientes["status"] == "Ativo"]) if not df_clientes.empty and "status" in df_clientes.columns else 0
    faturamento_mes = df_vendas["valor"].sum() if not df_vendas.empty else 0.0

    # Cards (MANTIDO SEU DESIGN)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">Total de Clientes<div style="font-size:28px; font-weight:bold;">{total_clientes}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">Leads<div style="font-size:28px; font-weight:bold;">{leads_cadastrados}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">Ativos<div style="font-size:28px; font-weight:bold;">{clientes_ativos}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">Faturamento<div style="font-size:26px; font-weight:bold;">R$ {faturamento_mes:,.2f}</div></div>', unsafe_allow_html=True)

    # --- LÓGICA DINÂMICA PARA GRÁFICOS ---
    # 1. Funil
    ordem_etapas = ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechamento']
    valores_funil = [len(df_pipeline[df_pipeline['estagio'] == e]) for e in ordem_etapas] if not df_pipeline.empty else [0]*5
    
    fig_funil = go.Figure(go.Bar(y=ordem_etapas, x=valores_funil, orientation='h', marker_color='#2563EB'))
    fig_funil.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=0, r=0, t=0, b=0))

    # 2. Vendas por Mês
    if not df_vendas.empty:
        df_vendas['mes'] = pd.to_datetime(df_vendas['data'], errors='coerce').dt.strftime('%b')
        vendas_mes = df_vendas.groupby('mes')['valor'].sum()
    else:
        vendas_mes = pd.Series(dtype=float)
        
    fig_line = go.Figure(go.Scatter(x=vendas_mes.index, y=vendas_mes.values, mode='lines+markers', line_color='#38bdf8'))
    fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220)

    # Exibição dos gráficos (MANTENDO SEU LAYOUT)
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Funil de Vendas")
        st.plotly_chart(fig_funil, use_container_width=True)
    with col_right:
        st.subheader("Vendas por Mês")
        st.plotly_chart(fig_line, use_container_width=True)

# --- ROTINAS DE CADASTRO (Adicionado st.rerun para atualizar Dashboard) ---
elif selected == "Clientes":
    with st.form("c1", clear_on_submit=True):
        nome = st.text_input("Nome")
        status = st.selectbox("Status", ["Ativo", "Lead", "Inativo"])
        if st.form_submit_button("Salvar"):
            conn = conectar()
            conn.execute("INSERT INTO clientes (nome, status, data) VALUES (?, ?, ?)", (nome, status, str(date.today())))
            conn.commit()
            conn.close()
            st.rerun() # O Dashboard atualizará ao voltar nele
