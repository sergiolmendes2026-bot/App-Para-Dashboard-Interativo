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

# --- BANCO DE DADOS E DADOS DE DEMONSTRAÇÃO ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    conn.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    
    # Popular dados falsos caso esteja vazio para aparecerem os gráficos imediatamente
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vendas")
    if cursor.fetchone()[0] == 0:
        conn.executemany("INSERT INTO vendas (cliente, valor, data, responsavel, status, produto) VALUES (?, ?, ?, ?, ?, ?)", [
            ("Empresa Alpha", 15000.0, "2026-06-01", "Carlos", "Pago", "Software A"),
            ("Empresa Beta", 25000.0, "2026-06-05", "Ana", "Pago", "Software B"),
            ("Empresa Gama", 10000.0, "2026-06-10", "Carlos", "Pago", "Consultoria"),
            ("Empresa Delta", 40000.0, "2026-06-15", "Ana", "Pago", "Software A"),
        ])
    
    cursor.execute("SELECT COUNT(*) FROM pipeline")
    if cursor.fetchone()[0] == 0:
        conn.executemany("INSERT INTO pipeline (titulo, estagio, valor, responsavel) VALUES (?, ?, ?, ?)", [
            ("Projeto X", "Prospecção", 50000.0, "Carlos"),
            ("Projeto Y", "Qualificação", 30000.0, "Ana"),
            ("Projeto Z", "Proposta", 20000.0, "Carlos"),
            ("Projeto W", "Fechamento", 15000.0, "Ana"),
        ])

    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        conn.executemany("INSERT INTO clientes (nome, status, origem, motivo_perda, data) VALUES (?, ?, ?, ?, ?)", [
            ("João Silva", "🆕 Novo Lead", "Google Ads", "", "2026-06-01"),
            ("Maria Souza", "✅ Venda Fechada", "Instagram", "", "2026-06-02"),
            ("Pedro Santos", "❌ Venda Perdida", "Indicação", "Preço Alto", "2026-06-03"),
            ("Ana Paula", "💬 Em Atendimento", "WhatsApp", "", "2026-06-04"),
        ])

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
        
        # 1. Evolução das Vendas (Linha)
        with c_v1:
            st.markdown("#### 📈 1. Evolução das Vendas")
            if not df_vendas.empty and "data" in df_vendas.columns:
                df_temp = df_vendas.copy()
                df_temp['data'] = pd.to_datetime(df_temp['data'], errors='coerce')
                df_v_linha = df_temp.groupby("data")["valor"].sum().reset_index()
                fig_linha = px.line(df_v_linha, x="data", y="valor", markers=True, color_discrete_sequence=[cor_hex])
                fig_linha.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_linha, use_container_width=True)
            else:
                st.info("Sem dados suficientes de vendas.")

        # 2. Meta x Realizado (Gauge)
        with c_v2:
            st.markdown("#### 🎯 2. Meta x Realizado (Gauge)")
            meta_exemplo = 150000.0
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=receita_realizada,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Progresso de Vendas vs Meta"},
                gauge={'axis': {'range': [None, meta_exemplo]}, 'bar': {'color': cor_hex}}
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), height=260)
            st.plotly_chart(fig_gauge, use_container_width=True)

        c_v3, c_v4 = st.columns(2)
        
        # 4. Receita por Vendedor (Barras)
        with c_v3:
            st.markdown("#### 🏆 4. Receita por Vendedor")
            if not df_vendas.empty and "responsavel" in df_vendas.columns:
                df_vend = df_vendas.groupby("responsavel")["valor"].sum().reset_index()
                fig_vend = px.bar(df_vend, x="responsavel", y="valor", color_discrete_sequence=[cor_hex])
                fig_vend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_vend, use_container_width=True)
            else:
                st.info("Sem dados de vendedores.")

        # 7. Produtos Mais Vendidos (Barras Horizontais)
        with c_v4:
            st.markdown("#### 📦 7. Produtos Mais Vendidos")
            if not df_vendas.empty and "produto" in df_vendas.columns:
                df_prod = df_vendas.groupby("produto")["valor"].sum().reset_index()
                fig_prod = px.bar(df_prod, x="valor", y="produto", orientation="h", color_discrete_sequence=[cor_hex])
                fig_prod.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_prod, use_container_width=True)
            else:
                st.info("Sem dados de produtos.")

    with tab2:
        c_p1, c_p2 = st.columns(2)
        
        # 3. Funil de Vendas
        with c_p1:
            st.markdown("#### 📊 3. Funil de Vendas")
            if not df_pipeline.empty and "estagio" in df_pipeline.columns:
                fig_funil = px.funnel(df_pipeline, x="valor", y="estagio", color_discrete_sequence=[cor_hex])
                fig_funil.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_funil, use_container_width=True)
            else:
                st.info("Sem dados no pipeline.")

        with c_p2:
            st.markdown("#### 📈 Valor do Pipeline por Etapa")
            if not df_pipeline.empty and "estagio" in df_pipeline.columns:
                df_pipe_bar = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
                fig_bar_pipe = px.bar(df_pipe_bar, x="valor", y="estagio", orientation="h", color_discrete_sequence=[cor_hex])
                fig_bar_pipe.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_bar_pipe, use_container_width=True)
            else:
                st.info("Sem dados no pipeline.")

    with tab3:
        c_l1, c_l2 = st.columns(2)
        
        # 5. Origem dos Leads (Donut)
        with c_l1:
            st.markdown("#### 🍩 5. Origem dos Leads (Donut)")
            if not df_clientes.empty and "origem" in df_clientes.columns:
                fig_origem = px.pie(df_clientes, names="origem", hole=0.5, color_discrete_sequence=px.colors.qualitative.Prism)
                fig_origem.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_origem, use_container_width=True)
            else:
                st.info("Sem dados de origem.")

        # 6. Clientes por Status
        with c_l2:
            st.markdown("#### 📋 6. Clientes por Status")
            if not df_clientes.empty and "status" in df_clientes.columns:
                df_status = df_clientes.groupby("status").size().reset_index(name="quantidade")
                fig_status = px.bar(df_status, x="status", y="quantidade", color_discrete_sequence=[cor_hex])
                fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Sem dados de status.")

        # 8. Motivos de Perda de Negócios
        st.markdown("#### ❌ 8. Motivos de Perda de Negócios")
        if not df_clientes.empty and "motivo_perda" in df_clientes.columns:
            df_perda = df_clientes[df_clientes["motivo_perda"].str.strip() != ""]
            if not df_perda.empty:
                df_perda_group = df_perda.groupby("motivo_perda").size().reset_index(name="quantidade")
                fig_perda = px.bar(df_perda_group, x="motivo_perda", y="quantidade", color_discrete_sequence=["#EF4444"])
                fig_perda.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_perda, use_container_width=True)
            else:
                st.info("Nenhum motivo de perda registrado.")
        else:
            st.info("Sem dados de perda.")

