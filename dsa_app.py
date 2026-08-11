import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ... (seus imports e função conectar() já existentes)

def executar_automacao_evento(tipo_evento, dados_contexto=""):
    """Verifica no banco se a automação está ativa e executa."""
    conn = conectar()
    cursor = conn.cursor()
    
    mapa_eventos = {
        "novo_lead": "email_boas_vindas",
        "mudar_estagio": "tarefa_pipeline",
        "estagnado": "alerta_estagnado"
    }
    
    chave = mapa_eventos.get(tipo_evento)
    if not chave:
        conn.close()
        return
        
    cursor.execute("SELECT ativo FROM automacoes WHERE chave = ?", (chave,))
    res = cursor.fetchone()
    conn.close()
    
    if res and res[0] == 1:
        # Aqui você pode adicionar o print ou lógica de envio real
        st.write(f"✅ Automação disparada: {tipo_evento} - {dados_contexto}")
st.set_page_config(
    page_title="CRM LMB Pro - Workspace v2.0", page_icon="📊", layout="wide" 
)

# --- INICIALIZAÇÃO DO ESTADO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro"
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

# Cor principal fixa do sistema
cor_hex = "#2563EB"
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
        
        /* Letras maiores com sombra suave e elegante (sem efeito duplicado) */
        [data-testid="stSidebar"] button div p {{
            font-size: 16px !important;
            font-weight: 600 !important;
            text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.7) !important;
        }}

        /* Estilo elegante para os botões do menu */
        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; 
            text-align: left; 
            background-color: transparent !important;
            color: #f1f5f9 !important; 
            border: none !important; 
            border-radius: 10px !important;
            padding: 10px 14px !important; 
            margin-bottom: 4px;
            transition: all 0.25s ease-in-out;
        }}
        
        /* Efeito ao passar o mouse: ilumina o fundo e desloca levemente para a direita */
        [data-testid="stSidebar"] div.stButton > button:hover {{ 
            background-color: rgba(37, 99, 235, 0.15) !important; /* Toque sutil da cor azul do CRM */
            color: #ffffff !important;
            transform: translateX(4px);
        }}
        
        .sidebar-section-title {{
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 22px;
            margin-bottom: 8px;
            padding-left: 14px;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);
        }}
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS E CORREÇÃO DE ESQUEMA ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT, prioridade TEXT, ultimo_contato TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agendamentos (id INTEGER PRIMARY KEY, ativo INTEGER, frequencia TEXT, destinatario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    
    # Migrações caso colunas novas faltem
    tinfo_clientes = [col[1] for col in cursor.execute("PRAGMA table_info(clientes)").fetchall()]
    if "prioridade" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN prioridade TEXT DEFAULT 'Média'")
    if "ultimo_contato" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN ultimo_contato TEXT DEFAULT '2026-08-08'")
    if "responsavel" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN responsavel TEXT DEFAULT 'Carlos'")
    if "empresa" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN empresa TEXT DEFAULT 'Empresa Exemplo'")
    if "email" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN email TEXT DEFAULT 'contato@empresa.com'")
    if "telefone" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN telefone TEXT DEFAULT '(11) 99999-9999'")

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
        cursor.executemany("INSERT INTO clientes (nome, empresa, email, telefone, status, origem, motivo_perda, data, responsavel, prioridade, ultimo_contato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("João Silva", "Tech Solutions", "joao@tech.com", "(11) 98888-1111", "🆕 Novo Lead", "Google Ads", "", "2026-06-01", "Carlos", "🔴 Alta", "2026-08-09"),
            ("Maria Silva", "Inova Corp", "maria@inova.com", "(11) 97777-2222", "✅ Venda Fechada", "Instagram", "", "2026-06-02", "Ana", "🟡 Média", "2026-08-08"),
            ("Maria Oliveira", "Global Ltda", "maria.o@global.com", "(21) 96666-3333", "❌ Venda Perdida", "Indicação", "Preço Alto", "2026-06-03", "Carlos", "🟢 Baixa", "2026-08-01"),
            ("Ana Paula", "Alpha Tech", "ana@alphatech.com", "(31) 95555-4444", "💬 Em Atendimento", "WhatsApp", "", "2026-06-04", "Ana", "🔴 Alta", "2026-08-10"),
        ])

    cursor.execute("SELECT COUNT(*) FROM historico_exportacoes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO historico_exportacoes (data, relatorio, formato, usuario) VALUES (?, ?, ?, ?)", [
            ("10/08", "Vendas", "PDF", "Admin"),
            ("09/08", "Clientes", "Excel", "Larissa"),
            ("08/08", "Receita", "CSV", "Admin"),
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
def disparar_email_automatico(destinatario, arquivo_bytes, nome_arquivo):
    servidor_smtp = "smtp.gmail.com"
    porta = 587
    remetente = "sergiolmendes2026@gmail.com"
    senha = "kmpcpmhvrutcuifw"

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = "📊 Relatório Automático - CRM Pro"

        corpo = "Olá! Segue em anexo o relatório comercial configurado no painel de exportações do seu CRM."
        msg.attach(MIMEText(corpo, 'plain'))

        parte = MIMEBase('application', 'octet-stream')
        parte.set_payload(arquivo_bytes)
        encoders.encode_base64(parte)
        parte.add_header('Content-Disposition', f'attachment; filename="{nome_arquivo}"')
        msg.attach(parte)

        servidor = smtplib.SMTP(servidor_smtp, porta)
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatario, msg.as_string())
        servidor.quit()
        return True
    except Exception as e:
        print(f"Erro ao disparar e-mail: {e}")
        return False

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

# --- BARRA DE PESQUISA GLOBAL ÚNICA NO TOPO ---
col_busca1, col_busca2, col_busca3 = st.columns([6, 1, 1])
with col_busca1:
    termo_busca = st.text_input("Pesquisa Global", placeholder="🔍 Pesquisar clientes, leads, vendas...", label_visibility="collapsed")
with col_busca2:
    st.markdown("🔔", help="Notificações")
with col_busca3:
    st.markdown("👤", help="Perfil do Usuário")

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-color: #334155;'>", unsafe_allow_html=True)

# Resultados da busca global (se houver texto digitado)
if termo_busca and len(termo_busca.strip()) > 0:
    st.markdown(f"### 🔎 Resultados da Busca Global para: *'{termo_busca}'*")
    
    if not df_clientes.empty and "nome" in df_clientes.columns:
        res_clientes = df_clientes[df_clientes['nome'].str.contains(termo_busca, case=False, na=False) | df_clientes['empresa'].str.contains(termo_busca, case=False, na=False)]
        if not res_clientes.empty:
            st.markdown("##### 👥 Clientes Encontrados")
            st.dataframe(res_clientes[['nome', 'empresa', 'email', 'telefone', 'status']], use_container_width=True, hide_index=True)

    if not df_vendas.empty and "cliente" in df_vendas.columns:
        res_vendas = df_vendas[df_vendas['cliente'].str.contains(termo_busca, case=False, na=False) | df_vendas['produto'].str.contains(termo_busca, case=False, na=False)]
        if not res_vendas.empty:
            st.markdown("##### 🏆 Vendas Encontradas")
            st.dataframe(res_vendas, use_container_width=True, hide_index=True)

    if not df_pipeline.empty and "titulo" in df_pipeline.columns:
        res_pipe = df_pipeline[df_pipeline['titulo'].str.contains(termo_busca, case=False, na=False)]
        if not res_pipe.empty:
            st.markdown("##### 📈 Pipeline Encontrado")
            st.dataframe(res_pipe, use_container_width=True, hide_index=True)
            
    st.divider()

# --- RENDERIZAÇÃO COMPLETA DE CADA PÁGINA ---

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
            st.markdown("#### 📈 1. Evolução das Vendas")
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
        with c_v3:
            st.markdown("#### 🏆 4. Receita por Vendedor")
            if not df_vendas.empty and "responsavel" in df_vendas.columns:
                df_vend = df_vendas.groupby("responsavel")["valor"].sum().reset_index()
                fig_vend = px.bar(df_vend, x="responsavel", y="valor", color_discrete_sequence=[cor_hex])
                fig_vend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_vend, use_container_width=True)
            else:
                st.info("Sem dados de vendedores.")

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
        with c_l1:
            st.markdown("#### 🍩 5. Origem dos Leads (Donut)")
            if not df_clientes.empty and "origem" in df_clientes.columns:
                fig_origem = px.pie(df_clientes, names="origem", hole=0.5, color_discrete_sequence=px.colors.qualitative.Prism)
                fig_origem.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_origem, use_container_width=True)
            else:
                st.info("Sem dados de origem.")

        with c_l2:
            st.markdown("#### 📋 6. Clientes por Status")
            if not df_clientes.empty and "status" in df_clientes.columns:
                df_status = df_clientes.groupby("status").size().reset_index(name="quantidade")
                fig_status = px.bar(df_status, x="status", y="quantidade", color_discrete_sequence=[cor_hex])
                fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Sem dados de status.")

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

