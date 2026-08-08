import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT, empresa TEXT, email TEXT, telefone TEXT, 
            regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT,
            data TEXT, data_fechamento TEXT, responsavel TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            titulo TEXT, estagio TEXT, valor REAL, empresa TEXT,
            contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_banco()

st.set_page_config(page_title="CRM Comercial Profissional", page_icon="📊", layout="wide")

# --- BARRA LATERAL ---
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
        options=["Dashboard", "Clientes", "Leads", "Pipeline", "Vendas", "Relatórios", "Integrações", "Configurações"],
        icons=["speedometer2", "people-fill", "person-plus-fill", "kanban", "trophy-fill", "file-earmark-bar-graph", "plug", "gear-fill"],
        default_index=0,
        styles={
            "container": {"background-color": "transparent"},
            "nav-link-selected": {"background-color": "#2563EB"}
        }
    )

def conectar(): return sqlite3.connect("crm.db")

@st.cache_data(ttl=1)
def carregar_dados():
    conn = conectar()
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- NAVEGAÇÃO ---
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Leads", len(df_clientes))
    k2.metric("Valor do Pipeline", f"R$ {df_pipeline['valor'].sum():,.2f}")
    k3.metric("Receita Realizada", f"R$ {df_vendas['valor'].sum():,.2f}")
    k4.metric("Ticket Médio", f"R$ {df_vendas['valor'].mean():,.2f}" if not df_vendas.empty else "R$ 0,00")

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro de Clientes")
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome *")
        status = col2.selectbox("Status", ["Novo Lead", "Em Atendimento", "Venda Fechada"])
        if st.form_submit_button("Salvar"):
            conn = conectar()
            conn.execute("INSERT INTO clientes (nome, status) VALUES (?, ?)", (nome, status))
            conn.commit()
            conn.close()
            st.rerun()
    st.dataframe(df_clientes, use_container_width=True)

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    # Lógica de pipeline...

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas")
    # Lógica de vendas...

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    c1.subheader("🏢 Dados da Organização")
    c1.text_input("Nome da Organização", value="Comercial Alpha LTDA")
    c2.subheader("🛠 Preferências")
    c2.selectbox("Moeda Padrão", ["Real (BRL - R$)", "Dólar (USD - $)", "Euro (EUR - €)"])

    st.markdown("---")
    st.markdown("### 👥 Gestão de Equipe e Permissões")
    
    if st.button("➕ Adicionar Usuário"):
        st.info("Formulário de cadastro aberto.")

    st.markdown("#### 🔒 Permissões")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        with st.container(border=True):
            st.markdown("**Administrador**")
            st.checkbox("Clientes", True, key="a1")
            st.checkbox("Leads", True, key="a2")
            st.checkbox("Pipeline", True, key="a3")
            st.checkbox("Relatórios", True, key="a4")
            st.checkbox("Configurações", True, key="a5")
            
    with col_p2:
        with st.container(border=True):
            st.markdown("**Vendedor**")
            st.checkbox("Clientes", True, key="v1")
            st.checkbox("Leads", True, key="v2")
            st.checkbox("Pipeline", True, key="v3")
            st.checkbox("Configurações", False, key="v4")
            st.checkbox("Usuários", False, key="v5")

    if st.button("Salvar Configurações"):
        st.success("Configurações e permissões atualizadas!")

else:
    st.write(f"Página {selected} em construção.")
