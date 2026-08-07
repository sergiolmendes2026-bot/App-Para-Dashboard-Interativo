import pandas as pd
import sqlite3
import streamlit as st
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu

# --- CONFIGURAÇÃO DO BANCO ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    # ... (seu código de CREATE TABLE permanece igual)
    conn.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, data TEXT, responsavel TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT)")
    conn.commit()
    conn.close()

inicializar_banco()

st.set_page_config(page_title="CRM Comercial", page_icon="📊", layout="wide")

# --- FUNÇÃO DE DADOS COM CACHE ---
@st.cache_data(ttl=1) 
def carregar_dados():
    conn = sqlite3.connect("crm.db")
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df_clientes, df_pipeline, df_vendas

# Carrega os dados atualizados
df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    # ... (seu código de estilo do menu permanece igual)
    selected = option_menu(None, ["Dashboard", "Clientes", "Leads", "Pipeline", "Vendas", "Relatórios", "Integrações", "Configurações"],
                           icons=["speedometer2", "people-fill", "person-plus-fill", "kanban", "trophy-fill", "file-earmark-bar-graph", "plug", "gear-fill"],
                           default_index=0)

# --- DASHBOARD ATUALIZADO ---
if selected == "Dashboard":
    st.markdown("### Visão Geral")
    
    # Cálculos dinâmicos (Removidos os valores fixos)
    total_clientes = len(df_clientes)
    leads_cadastrados = len(df_clientes[df_clientes["status"] == "Lead"]) if not df_clientes.empty else 0
    clientes_ativos = len(df_clientes[df_clientes["status"] == "Ativo"]) if not df_clientes.empty else 0
    faturamento_mes = df_vendas["valor"].sum() if not df_vendas.empty else 0.0

    col1, col2, col3, col4 = st.columns(4)
    
    # Função auxiliar para cards para evitar repetição
    def exibir_card(label, valor, delta):
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px;">{label}</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{valor}</div>
                <div style="color: #10b981; font-size: 12px;">{delta}</div>
            </div>
        """, unsafe_allow_html=True)

    with col1: exibir_card("Total de Clientes", total_clientes, "Total geral")
    with col2: exibir_card("Leads Cadastrados", leads_cadastrados, "Prospectos")
    with col3: exibir_card("Clientes Ativos", clientes_ativos, "Clientes ativos")
    with col4: exibir_card("Faturamento (Mês)", f"R$ {faturamento_mes:,.2f}", "Total acumulado")

    # ... (O restante dos seus gráficos permanece igual abaixo)

# --- LOGICA DE INSERÇÃO ---
# Em todos os seus formulários (Clientes, Leads, Pipeline, Vendas), 
# quando você usa o st.rerun(), o Streamlit chamará a função carregar_dados() 
# novamente no topo do script, garantindo que o Dashboard veja os novos dados.

# Exemplo no bloco de Clientes:
# if submitted_cli:
#     ... conn.execute(...) ...
#     conn.commit()
#     conn.close()
#     st.success("Cliente cadastrado!")
#     st.rerun() # <--- Isso é o que faz o Dashboard atualizar!