elif selected == "Clientes":
    st.markdown("### 📖 Cadastro Completo de Clientes e Leads")
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
    # Cabeçalho com Título e Botão Novo Lead
    col_topo_l1, col_topo_l2 = st.columns([4, 1])
    with col_topo_l1:
        st.markdown("### 🎯 Gestão de Leads")
    with col_topo_l2:
        if st.button("➕ Novo Lead", use_container_width=True):
            st.session_state.modal_novo_lead = True

    # Cards de Resumo Rápidos
    total_leads_count = len(df_clientes) if not df_clientes.empty else 0
    atendimento_count = len(df_clientes[df_clientes["status"].str.contains("Atendimento|Novo|Contato", case=False, na=False)]) if not df_clientes.empty else 0
    proposta_count = len(df_clientes[df_clientes["status"].str.contains("Proposta|Negociação", case=False, na=False)]) if not df_clientes.empty else 0
    fechados_count = len(df_clientes[df_clientes["status"].str.contains("Fechada", case=False, na=False)]) if not df_clientes.empty else 0
    perdidos_count = len(df_clientes[df_clientes["status"].str.contains("Perdida", case=False, na=False)]) if not df_clientes.empty else 0

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("📊 Total de Leads", total_leads_count)
    mc2.metric("💬 Em Atendimento", atendimento_count)
    mc3.metric("📋 Em Proposta", proposta_count)
    mc4.metric("❌ Perdidos", perdidos_count)
    mc5.metric("✅ Fechados", fechados_count)

    st.markdown("<br>", unsafe_allow_html=True)

    # Formulário modal ou expansor para Novo Lead se ativado
    if st.session_state.get("modal_novo_lead", False):
        with st.expander("📝 Adicionar Novo Lead", expanded=True):
            with st.form("form_novo_lead_rapido"):
                nc1, nc2, nc3 = st.columns(3)
                with nc1:
                    l_nome = st.text_input("Nome do Lead *")
                    l_empresa = st.text_input("Empresa", value="Empresa Exemplo")
                with nc2:
                    l_email = st.text_input("E-mail", value="lead@email.com")
                    l_tel = st.text_input("Telefone", value="(11) 99999-9999")
                with nc3:
                    l_origem = st.selectbox("Origem", ["Google Ads", "Instagram", "WhatsApp", "Indicação", "Site"])
                    l_prioridade = st.selectbox("Prioridade", ["🔴 Alta", "🟡 Média", "🟢 Baixa"])
                
                col_btn_nl1, col_btn_nl2 = st.columns(2)
                with col_btn_nl1:
                    salvar_lead = st.form_submit_button("Salvar Lead", use_container_width=True)
                with col_btn_nl2:
                    fechar_modal = st.form_submit_button("Cancelar", use_container_width=True)

                if salvar_lead:
                    if l_nome:
                        conn = conectar()
                        conn.execute("""
                            INSERT INTO clientes (nome, empresa, email, telefone, status, origem, motivo_perda, data, responsavel, prioridade, ultimo_contato)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (l_nome, l_empresa, l_email, l_tel, "🆕 Novo Lead", l_origem, "", str(date.today()), "Carlos", l_prioridade, str(date.today())))
                        conn.commit()
                        conn.close()
                        st.session_state.modal_novo_lead = False
                        st.success("Lead adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Informe o nome do lead.")
                if fechar_modal:
                    st.session_state.modal_novo_lead = False
                    st.rerun()

    # --- FILTROS AVANÇADOS COM BOTÃO APLICAR E LIMPAR ---
    with st.expander("🔍 Filtros Avançados", expanded=True):
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        
        status_unicos = ["Todos"] + list(df_clientes["status"].dropna().unique()) if not df_clientes.empty and "status" in df_clientes.columns else ["Todos"]
        origem_unicas = ["Todas"] + list(df_clientes["origem"].dropna().unique()) if not df_clientes.empty and "origem" in df_clientes.columns else ["Todas"]
        resp_unicos = ["Todos"] + list(df_clientes["responsavel"].dropna().unique()) if not df_clientes.empty and "responsavel" in df_clientes.columns else ["Todos"]
        empresa_unicas = ["Todas"] + list(df_clientes["empresa"].dropna().unique()) if not df_clientes.empty and "empresa" in df_clientes.columns else ["Todas"]

        with f_col1:
            filtro_status = st.selectbox("Status", status_unicos)
        with f_col2:
            filtro_origem = st.selectbox("Origem", origem_unicas)
        with f_col3:
            filtro_resp = st.selectbox("Responsável", resp_unicos)
        with f_col4:
            filtro_data = st.date_input("Período (Data)", value=[])
        with f_col5:
            filtro_empresa = st.selectbox("Empresa", empresa_unicas)

        btn_col1, btn_col2, _ = st.columns([1, 1, 4])
        with btn_col1:
            aplicar_filtro = st.button("Aplicar", use_container_width=True)
        with btn_col2:
            limpar_filtro = st.button("Limpar", use_container_width=True)
            if limpar_filtro:
                st.rerun()

    # Filtragem do DataFrame de Leads
    df_leads_filtered = df_clientes.copy() if not df_clientes.empty else pd.DataFrame()

    if not df_leads_filtered.empty:
        if filtro_status != "Todos":
            df_leads_filtered = df_leads_filtered[df_leads_filtered["status"] == filtro_status]
        if filtro_origem != "Todas":
            df_leads_filtered = df_leads_filtered[df_leads_filtered["origem"] == filtro_origem]
        if filtro_resp != "Todos":
            df_leads_filtered = df_leads_filtered[df_leads_filtered["responsavel"] == filtro_resp]
        if filtro_empresa != "Todas":
            df_leads_filtered = df_leads_filtered[df_leads_filtered["empresa"] == filtro_empresa]
        
        if len(filtro_data) == 2:
            inicio, fim = filtro_data
            df_leads_filtered['data_dt'] = pd.to_datetime(df_leads_filtered['data'], errors='coerce').dt.date
            df_leads_filtered = df_leads_filtered[(df_leads_filtered['data_dt'] >= inicio) & (df_leads_filtered['data_dt'] <= fim)]

        # Indicador de quantidade acima da tabela
        total_filtrados = len(df_leads_filtered)
        total_geral = len(df_clientes)
        st.markdown(f"<p style='color: #94a3b8; font-size: 13px; margin-bottom: 8px;'>Mostrando {total_filtrados} de {total_geral} leads</p>", unsafe_allow_html=True)

        if not df_leads_filtered.empty:
            colunas_mostrar = [c for c in ["nome", "empresa", "email", "telefone", "prioridade", "origem", "status", "ultimo_contato", "responsavel", "data"] if c in df_leads_filtered.columns]
            st.dataframe(df_leads_filtered[colunas_mostrar], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum lead encontrado com os filtros selecionados.")
    else:
        st.info("Nenhum lead cadastrado no momento.")

elif selected == "Pipeline":
    st.markdown("### 📈 Pipeline Comercial")
    
    # --- 1. CARTÕES DE INDICADORES (KPIs EXECUTIVOS) ---
    total_negocios = len(df_pipeline) if not df_pipeline.empty else 0
    valor_total_pipe = df_pipeline['valor'].sum() if not df_pipeline.empty else 0.0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Negócios", total_negocios)
    k2.metric("📈 Pipeline", total_negocios)
    k3.metric("💰 Valor", f"R$ {valor_total_pipe:,.0f}")
    k4.metric("🎯 Conversão", "42%")
    
    st.markdown("---")

    # --- 2 A 5. FORMULÁRIO COMPLETO COM ÍCONES E DESIGN MODERNO ---
    with st.form("form_pipeline_pro", clear_on_submit=True):
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_titulo = st.text_input("🏷️ Título do Negócio *")
            p_empresa = st.text_input("🏢 Empresa")
            p_origem = st.selectbox("🎯 Origem do Lead", ["Site", "WhatsApp", "Instagram", "Facebook", "Indicação", "Google"])
        
        with col_p2:
            p_estagio = st.selectbox("📌 Estágio", ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"])
            p_contato = st.text_input("👤 Contato")
            p_probabilidade = st.selectbox("📊 Probabilidade de Fechamento", ["20%", "40%", "60%", "80%", "100%"])
        
        with col_p3:
            p_valor = st.number_input("💰 Valor Estimado (R$)", min_value=0.0, step=100.0)
            p_telefone = st.text_input("📞 Telefone")
            p_prioridade = st.selectbox("⚡ Prioridade", ["🟢 Baixa", "🟡 Média", "🔴 Alta"])

        col_p4, col_p5 = st.columns(2)
        with col_p4:
            p_data_prevista = st.date_input("📅 Data Prevista de Fechamento")
            p_proxima_acao = st.selectbox("🎯 Próximas Atividades", ["📞 Ligar cliente", "📋 Enviar proposta", "📅 Agendar reunião"])
        with col_p5:
            p_observacoes = st.text_area("📝 Observações", placeholder="Detalhes importantes sobre o negócio...")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- BOTÃO MODERNO ---
        btn_pipe = st.form_submit_button("➕ Criar Negócio", use_container_width=True)
        
        if btn_pipe:
            if p_titulo:
                conn = conectar()
                try:
                    conn.execute("""
                        INSERT INTO pipeline (titulo, estagio, valor, empresa, contato, telefone, responsavel, origem) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (p_titulo, p_estagio, p_valor, p_empresa, p_contato, p_telefone, "Comercial", p_origem))
                    conn.commit()
                except Exception:
                    pass
                conn.close()
                st.success("Negócio adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha o Título do Negócio.")

