import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="CRM Comercial Profissional", page_icon="📊", layout="wide"
)

# --- INICIALIZAÇÃO DO ESTADO PARA APARÊNCIA E NAVEGAÇÃO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro"
if "cor_principal_sistema" not in st.session_state:
    st.session_state.cor_principal_sistema = "🔵 Azul"
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

# Mapeamento de cores da interface
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

# --- APLICAÇÃO DINÂMICA DE CSS ---
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_app};
            color: {text_app};
        }}
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
        }}
        div.stButton > button:first-child {{
            background-color: {cor_hex} !important;
            color: white !important;
            border: none !important;
        }}
        h1, h2, h3, h4 {{
            color: {text_app};
        }}
        /* Estilização personalizada para os botões da Sidebar */
        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%;
            text-align: left;
            background-color: transparent !important;
            color: #94a3b8 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            transition: all 0.2s ease-in-out;
        }}
        [data-testid="stSidebar"] div.stButton > button:hover {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #ffffff !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO E MIGRAÇÃO AUTOMÁTICA DO BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    
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
    
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(clientes)")
    colunas_existentes_clientes = [col[1] for col in cursor.fetchall()]
    novas_colunas_clientes = {"origem": "TEXT", "motivo_perda": "TEXT", "data_fechamento": "TEXT", "responsavel": "TEXT"}
    for coluna, tipo in novas_colunas_clientes.items():
        if coluna not in colunas_existentes_clientes:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}")

    cursor.execute("PRAGMA table_info(pipeline)")
    colunas_existentes_pipeline = [col[1] for col in cursor.fetchall()]
    novas_colunas_pipeline = {"empresa": "TEXT", "contato": "TEXT", "telefone": "TEXT", "email": "TEXT", "responsavel": "TEXT", "origem": "TEXT"}
    for coluna, tipo in novas_colunas_pipeline.items():
        if coluna not in colunas_existentes_pipeline:
            conn.execute(f"ALTER TABLE pipeline ADD COLUMN {coluna} {tipo}")

    cursor.execute("PRAGMA table_info(vendas)")
    colunas_existentes_vendas = [col[1] for col in cursor.fetchall()]
    if "status" not in colunas_existentes_vendas:
        conn.execute("ALTER TABLE vendas ADD COLUMN status TEXT")
            
    conn.commit()
    conn.close()

inicializar_banco()

