import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="CRM Pro - Workspace v2.0", page_icon="📊", layout="wide"
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
text_app = "#ffffff" if is_escuro else "#1e293b"
sidebar_bg = "#0b0f19" if is_escuro else "#f8fafc"

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
        
        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; 
            text-align: left; 
            background-color: transparent !important;
            color: #94a3b8 !important; 
            border: none !important; 
            border-radius: 8px !important;
            padding: 8px 12px !important; 
            font-size: 14px !important; 
            font-weight: 500 !important;
            margin-bottom: 2px;
            transition: all 0.2s ease-in-out;
        }}
        
        [data-testid="stSidebar"] div.stButton > button:hover {{ 
            background-color: rgba(255, 255, 255, 0.05) !important; 
            color: #ffffff !important; 
        }}
        
        .sidebar-section-title {{
            color: #64748b;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-top: 18px;
            margin-bottom: 6px;
            padding-left: 12px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS E CORREÇÃO DE ESQUEMA ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    
    tinfo_vendas = [col[1] for col in cursor.execute("PRAGMA table_info(vendas)").fetchall()]
    if "produto" not in tinfo_vendas:
        cursor.execute("ALTER TABLE vendas ADD COLUMN produto TEXT")
    
    cursor.execute("SELECT COUNT(*) FROM vendas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO vendas (cliente, valor, data, responsavel, status, produto) VALUES (?, ?, ?, ?, ?, ?)", [
            ("Empresa Alpha", 15000.0, "2026-06-01", "Carlos", "Pago", "Software A"),
            ("Empresa Beta", 25000.0, "2026-06-05", "Ana", "Pago", "Software B"),
            ("Empresa Gama", 10000.0, "2026-06-10", "Carlos", "Pago", "Consultoria"),
            ("Empresa Delta", 40000.0, "2026-06-15", "Ana", "Pago", "Software A"),
        ])
    
    cursor.execute("SELECT COUNT(*) FROM pipeline")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO pipeline (titulo, estagio, valor, responsavel) VALUES (?, ?, ?, ?)", [
            ("Projeto X", "Prospecção", 50000.0, "Carlos"),
            ("Projeto Y", "Qualificação", 30000.0, "Ana"),
            ("Projeto Z", "Proposta", 20000.0, "Carlos"),
            ("Projeto W", "Fechamento", 15000.0, "Ana"),
        ])

    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO clientes (nome, status, origem, motivo_perda, data) VALUES (?, ?, ?, ?, ?)", [
            ("João Silva", "🆕 Novo Lead", "Google Ads", "", "2026-06-01"),
            ("Maria Silva", "✅ Venda Fechada", "Instagram", "", "2026-06-02"),
            ("Maria Oliveira", "❌ Venda Perdida", "Indicação", "Preço Alto", "2026-06-03"),
            ("Ana Paula", "💬 Em Atendimento", "WhatsApp", "", "2026-06-04"),
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
        is_active = st.session_state.selected == label
        if st.button(f"{icon}  {label}", key=key, use_container_width=True):
            st.session_state.selected = label
            st.rerun()

    st.markdown('<p class="sidebar-section-title">Principal</p>', unsafe_allow_html=True)
    menu_button("Dashboard", "🏠", "nav_dashboard")
    menu_button("Clientes", "📖", "nav_clientes")
    menu_button("Leads", "🎯", "nav_leads")

    st.markdown('<p class="sidebar-section-title">Comercial</p>', unsafe_allow_html=True)
    menu_button("Pipeline", "📈", "nav_pipeline")
    menu_button("Vendas", "🏆", "nav_vendas")
    menu_button("Relatórios", "📄", "nav_relatorios")

    st.markdown('<p class="sidebar-section-title">Sistema</p>', unsafe_allow_html=True)
    menu_button("Integrações", "🔌", "nav_integracoes")
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