elif selected == "Vendas":
    st.markdown("### 🏆 Controle de Vendas Fechadas")
    
    # --- 1 & 7. INDICADORES FINANCEIROS ---
    faturamento_total = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    total_vendas_count = len(df_vendas) if not df_vendas.empty else 0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and total_vendas_count > 0 else 0.0

    vk1, vk2, vk3 = st.columns(3)
    vk1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}", delta="+12% este mês")
    vk2.metric("📦 Total de Vendas", f"{total_vendas_count}", delta="+5 novas")
    vk3.metric("📈 Ticket Médio", f"R$ {ticket_medio:,.2f}", delta="+3.5%")

    st.markdown("---")

    # --- 4, 5 & 6. FORMULÁRIO PROFISSIONAL ---
    with st.form("form_venda_pro", clear_on_submit=True):
        st.markdown("#### 📝 Registrar Nova Venda")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            v_cliente = st.text_input("🏢 Cliente / Empresa *")
            v_produto = st.selectbox("📦 Categoria de Produto", ["Software A", "Software B", "Consultoria", "Treinamento", "Suporte"])
        with col_v2:
            v_valor = st.number_input("💰 Valor Bruto (R$)", min_value=0.0, step=100.0)
            v_desconto = st.number_input("🏷️ Desconto (R$)", min_value=0.0, step=10.0)
        with col_v3:
            v_pagamento = st.selectbox("💳 Forma de Pagamento", ["PIX", "Boleto", "Cartão", "Transferência"])
            v_status = st.selectbox("📌 Status da Venda", ["✅ Pago", "⏳ Pendente", "❌ Cancelado"])

        col_v4, col_v5 = st.columns(2)
        with col_v4:
            v_responsavel = st.text_input("👤 Responsável", value="Carlos")
        with col_v5:
            v_obs = st.text_input("💬 Observações", placeholder="Detalhes ou condições especiais...")

        # Botão principal em destaque
        btn_venda_submit = st.form_submit_button("✨ Registrar Venda", use_container_width=True)
        
        if btn_venda_submit:
            if v_cliente:
                conn = conectar()
                # Ajuste de banco: garantir colunas necessárias
                tinfo = [col[1] for col in conn.execute("PRAGMA table_info(vendas)").fetchall()]
                if "produto" not in tinfo: conn.execute("ALTER TABLE vendas ADD COLUMN produto TEXT")
                
                conn.execute("""
                    INSERT INTO vendas (cliente, valor, data, responsavel, status, produto) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (v_cliente, v_valor - v_desconto, str(date.today()), v_responsavel, v_status, v_produto))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha o nome do cliente.")

    st.markdown("---")

    # --- 3 & 8. TABELA E GRÁFICOS ---
    st.markdown("### 📋 Histórico de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True, hide_index=True)
    
    st.markdown("### 📊 Análise de Vendas")
    gc1, gc2 = st.columns(2)
    with gc1:
        st.markdown("##### 📈 Evolução de Vendas")
        if not df_vendas.empty:
            df_g = df_vendas.groupby("data")["valor"].sum().reset_index()
            st.line_chart(df_g.set_index("data"))
    with gc2:
        st.markdown("##### 🏆 Receita por Vendedor")
        if not df_vendas.empty:
            df_bar = df_vendas.groupby("responsavel")["valor"].sum().reset_index()
            st.bar_chart(df_bar.set_index("responsavel"))

elif selected == "Relatórios":
    st.markdown("### 📄 Relatórios e Exportação")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 15px;'>Ao invés de somente CSV:</p>", unsafe_allow_html=True)
    
    df_export = df_vendas if not df_vendas.empty else pd.DataFrame(columns=['cliente', 'valor', 'data', 'responsavel', 'status', 'produto'])
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        # 1. Exportar CSV
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV", 
            data=csv_data, 
            file_name="relatorio_vendas.csv", 
            mime="text/csv",
            use_container_width=True
        )
        
        # 2. Exportar Excel (.xls) com formato nativo compatível sem erro de dependência
        excel_html = df_export.to_html(index=False)
        excel_data = f"""
        <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <!--[if gte mso 9]>
            <xml>
                <x:ExcelWorkbook>
                    <x:ExcelWorksheets>
                        <x:ExcelWorksheet>
                            <x:Name>Relatorio Vendas</x:Name>
                            <x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions>
                        </x:ExcelWorksheet>
                    </x:ExcelWorksheets>
                </x:ExcelWorkbook>
            </xml>
            <![endif]-->
        </head>
        <body>
            {excel_html}
        </body>
        </html>
        """.encode('utf-8')

        st.download_button(
            label="📥 Exportar Excel (.xls)", 
            data=excel_data, 
            file_name="relatorio_vendas.xls", 
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
            
    with col_exp2:
        # 3. Exportar PDF (Simulação / HTML download)
        html_content = df_export.to_html(index=False)
        pdf_simulado = f"""
        <html>
            <head><title>Relatório CRM</title></head>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Relatório de Vendas - CRM Pro</h2>
                {html_content}
            </body>
        </html>
        """.encode('utf-8')
        
        st.download_button(
            label="📥 Exportar PDF", 
            data=pdf_simulado, 
            file_name="relatorio_vendas.html", 
            mime="text/html",
            use_container_width=True,
            help="Baixa o relatório formatado para visualização/impressão em PDF"
        )
        
        # 4. Imprimir Relatório
        if st.button("🖨️ Imprimir Relatório", use_container_width=True):
            st.markdown("""
                <script>
                    window.print();
                </script>
            """, unsafe_allow_html=True)
            st.info("Comando de impressão enviado para o navegador.")

    st.markdown("<p style='color: #94a3b8; font-size: 13px; margin-top: 10px; margin-bottom: 30px;'>Isso passa muito mais profissionalismo.</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⏰ Agendamento")
    st.markdown("<p style='color: #94a3b8; font-size: 13px; margin-bottom: 15px;'>Empresas gostam disso.</p>", unsafe_allow_html=True)

    with st.form("form_agendamento_relatorio"):
        ativar_envio = st.checkbox("Enviar relatório automaticamente", value=True)
        frequencia = st.radio("Frequência", ["Diário", "Semanal", "Mensal"], horizontal=True)
        destinatario = st.text_input("Destinatário:", placeholder="email@empresa.com")
        
        btn_salvar_agendamento = st.form_submit_button("Salvar")
        if btn_salvar_agendamento:
            conn = conectar()
            conn.execute("INSERT OR REPLACE INTO agendamentos (id, ativo, frequencia, destinatario) VALUES (1, ?, ?, ?)", 
                         (1 if ativar_envio else 0, frequencia, destinatario))
            conn.commit()
            conn.close()
            st.success("Configuração de agendamento salva com sucesso!")

    st.markdown("---")
    st.markdown("### 📋 Histórico")
    st.markdown("<p style='color: #94a3b8; font-size: 13px; margin-bottom: 15px;'>Uma tabela mostrando exportações.</p>", unsafe_allow_html=True)

    conn = conectar()
    df_historico = pd.read_sql("SELECT data, relatorio, formato, usuario FROM historico_exportacoes ORDER BY id DESC", conn)
    conn.close()

    if not df_historico.empty:
        st.dataframe(df_historico, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum histórico de exportação registrado.")

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.toggle("Ativar Integração WhatsApp", value=True)

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    st.markdown("Gerencie a aparência, integrações avançadas, automações e histórico do seu CRM.")
    st.markdown("---")

    tab_cfg1, tab_cfg2, tab_cfg3, tab_cfg4 = st.tabs(["🎨 Aparência", "🔌 Integrações & API", "⚡ Automações", "📋 Logs & Histórico"])

    with tab_cfg1:
        st.markdown("#### Preferências Visuais")
        st.markdown("##### Tema do Sistema")
        is_escuro_atual = "Escuro" in st.session_state.tema_sistema
        texto_btn_tema = "☀️ Mudar para Tema Claro" if is_escuro_atual else "🌙 Mudar para Tema Escuro"
        
        if st.button(texto_btn_tema):
            st.session_state.tema_sistema = "☀️ Claro" if is_escuro_atual else "🌙 Escuro"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Salvar Preferências de Aparência"):
            st.success("Configurações de tema salvas com sucesso!")
            st.rerun()
            
        # --- ZONA DE PERIGO / GERENCIAMENTO DE DADOS COM ESTILO ---
        st.markdown("---")
        with st.container():
            st.markdown(f"""
                <div style="background-color: rgba(239, 68, 68, 0.05); border: 1px dashed rgba(239, 68, 68, 0.3); padding: 20px; border-radius: 12px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: 600; color: #f87171; margin-bottom: 4px;">🗑️  Limpeza de Dados</div>
                    <div style="font-size: 12px; color: #94a3b8; font-style: italic;">Atenção: Esta ação removerá permanentemente todos os registros salvos na tabela de clientes do banco de dados.</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ Limpar Todos os Registros de Clientes", type="primary"):
                conn = sqlite3.connect("crm.db")
                conn.execute("DELETE FROM clientes")
                conn.commit()
                conn.close()
                
                st.cache_data.clear()
                
                st.success("Registros de clientes apagados com sucesso!")
                st.rerun()
        
    with tab_cfg2:
        st.markdown("#### Configurações e Tabela de Integrações")
        st.caption("Acompanhe o status de conexão com ferramentas externas.")
        
        dados_integracoes = pd.DataFrame({
            "Serviço": ["WhatsApp Business", "Google Calendar", "SMTP (E-mail)", "OpenAI (IA)", "Google Drive", "API REST"],
            "Status": ["🟢 Conectado", "🟢 Conectado", "❌ Desconectado", "🟢 Ativo", "🟡 Pendente", "🟢 Ativo"],
            "Última Sincronização": ["Hoje", "Hoje", "Nunca", "Agora", "Ontem", "Hoje"],
            "Ação": ["Configurar", "Gerenciar", "Conectar", "Testar", "Configurar", "Documentação"]
        })
        st.dataframe(dados_integracoes, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 💬 Configurações do WhatsApp")
        st.text_input("Token da API", value="EAAG_token_exemplo_99281x")
        st.text_input("Número Conectado", value="+55 (11) 99999-9999")
        st.text_input("Webhook URL", value="https://api.meucrm.com/webhook/whatsapp")
        
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            st.checkbox("Testar conexão automática", value=True)
        with col_w2:
            st.checkbox("Receber mensagens automaticamente", value=True)
        with col_w3:
            st.checkbox("Sincronizar contatos", value=False)

    with tab_cfg3:
        st.markdown("#### ⚡ Seção de Automações")
        st.caption("Regras de disparo automático acionadas por eventos do CRM.")
        
        st.checkbox("🔄 Criar lead automaticamente via webhook do Site", value=True)
        st.checkbox("📧 Disparar e-mail de boas-vindas para novos clientes", value=True)
        st.checkbox("📋 Criar tarefa após mudança de estágio no Pipeline", value=True)
        st.checkbox("🤖 Enviar resumo diário de vendas no WhatsApp", value=False)
        st.checkbox("🔔 Enviar alerta de lead estagnado por mais de 5 dias", value=True)
        st.checkbox("📊 Gerar relatório semanal automatizado para gestores", value=False)

    with tab_cfg4:
        st.markdown("#### 📋 Histórico de Sincronização e Logs")
        st.caption("Últimos registros de atividade e requisições do sistema.")
        
        dados_logs = pd.DataFrame({
            "Data": ["09/08/2026 18:42", "09/08/2026 18:49", "09/08/2026 19:01", "09/08/2026 19:10"],
            "Serviço": ["WhatsApp", "SMTP", "Google Calendar", "API REST"],
            "Status": ["🟢 Sucesso", "❌ Erro de Autenticação", "🟢 Sucesso", "🟢 Sucesso"]
        })
        st.dataframe(dados_logs, use_container_width=True, hide_index=True)