# --- CLIENTES ---
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

# --- LEADS ---
elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    df_leads_only = df_clientes[df_clientes["status"].str.contains("Lead|Contato|Atendimento|Novo", case=False, na=False)] if not df_clientes.empty and "status" in df_clientes.columns else pd.DataFrame()
    if not df_leads_only.empty:
        colunas_mostrar = [c for c in ["nome", "empresa", "email", "telefone", "origem", "status", "data"] if c in df_leads_only.columns]
        st.dataframe(df_leads_only[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead em aberto no momento.")

# --- PIPELINE ---
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
                    INSERT INTO pipeline (titulo, estagio, valor, empresa, contato, telefone, responsavel, origem) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (p_titulo, p_estagio, p_valor, p_empresa, p_contato, p_telefone, "Comercial", "Direto"))
                conn.commit()
                conn.close()
                st.success("Negócio adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Informe o título do negócio.")

# --- VENDAS ---
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
        col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
        with col_v1:
            v_cliente = st.text_input("Cliente *")
        with col_v2:
            v_valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
        with col_v3:
            v_produto = st.text_input("Produto", value="Software A")
        with col_v4:
            v_resp = st.text_input("Responsável", value="Carlos")
        with col_v5:
            v_data = st.text_input("Data (AAAA-MM-DD)", value=str(date.today()))
            
        btn_venda = st.form_submit_button("Registrar Venda")
        if btn_venda:
            if v_cliente and v_valor > 0:
                conn = conectar()
                tinfo = [col[1] for col in conn.execute("PRAGMA table_info(vendas)").fetchall()]
                if "produto" not in tinfo:
                    conn.execute("ALTER TABLE vendas ADD COLUMN produto TEXT")
                
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel, status, produto) VALUES (?, ?, ?, ?, ?, ?)", 
                           (v_cliente, v_valor, v_data, v_resp, "Pago", v_produto))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o cliente e um valor válido.")

# --- RELATÓRIOS ---
elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação")
    df_export = df_vendas if not df_vendas.empty else pd.DataFrame(columns=['cliente', 'valor', 'data', 'responsavel', 'status', 'produto'])
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Exportar Dados para CSV", data=csv_data, file_name="vendas_crm.csv", mime="text/csv")

# --- INTEGRAÇÕES ---
elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.toggle("Ativar Integração WhatsApp", value=True)

# --- CONFIGURAÇÕES ---
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
    if st.button("Salvar Configurações"):
        st.success("Configurações atualizadas!")
        st.rerun()