# --- BARRA DE PESQUISA GLOBAL NO CABEÇALHO ---
col_busca1, col_busca2, col_busca3 = st.columns([6, 1, 1])
with col_busca1:
    termo_busca = st.text_input("Pesquisa Global", placeholder="🔍 Pesquisar clientes, leads, vendas...", label_visibility="collapsed")
with col_busca2:
    st.markdown("🔔", help="Notificações")
with col_busca3:
    st.markdown("👤", help="Perfil do Usuário")

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-color: #334155;'>", unsafe_allow_html=True)

# Lógica de Exibição dos Resultados da Busca Global
if termo_busca and len(termo_busca.strip()) > 0:
    st.markdown(f"### 🔎 Resultados da Busca para: *'{termo_busca}'*")
    
    # 1. Clientes
    if not df_clientes.empty and "nome" in df_clientes.columns:
        res_clientes = df_clientes[df_clientes['nome'].str.contains(termo_busca, case=False, na=False) | df_clientes['empresa'].str.contains(termo_busca, case=False, na=False)]
        if not res_clientes.empty:
            st.markdown("##### 👥 Clientes")
            st.dataframe(res_clientes[['nome', 'empresa', 'email', 'telefone', 'status']], use_container_width=True, hide_index=True)

    # 2. Leads (Filtra por leads)
    if not df_clientes.empty and "status" in df_clientes.columns:
        df_leads_base = df_clientes[df_clientes["status"].str.contains("Lead|Contato|Atendimento|Novo", case=False, na=False)]
        res_leads = df_leads_base[df_leads_base['nome'].str.contains(termo_busca, case=False, na=False) | df_leads_base['empresa'].str.contains(termo_busca, case=False, na=False)]
        if not res_leads.empty:
            st.markdown("##### 🎯 Leads")
            st.dataframe(res_leads[['nome', 'empresa', 'telefone', 'origem', 'status']], use_container_width=True, hide_index=True)

    # 3. Vendas
    if not df_vendas.empty and "cliente" in df_vendas.columns:
        res_vendas = df_vendas[df_vendas['cliente'].str.contains(termo_busca, case=False, na=False) | df_vendas['produto'].str.contains(termo_busca, case=False, na=False)]
        if not res_vendas.empty:
            st.markdown("##### 🏆 Vendas")
            st.dataframe(res_vendas, use_container_width=True, hide_index=True)

    # 4. Pipeline
    if not df_pipeline.empty and "titulo" in df_pipeline.columns:
        res_pipe = df_pipeline[df_pipeline['titulo'].str.contains(termo_busca, case=False, na=False) | df_pipeline['estagio'].str.contains(termo_busca, case=False, na=False)]
        if not res_pipe.empty:
            st.markdown("##### 📈 Pipeline")
            st.dataframe(res_pipe, use_container_width=True, hide_index=True)

    st.divider()
