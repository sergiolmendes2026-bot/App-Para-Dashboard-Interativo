import pandas as pd
import sqlite3
import streamlit as st
import altair as alt
from datetime import date, datetime
from database import conectar, inicializar_banco
from streamlit_option_menu import option_menu

# Garante que o banco e as tabelas estejam criados
inicializar_banco()

st.set_page_config(
    page_title="CRM Comercial", page_icon="📊", layout="wide"
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
        default_index=1, # Inicia em Clientes ou conforme navegação
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

# --- FUNÇÃO PARA CARREGAR DADOS DE FORMA SEGURA ---
def carregar_dados():
    conn = conectar()
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    if "clientes" in tabelas:
        df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    else:
        df_clientes = pd.DataFrame(columns=["id", "nome", "empresa", "email", "telefone", "regiao", "status", "data", "responsavel"])
        
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame(columns=["id", "titulo", "estagio", "valor"])
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame(columns=["id", "cliente", "valor", "data"])
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### Visão Geral")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    total_clientes = len(df_clientes) if not df_clientes.empty else 1248
    leads_cadastrados = len(df_clientes[df_clientes["status"] == "Lead"]) if not df_clientes.empty and "status" in df_clientes.columns else 532
    clientes_ativos = len(df_clientes[df_clientes["status"] == "Ativo"]) if not df_clientes.empty and "status" in df_clientes.columns else 873
    faturamento_mes = df_vendas["valor"].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 245780.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Total de Clientes</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{total_clientes:,}</div>
                <div style="color: #10b981; font-size: 12px;">↑ +12,5% <span style="color: #64748b;">vs mês anterior</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Leads Cadastrados</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{leads_cadastrados:,}</div>
                <div style="color: #10b981; font-size: 12px;">↑ +8,3% <span style="color: #64748b;">vs mês anterior</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Clientes Ativos</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{clientes_ativos:,}</div>
                <div style="color: #10b981; font-size: 12px;">↑ +15,7% <span style="color: #64748b;">vs mês anterior</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Faturamento (Mês)</div>
                <div style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 8px 0;">R$ {faturamento_mes:,.2f}</div>
                <div style="color: #10b981; font-size: 12px;">↑ +10,2% <span style="color: #64748b;">vs mês anterior</span></div>
            </div>
        """, unsafe_allow_html=True)

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro de Clientes e Leads")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Adicione novos clientes para alimentar o seu CRM e a sua operação comercial.</p>", unsafe_allow_html=True)
    
    # Formulário de Cadastro com 2 Colunas Exatamente como na Referência
    with st.form("form_cliente_completo", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            nome_contato = st.text_input("Nome do Contato *")
            nome_empresa = st.text_input("Nome da Empresa")
            email_cli = st.text_input("E-mail")
            
        with col_c2:
            telefone_cli = st.text_input("Telefone / WhatsApp")
            regiao_cli = st.selectbox("Região", ["Selecione...", "Região Sul", "Região Sudeste", "Região Nordeste", "Região Centro-Oeste", "Região Norte"])
            status_cli = st.selectbox("Status do Cliente", ["Ativo", "Lead", "Inativo"])
            data_cad = st.text_input("Data de Cadastro", value=str(date.today()))
            
        submitted_cli = st.form_submit_button("Salvar Cliente")
        
        if submitted_cli:
            if nome_contato:
                conn = conectar()
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        nome TEXT, 
                        empresa TEXT, 
                        email TEXT, 
                        telefone TEXT, 
                        regiao TEXT, 
                        status TEXT, 
                        data TEXT, 
                        responsavel TEXT
                    )
                """)
                conn.execute("""
                    INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, data, responsavel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome_contato, nome_empresa, email_cli, telefone_cli, regiao_cli, status_cli, data_cad, "Equipe Comercial"))
                conn.commit()
                conn.close()
                st.success("Cliente cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha ao menos o Nome do Contato.")

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Tabela de Clientes e Contatos (CRM)")
    
    if not df_clientes.empty:
        # Prepara o dataframe para exibição alinhada ao layout desejado
        df_exibicao = pd.DataFrame()
        df_exibicao["Cliente"] = df_clientes.apply(lambda row: f"{row['nome']} - {row.get('empresa', 'CRM')}" if pd.notnull(row.get('empresa')) and row.get('empresa') != "" else row['nome'], axis=1)
        df_exibicao["Tipo"] = df_clientes["regiao"] if "regiao" in df_clientes.columns else "Região Sul"
        df_exibicao["Data"] = df_clientes["data"] if "data" in df_clientes.columns else str(date.today())
        df_exibicao["Responsável"] = df_clientes["responsavel"] if "responsavel" in df_clientes.columns else "Equipe Comercial"
        df_exibicao["Status"] = df_clientes["status"] if "status" in df_clientes.columns else "Ativo"
        df_exibicao["Ações"] = "Gerenciar / WhatsApp"
        
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado no banco de dados.")

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("### 💬 Ações Rápidas - WhatsApp")
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Selecione o cliente para enviar mensagem:</p>", unsafe_allow_html=True)
    
    lista_nomes = df_clientes["nome"].tolist() if not df_clientes.empty and "nome" in df_clientes.columns else ["Nenhum cliente disponível"]
    cliente_selecionado = st.selectbox("Selecione o cliente", lista_nomes, label_visibility="collapsed")
    
    if st.button("🟢 Falar no WhatsApp"):
        st.success(f"Iniciando conversa via WhatsApp com: **{cliente_selecionado}**")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline de Vendas")
    st.info("Módulo de Pipeline comercial.")

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas")
    st.info("Módulo de Gestão de Vendas.")

else:
    st.markdown(f"### ⚙️ {selected}")
    st.info("Módulo em desenvolvimento.")