# --- BARRA LATERAL PERSONALIZADA ---
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px 5px 20px 5px;">
            <div style="background-color: {cor_hex}; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">📊</div>
            <div>
                <div style="font-weight: bold; font-size: 16px; color: {text_app}; line-height: 1.2;">CRM</div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; font-weight: 600;">COMERCIAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    menu_itens = [
        ("Dashboard", "📊"),
        ("Clientes", "👥"),
        ("Leads", "👤"),
        ("Pipeline", "📈"),
        ("Vendas", "🏆"),
        ("Relatórios", "📄"),
        ("Integrações", "🔌"),
        ("Configurações", "⚙️")
    ]

    for nome_pagina, icone in menu_itens:
        is_ativo = st.session_state.selected == nome_pagina
        # Se for o item ativo, aplicamos estilo visual destacado diretamente no botão
        if is_ativo:
            if st.button(f"{icone}  {nome_pagina}", key=f"btn_{nome_pagina}", use_container_width=True):
                st.session_state.selected = nome_pagina
            # Injeta estilo dinâmico de ativo por cima do botão correspondente
            st.markdown(f"""
                <style>
                    div[data-testid="stSidebar"] button[kind="secondary"]:has(div:text-matches("{nome_pagina}", "i")) {{
                        background-color: {cor_hex} !important;
                        color: #ffffff !important;
                        font-weight: 600 !important;
                        box-shadow: 0 4px 12px {cor_hex}40 !important;
                    }}
                </style>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"{icone}  {nome_pagina}", key=f"btn_{nome_pagina}", use_container_width=True):
                st.session_state.selected = nome_pagina
                st.rerun()

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

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and "valor" in df_vendas.columns and len(df_vendas) > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Leads", f"{total_leads}")
    k2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    k3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    k4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("#### 📊 1. Vendas por mês (Barras)")
        if not df_vendas.empty and "data" in df_vendas.columns and "valor" in df_vendas.columns:
            df_vendas['mes'] = pd.to_datetime(df_vendas['data'], errors='coerce').dt.strftime('%b').fillna('Outros')
            df_vendas_grouped = df_vendas.groupby("mes")["valor"].sum().reset_index()
            
            fig_vendas = px.bar(
                df_vendas_grouped, x="mes", y="valor", 
                labels={"mes": "", "valor": "R$"},
                color_discrete_sequence=[cor_hex]
            )
            fig_vendas.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_app), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#1e293b")
            )
            st.plotly_chart(fig_vendas, use_container_width=True)
        else:
            df_demo = pd.DataFrame({"mes": ["Jan", "Fev", "Mar", "Abr"], "valor": [30000, 50000, 70000, 90000]})
            fig_vendas = px.bar(
                df_demo, x="mes", y="valor", labels={"mes": "", "valor": "R$"},
                color_discrete_sequence=[cor_hex]
            )
            fig_vendas.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_app), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#1e293b")
            )
            st.plotly_chart(fig_vendas, use_container_width=True)

    with col_g2:
        st.markdown("#### 🥧 2. Pizza do Pipeline")
        cores_pipeline = [cor_hex, "#10B981", "#F59E0B", "#EF4444", "#BE185D"]

        if not df_pipeline.empty and "estagio" in df_pipeline.columns and "valor" in df_pipeline.columns:
            df_pipe_grouped = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
            fig_pipe = px.pie(
                df_pipe_grouped, names="estagio", values="valor", hole=0.4,
                color_discrete_sequence=cores_pipeline
            )
            fig_pipe.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
            st.plotly_chart(fig_pipe, use_container_width=True)
        else:
            df_demo_pipe = pd.DataFrame({
                "estagio": ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"],
                "porcentagem": [35, 25, 20, 12, 8]
            })
            fig_pipe = px.pie(
                df_demo_pipe, names="estagio", values="porcentagem", hole=0.4,
                color_discrete_sequence=cores_pipeline
            )
            fig_pipe.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
            st.plotly_chart(fig_pipe, use_container_width=True)

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro Completo de Clientes e Leads")
    with st.form("form_cliente_completo", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_contato = st.text_input("Nome do Contato *")
            nome_empresa = st.text_input("Nome da Empresa")
            email_cli = st.text_input("E-mail")
            telefone_cli = st.text_input("Telefone / WhatsApp")
            regiao_cli = st.selectbox("Região", ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"])
        with col_c2:
            origem_cli = st.selectbox("Origem do Lead", ["Indicação", "Instagram", "Google Ads", "WhatsApp", "Prospecção Ativa", "Site"])
            status_opcoes = [
                "🆕 Novo Lead", "📞 Primeiro Contato", "💬 Em Atendimento",
                "📋 Proposta Enviada", "⏳ Aguardando Resposta", "🤝 Negociação",
                "✅ Venda Fechada", "❌ Venda Perdida", "🔄 Pós-Venda"
            ]
            status_cli = st.selectbox("Status do Cliente", status_opcoes)
            motivo_cli = st.text_input("Motivo de Perda (Se aplicável)")
            responsavel_cli = st.text_input("Responsável Comercial", value="Equipe Comercial")
            data_cad = st.text_input("Data de Cadastro", value=str(date.today()))
            data_fech = st.text_input("Data de Fechamento", value="")
            
        submitted_cli = st.form_submit_button("Salvar Cliente no CRM")
        if submitted_cli:
            if nome_contato:
                conn = conectar()
                conn.execute("""
                    INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, origem, motivo_perda, data, data_fechamento, responsavel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome_contato, nome_empresa, email_cli, telefone_cli, regiao_cli, status_cli, origem_cli, motivo_cli, data_cad, data_fech, responsavel_cli))
                conn.commit()
                conn.close()
                st.success("Cliente cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha ao menos o Nome do Contato.")

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Base de Dados Geral (CRM)")
    if not df_clientes.empty:
        colunas_mostrar = [c for c in ['nome', 'empresa', 'telefone', 'origem', 'status', 'responsavel', 'data'] if c in df_clientes.columns]
        st.dataframe(df_clientes[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    df_leads_only = df_clientes[df_clientes["status"].str.contains("Lead|Contato|Atendimento", case=False, na=False)] if not df_clientes.empty and "status" in df_clientes.columns else pd.DataFrame()
    if not df_leads_only.empty:
        colunas_mostrar = [c for c in ["nome", "empresa", "email", "telefone", "origem", "status", "data"] if c in df_leads_only.columns]
        st.dataframe(df_leads_only[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead em aberto no momento.")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    with st.form("form_pipeline", clear_on_submit=True):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_titulo = st.text_input("Título do Negócio *")
            p_empresa = st.text_input("Empresa")
        with col_p2:
            p_estagio = st.selectbox("Estágio", ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"])
            p_contato = st.text_input("Contato")
        with col_p3:
            p_valor = st.number_input("Valor Estimado (R$)", min_value=0.0, step=100.0)
            p_telefone = st.text_input("Telefone")
            
        btn_pipe = st.form_submit_button("Adicionar Negócio ao Pipeline")
        if btn_pipe:
            if p_titulo:
                conn = conectar()
                conn.execute("""
                    INSERT INTO pipeline (titulo, estagio, valor, empresa, contato, telefone, responsavel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_titulo, p_estagio, p_valor, p_empresa, p_contato, p_telefone, "Comercial"))
                conn.commit()
                conn.close()
                st.success("Negócio adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Informe o título do negócio.")

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas Fechadas")
    faturamento_total = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    total_vendas_count = len(df_vendas) if not df_vendas.empty else 0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and total_vendas_count > 0 else 0.0

    vk1, vk2, vk3 = st.columns(3)
    vk1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
    vk2.metric("📦 Total de Vendas", f"{total_vendas_count}")
    vk3.metric("📈 Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    with st.form("form_venda", clear_on_submit=True):
        col_v1, col_v2, col_v3, col_v4 = st.columns(4)
        with col_v1:
            v_cliente = st.text_input("Cliente *")
        with col_v2:
            v_valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
        with col_v3:
            v_resp = st.text_input("Responsável", value="Comercial")
        with col_v4:
            v_data = st.text_input("Data", value=str(date.today()))
            
        btn_venda = st.form_submit_button("Registrar Venda")
        if btn_venda:
            if v_cliente and v_valor > 0:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel, status) VALUES (?, ?, ?, ?, ?)", 
                             (v_cliente, v_valor, v_data, v_resp, "Pago"))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o cliente e um valor válido.")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação")
    df_export = df_vendas if not df_vendas.empty else pd.DataFrame(columns=['cliente', 'valor', 'data', 'responsavel', 'status'])
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Exportar Dados para CSV", data=csv_data, file_name="vendas_crm.csv", mime="text/csv")

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.toggle("Ativar Integração WhatsApp", value=True)

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    st.markdown("---")
    
    st.markdown("#### 🎨 Aparência")
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        st.radio("Tema", ["🌙 Escuro", "☀️ Claro"], key="tema_sistema")
    with col_ap2:
        st.radio("Cor principal", ["🔵 Azul", "🟢 Verde", "🟣 Roxo"], key="cor_principal_sistema")

    st.markdown("---")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("🏢 Dados da Organização")
        st.text_input("Nome da Organização", value="Comercial Alpha LTDA")
        st.text_input("CNPJ")
        st.text_input("E-mail de Suporte")
    with col_c2:
        st.subheader("🛠 Preferências Gerais")
        st.selectbox("Moeda Padrão", ["Real (BRL - R$)", "Dólar (USD - $)", "Euro (EUR - €)"])
        st.selectbox("Fuso Horário", ["(GMT-03:00) Horário de Brasília"])

    st.markdown("---")
    if st.button("Salvar Configurações"):
        st.success("Configurações e aparências atualizadas com sucesso!")
        st.rerun()