else:
    # --- CONTEÚDO NORMAL DAS PÁGINAS SE NÃO HOUVER BUSCA GLOBAL ---

    # --- DASHBOARD ---
    if selected == "Dashboard":
        st.markdown("### 📊 Dashboard de Performance Comercial")
        
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

        tab1, tab2, tab3 = st.tabs(["💰 Vendas & Receita", "🎯 Pipeline & Funil", "👥 Leads & Perdas"])

        with tab1:
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown("#### 📈 Evolução das Vendas")
                if not df_vendas.empty and "data" in df_vendas.columns:
                    df_temp = df_vendas.copy()
                    df_temp['data'] = pd.to_datetime(df_temp['data'], errors='coerce')
                    df_v_linha = df_temp.groupby("data")["valor"].sum().reset_index()
                    df_v_linha = df_v_linha.sort_values("data")
                    fig_linha = px.line(df_v_linha, x="data", y="valor", markers=True, color_discrete_sequence=[cor_hex])
                    fig_linha.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                    st.plotly_chart(fig_linha, use_container_width=True)
                else:
                    st.info("Sem dados suficientes de vendas.")

            with c_v2:
                st.markdown("#### 🎯 Meta x Realizado (Gauge)")
                meta_exemplo = 150000.0
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=receita_realizada,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Progresso de Vendas vs Meta"},
                    gauge={'axis': {'range': [None, meta_exemplo]}, 'bar': {'color': cor_hex}}
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), height=260)
                st.plotly_chart(fig_gauge, use_container_width=True)

        with tab2:
            st.markdown("#### 📊 Funil de Vendas")
            if not df_pipeline.empty and "estagio" in df_pipeline.columns:
                fig_funil = px.funnel(df_pipeline, x="valor", y="estagio", color_discrete_sequence=[cor_hex])
                fig_funil.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_funil, use_container_width=True)
            else:
                st.info("Sem dados no pipeline.")

        with tab3:
            st.markdown("#### 🍩 Origem dos Leads")
            if not df_clientes.empty and "origem" in df_clientes.columns:
                fig_origem = px.pie(df_clientes, names="origem", hole=0.5, color_discrete_sequence=px.colors.qualitative.Prism)
                fig_origem.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_origem, use_container_width=True)
            else:
                st.info("Sem dados de origem.")

    # --- CLIENTES ---
    elif selected == "Clientes":
        st.markdown("### 📖 Cadastro Completo de Clientes e Leads")
        
        # Filtro específico da tela de clientes
        filtro_cli = st.text_input("🔍 Pesquisar na tabela de Clientes", placeholder="Digite nome, empresa ou e-mail...")
        
        with st.form("form_cliente_completo", clear_on_submit=True):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                nome_contato = st.text_input("Nome do Contato *")
                nome_empresa = st.text_input("Nome da Empresa")
                email_cli = st.text_input("E-mail")
                telefone_cli = st.text_input("Telefone / WhatsApp")
            with col_c2:
                origem_cli = st.selectbox("Origem do Lead", ["Indicação", "Instagram", "Google Ads", "WhatsApp", "Site"])
                status_cli = st.selectbox("Status do Cliente", ["🆕 Novo Lead", "💬 Em Atendimento", "✅ Venda Fechada", "❌ Venda Perdida"])
                responsavel_cli = st.text_input("Responsável Comercial", value="Equipe Comercial")
                data_cad = st.text_input("Data de Cadastro", value=str(date.today()))
                
            submitted_cli = st.form_submit_button("Salvar Cliente no CRM")
            if submitted_cli:
                if nome_contato:
                    conn = conectar()
                    conn.execute("INSERT INTO clientes (nome, empresa, email, telefone, status, origem, data, responsavel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                               (nome_contato, nome_empresa, email_cli, telefone_cli, status_cli, origem_cli, data_cad, responsavel_cli))
                    conn.commit()
                    conn.close()
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha ao menos o Nome do Contato.")

        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📋 Base de Dados de Clientes")
        if not df_clientes.empty:
            df_exibir = df_clientes.copy()
            if filtro_cli:
                df_exibir = df_exibir[df_exibir['nome'].str.contains(filtro_cli, case=False, na=False) | df_exibir['empresa'].str.contains(filtro_cli, case=False, na=False)]
            st.dataframe(df_exibir[['nome', 'empresa', 'telefone', 'origem', 'status', 'responsavel', 'data']], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cliente cadastrado.")

    # --- LEADS ---
    elif selected == "Leads":
        st.markdown("### 🎯 Gestão de Leads")
        filtro_leads = st.text_input("🔍 Pesquisar em Leads", placeholder="Nome ou empresa...")
        df_leads_only = df_clientes[df_clientes["status"].str.contains("Lead|Contato|Atendimento|Novo", case=False, na=False)] if not df_clientes.empty and "status" in df_clientes.columns else pd.DataFrame()
        if not df_leads_only.empty:
            if filtro_leads:
                df_leads_only = df_leads_only[df_leads_only['nome'].str.contains(filtro_leads, case=False, na=False)]
            st.dataframe(df_leads_only[["nome", "empresa", "email", "telefone", "origem", "status", "data"]], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum lead em aberto.")

    # --- PIPELINE ---
    elif selected == "Pipeline":
        st.markdown("### 📈 Pipeline Comercial")
        filtro_pipe = st.text_input("🔍 Pesquisar no Pipeline", placeholder="Título ou estágio...")
        if not df_pipeline.empty:
            df_pipe_ex = df_pipeline.copy()
            if filtro_pipe:
                df_pipe_ex = df_pipe_ex[df_pipe_ex['titulo'].str.contains(filtro_pipe, case=False, na=False)]
            st.dataframe(df_pipe_ex, use_container_width=True, hide_index=True)
        else:
            st.info("Pipeline vazio.")

    # --- VENDAS ---
    elif selected == "Vendas":
        st.markdown("### 🏆 Controle de Vendas Fechadas")
        filtro_vendas = st.text_input("🔍 Pesquisar em Vendas", placeholder="Cliente ou produto...")
        if not df_vendas.empty:
            df_v_ex = df_vendas.copy()
            if filtro_vendas:
                df_v_ex = df_v_ex[df_v_ex['cliente'].str.contains(filtro_vendas, case=False, na=False) | df_v_ex['produto'].str.contains(filtro_vendas, case=False, na=False)]
            st.dataframe(df_v_ex, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma venda registrada.")

    # --- RELATÓRIOS ---
    elif selected == "Relatórios":
        st.markdown("### 📄 Relatórios e Exportação")
        df_export = df_vendas if not df_vendas.empty else pd.DataFrame()
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Exportar Dados para CSV", data=csv_data, file_name="vendas_crm.csv", mime="text/csv")

    # --- INTEGRAÇÕES ---
    elif selected == "Integrações":
        st.markdown("### 🔌 Integrações e Conexões")
        st.toggle("Ativar Integração WhatsApp", value=True)

    # --- CONFIGURAÇÕES ---
    elif selected == "Configurações":
        st.markdown("### ⚙️ Configurações do Sistema")
        tab_cfg1, tab_cfg2, tab_cfg3, tab_cfg4 = st.tabs(["🎨 Aparência", "🔌 Integrações & API", "⚡ Automações", "📋 Logs & Histórico"])

        with tab_cfg1:
            st.markdown("#### Preferências Visuais")
            col_ap1, col_ap2 = st.columns(2)
            with col_ap1:
                st.radio("Tema do Sistema", ["🌙 Escuro", "☀️ Claro"], key="tema_sistema")
            with col_ap2:
                st.radio("Cor Principal do Sistema", ["🔵 Azul", "🟢 Verde", "🟣 Roxo"], key="cor_principal_sistema")
            if st.button("Salvar Preferências"):
                st.success("Salvo com sucesso!")
                st.rerun()

        with tab_cfg2:
            st.markdown("#### Tabela de Integrações")
            dados_integracoes = pd.DataFrame({
                "Serviço": ["WhatsApp Business", "Google Calendar", "SMTP", "OpenAI"],
                "Status": ["🟢 Conectado", "🟢 Conectado", "❌ Desconectado", "🟢 Ativo"],
                "Ação": ["Configurar", "Gerenciar", "Conectar", "Testar"]
            })
            st.dataframe(dados_integracoes, use_container_width=True, hide_index=True)

        with tab_cfg3:
            st.markdown("#### Automações")
            st.checkbox("Criar lead automaticamente via webhook", value=True)
            st.checkbox("Disparar e-mail de boas-vindas", value=True)

        with tab_cfg4:
            st.markdown("#### Histórico de Sincronização")
            dados_logs = pd.DataFrame({
                "Data": ["09/08/2026 18:42", "09/08/2026 18:49"],
                "Serviço": ["WhatsApp", "SMTP"],
                "Status": ["🟢 Sucesso", "❌ Erro"]
            })
            st.dataframe(dados_logs, use_container_width=True, hide_index=True)
