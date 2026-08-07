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
    
    # Cria as tabelas se não existirem
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
    
    # Garante que colunas novas existam mesmo em bases antigas
    cursor = conn.cursor()
    
    # Migração Clientes
    cursor.execute("PRAGMA table_info(clientes)")
    colunas_existentes_clientes = [col[1] for col in cursor.fetchall()]
    novas_colunas_clientes = {"origem": "TEXT", "motivo_perda": "TEXT", "data_fechamento": "TEXT", "responsavel": "TEXT"}
    for coluna, tipo in novas_colunas_clientes.items():
        if coluna not in colunas_existentes_clientes:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}")

    # Migração Pipeline
    cursor.execute("PRAGMA table_info(pipeline)")
    colunas_existentes_pipeline = [col[1] for col in cursor.fetchall()]
    novas_colunas_pipeline = {"empresa": "TEXT", "contato": "TEXT", "telefone": "TEXT", "email": "TEXT", "responsavel": "TEXT", "origem": "TEXT"}
    for coluna, tipo in novas_colunas_pipeline.items():
        if coluna not in colunas_existentes_pipeline:
            conn.execute(f"ALTER TABLE pipeline ADD COLUMN {coluna} {tipo}")

    # Migração Vendas (Adiciona status se não existir)
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
            "Dashboard",
            "Clientes",
            "Leads",
            "Pipeline",
            "Vendas",
            "Relatórios",
            "Integrações",
            "Configurações",
        ],
        icons=[
            "speedometer2", 
            "people-fill",    
            "person-plus-fill", 
            "kanban",         
            "trophy-fill",    
            "file-earmark-bar-graph", 
            "plug",           
            "gear-fill"       
        ],
        menu_icon="cast",
        default_index=4, # Abre direto na aba Vendas para facilitar
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
    st.info("Dashboard carregado com sucesso.")

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro Completo de Clientes e Leads")
    # ... (Conteúdo da página de Clientes)

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    # ... (Conteúdo da página de Leads)

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    # ... (Conteúdo da página de Pipeline)

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas Fechadas")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Registre faturamentos, acompanhe os indicadores e consulte o histórico em tabela.</p>", unsafe_allow_html=True)

    # --- CÁLCULOS DOS INDICADORES DE VENDAS ---
    faturamento_total = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    total_vendas_count = len(df_vendas) if not df_vendas.empty else 0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and total_vendas_count > 0 else 0.0
    
    melhor_vendedor = "N/A"
    if not df_vendas.empty and "responsavel" in df_vendas.columns and total_vendas_count > 0:
        vendas_por_resp = df_vendas.groupby('responsavel')['valor'].sum()
        if not vendas_por_resp.empty:
            melhor_vendedor = vendas_por_resp.idxmax()

    # --- EXIBIÇÃO DOS INDICADORES EM COLUNAS (CARDS) ---
    vk1, vk2, vk3, vk4 = st.columns(4)
    vk1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
    vk2.metric("📦 Total de Vendas", f"{total_vendas_count}")
    vk3.metric("📈 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    vk4.metric("🏆 Melhor Vendedor", f"{melhor_vendedor}")

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # --- FORMULÁRIO DE REGISTRO DE VENDAS (ATUALIZADO COM STATUS) ---
    with st.form("form_venda", clear_on_submit=True):
        col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
        with col_v1:
            v_cliente = st.text_input("Cliente *")
        with col_v2:
            v_valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
        with col_v3:
            v_resp = st.text_input("Responsável", value="Comercial")
        with col_v4:
            v_data = st.text_input("Data", value=str(date.today()))
        with col_v5:
            v_status = st.selectbox("Status", ["Pago", "Pendente", "Cancelado"])
            
        btn_venda = st.form_submit_button("Registrar Venda")
        if btn_venda:
            if v_cliente and v_valor > 0:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel, status) VALUES (?, ?, ?, ?, ?)", 
                             (v_cliente, v_valor, v_data, v_resp, v_status))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o cliente e um valor válido.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📜 Histórico de Vendas")
    
    if not df_vendas.empty:
        # Renomeia/organiza as colunas para exibição profissional idêntica à solicitada
        df_tabela_vendas = df_vendas[['cliente', 'valor', 'responsavel', 'data', 'status']].copy()
        df_tabela_vendas.columns = ['Cliente', 'Valor', 'Responsável', 'Data', 'Status']
        
        # Formata o campo de valor para exibição em moeda
        df_tabela_vendas['Valor'] = df_tabela_vendas['Valor'].apply(lambda x: f"R$ {x:,.3f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(df_tabela_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada ainda.")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação")
    # ...

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    # ...

else:
    st.markdown("### ⚙️ Configurações do Sistema")
    # ...
