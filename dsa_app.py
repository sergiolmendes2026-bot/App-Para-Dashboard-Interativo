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
from streamlit_option_menu import option_menu

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CRM LMB Pro", layout="wide")

# --- INICIALIZAÇÃO DE ESTADOS ---
if "modal_nova_atividade" not in st.session_state:
    st.session_state.modal_nova_atividade = False
if "modal_novo_lead" not in st.session_state:
    st.session_state.modal_novo_lead = False
if "filtro_atividades" not in st.session_state:
    st.session_state.filtro_atividades = "Todas as atividades"
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro" 
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

# Cores e Variáveis de Tema
is_escuro = "Escuro" in st.session_state.tema_sistema
bg_app = "#0e1117" if is_escuro else "#ffffff"
text_app = "#ffffff" if is_escuro else "#1e293b"
sidebar_bg = "#0b0f19" if is_escuro else "#f8fafc" 
cor_hex = "#2563EB" 

# --- CSS GLOBAL E CENTRALIZADO ---
st.markdown(
    f"""
    <style>
        /* Fundo geral da página com a cor exata solicitada */
        .stApp {{ 
            background-color: #16222A !important; 
            color: {text_app}; 
        }}
        
        /* Sidebar com transparência de vidro fumê e efeito flutuante sobre a nova cor */
        [data-testid="stSidebar"] {{ 
            background: rgba(15, 23, 32, 0.55) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 8px 0 32px rgba(0, 0, 0, 0.5);
            padding: 0 !important;
        }}

        /* Container de Filtros do Dashboard */
        .filtros-container {{
            background-color: #1b2836;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        /* Cards de métricas */
        .metric-card {{
            background-color: #1b2836;
            border: 1px solid #00d2ff;
            border-radius: 10px;
            padding: 20px;
            text-align: left;
            box-shadow: 0 4px 20px rgba(0, 210, 255, 0.12);
        }}

        /* Botões do Menu com efeito translúcido (Marca d'água interna) */
        [data-testid="stSidebar"] div.stButton > button {{
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
            width: 100%; 
            background: rgba(255, 255, 255, 0.01) !important;
            color: #94a3b8 !important; 
            border: 1px solid rgba(255, 255, 255, 0.03) !important; 
            border-radius: 10px !important;
            padding: 11px 16px !important; 
            margin-bottom: 4px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 14px !important;
            font-weight: 500 !important;
        }}
        
        /* Efeito de Marca d'Água nos botões */
        [data-testid="stSidebar"] div.stButton > button::before {{
            content: "";
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 32px;
            height: 32px;
            background-color: currentColor;
            opacity: 0.03;
            pointer-events: none;
        }}

        /* Efeito Hover Moderno nos Botões */
        [data-testid="stSidebar"] div.stButton > button:hover {{ 
            background: rgba(255, 255, 255, 0.06) !important; 
            color: #ffffff !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
            transform: translateX(4px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        }}

        /* Estilização para o item selecionado/ativo do menu */
        .nav-link-selected {{
            background: linear-gradient(90deg, rgba(37, 99, 235, 0.25) 0%, rgba(37, 99, 235, 0.02) 100%) !important;
            color: #ffffff !important;
            border-left: 3px solid #3b82f6 !important;
            border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.15), inset 0 0 15px rgba(59, 130, 246, 0.1);
        }}
        
        /* Divisores internos sutis */
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255, 255, 255, 0.05) !important;
            margin: 14px 16px !important;
        }}
        
        .sidebar-section-title {{
            color: #484f58;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 20px 0 8px 16px;
        }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- BANCO DE DADOS E CORREÇÃO DE ESQUEMA ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT, prioridade TEXT, ultimo_contato TEXT, valor_estimado REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agendamentos (id INTEGER PRIMARY KEY, ativo INTEGER, frequencia TEXT, destinatario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS automacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, chave TEXT, ativo INTEGER)")
    
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
    if "valor_estimado" not in tinfo_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN valor_estimado REAL DEFAULT 0.0")

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
        cursor.executemany("INSERT INTO clientes (nome, empresa, email, telefone, status, origem, motivo_perda, data, responsavel, prioridade, ultimo_contato, valor_estimado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("João Silva", "Tech Solutions", "joao@tech.com", "(11) 98888-1111", "🆕 Novo Lead", "Google Ads", "", "2026-06-01", "Carlos", "🔴 Alta", "2026-08-09", 12000.0),
            ("Maria Silva", "Inova Corp", "maria@inova.com", "(11) 97777-2222", "✅ Venda Fechada", "Instagram", "", "2026-06-02", "Ana", "🟡 Média", "2026-08-08", 25000.0),
            ("Maria Oliveira", "Global Ltda", "maria.o@global.com", "(21) 96666-3333", "❌ Venda Perdida", "Indicação", "Preço Alto", "2026-06-03", "Carlos", "🟢 Baixa", "2026-08-01", 8000.0),
            ("Ana Paula", "Alpha Tech", "ana@alphatech.com", "(31) 95555-4444", "💬 Em Atendimento", "WhatsApp", "", "2026-06-04", "Ana", "🔴 Alta", "2026-08-10", 15000.0),
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

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0px 20px 10px;">
            <span style="font-weight: 700; font-size: 20px; color: white;">📊 CRM PRO</span>
        </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard", "Clientes", "Leads", "Agenda", "Atividades", 
            "---", 
            "Pipeline", "Vendas", "Propostas", "Relatórios", "Metas",
            "---",
            "Campanhas", 
            "---",
            "Usuários", "Permissões", "Notificações", "Configurações"
        ],
        icons=[
            "house", "people", "target", "calendar-event", "clipboard-data", 
            None, 
            "arrow-repeat", "currency-dollar", "file-earmark-text", "graph-up", "mountain",
            None,
            "megaphone", 
            None,
            "person", "shield-lock", "bell", "gear"
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": sidebar_bg},
            "icon": {"color": "#64748b", "font-size": "16px"}, 
            "nav-link": {
                "font-size": "14px", 
                "text-align": "left", 
                "margin": "0px", 
                "color": "#94a3b8", 
                "--hover-color": "#1e293b"
            },
            "nav-link-selected": {
                "background-color": "#1e293b", 
                "color": "white", 
                "border-left": "4px solid #3b82f6"
            },
        }
    )
    st.session_state.selected = selected

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
    
    # --- BARRA DE FILTROS ESTILIZADA ---
    st.markdown('<div class="filtros-container">', unsafe_allow_html=True)
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    with f1:
        st.selectbox("Período", ["Mês Atual", "Últimos 30 dias", "Este Ano", "Personalizado"], key="f_periodo")
    with f2:
        st.selectbox("Produto", ["Todos", "Software A", "Software B", "Consultoria"], key="f_produto")
    with f3:
        st.selectbox("Equipe", ["Todas", "Comercial A", "Comercial B"], key="f_equipe")
    with f4:
        st.selectbox("Compra", ["Todas", "À vista", "Parcelado"], key="f_compra")
    with f5:
        st.selectbox("Consultor", ["Todos", "Carlos", "Ana"], key="f_consultor")
    with f6:
        st.selectbox("Ticket", ["Todos", "Alto", "Médio", "Baixo"], key="f_ticket")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- CARDS DE MÉTRICAS COM BORDA CIANO ---
    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and "valor" in df_vendas.columns and len(df_vendas) > 0 else 0.0

    st.markdown(f"""
        <div style="display: flex; gap: 15px; margin-bottom: 25px;">
            <div class="metric-card" style="flex: 1;">
                <div style="color: #00d2ff; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px;">TOTAL DE LEADS</div>
                <div style="color: white; font-size: 24px; font-weight: 700;">{total_leads}</div>
            </div>
            <div class="metric-card" style="flex: 1;">
                <div style="color: #00d2ff; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px;">VALOR NO PIPELINE</div>
                <div style="color: white; font-size: 24px; font-weight: 700;">R$ {valor_pipeline:,.2f}</div>
            </div>
            <div class="metric-card" style="flex: 1;">
                <div style="color: #00d2ff; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px;">RECEITA REALIZADA</div>
                <div style="color: white; font-size: 24px; font-weight: 700;">R$ {receita_realizada:,.2f}</div>
            </div>
            <div class="metric-card" style="flex: 1;">
                <div style="color: #00d2ff; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px;">TICKET MÉDIO REAL</div>
                <div style="color: white; font-size: 24px; font-weight: 700;">R$ {ticket_medio:,.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ABAS DE GRÁFICOS ---
    tab1, tab2, tab3 = st.tabs(["💰 Vendas & Receita", "🎯 Pipeline & Funil", "👥 Leads & Perdas"])

    with tab1:
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.markdown("#### 📈 1. Evolução das Vendas")
            if not df_vendas.empty and "data" in df_vendas.columns:
                df_temp = df_vendas.copy()
                df_temp['data'] = pd.to_datetime(df_temp['data'], errors='coerce')
                
                df_v_linha = df_temp.groupby(df_temp['data'].dt.strftime('%b/%Y'))["valor"].sum().reset_index()
                
                df_v_linha['mes_ordem'] = pd.to_datetime(df_v_linha['data'], format='%b/%Y')
                df_v_linha = df_v_linha.sort_values('mes_ordem')
                
                fig_linha = px.line(df_v_linha, x="data", y="valor", markers=True)
                
                fig_linha.update_traces(
                    line=dict(color="#38BDF8", width=3),
                    fill='tozeroy',
                    fillcolor="rgba(56, 189, 248, 0.15)"
                )
                
                fig_linha.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color=text_app),
                    xaxis_title="Período"
                )
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
                gauge={
                    'axis': {'range': [None, meta_exemplo]},
                    'bar': {'color': "#2563EB"},
                    'steps': [
                        {'range': [0, meta_exemplo * 0.5], 'color': "#EF4444"},
                        {'range': [meta_exemplo * 0.5, meta_exemplo * 0.8], 'color': "#F59E0B"},
                        {'range': [meta_exemplo * 0.8, meta_exemplo], 'color': "#22C55E"}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': receita_realizada
                    }
                }
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app), height=260)
            st.plotly_chart(fig_gauge, use_container_width=True)

        c_v3, c_v4 = st.columns(2)
        with c_v3:
            st.markdown("#### 🏆 4. Receita por Vendedor")
            if not df_vendas.empty and "responsavel" in df_vendas.columns:
                df_vend = df_vendas.groupby("responsavel")["valor"].sum().reset_index()
                cores_vendedores = {"Ana": "#38BDF8", "Carlos": "#1D4ED8", "Pedro": "#F59E0B", "Julia": "#065CF6"}
                fig_vend = px.bar(df_vend, x="responsavel", y="valor", color="responsavel", color_discrete_map=cores_vendedores)
                fig_vend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
                st.plotly_chart(fig_vend, use_container_width=True)
            else:
                st.info("Sem dados de vendedores.")

        with c_v4:
            st.markdown("#### 📦 7. Produtos Mais Vendidos")
            if not df_vendas.empty and "produto" in df_vendas.columns:
                df_prod = df_vendas.groupby("produto")["valor"].sum().reset_index()
                cores_produtos = ["#2563EB", "#38BDF8", "#60A5FA", "#93C5FD"]
                fig_prod = px.bar(df_prod, x="valor", y="produto", orientation="h", color="produto", color_discrete_sequence=cores_produtos)
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
                
                ordem = ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"]
                df_pipe_bar["estagio"] = pd.Categorical(df_pipe_bar["estagio"], categories=ordem, ordered=True)
                df_pipe_bar = df_pipe_bar.sort_values("estagio")

                cores_pipeline = {
                    "Prospecção": "#38BDF4",
                    "Qualificação": "#8B5CF6",
                    "Proposta": "#F59E0B",
                    "Negociação": "#F97316",
                    "Fechamento": "#22C55E"
                }

                fig_bar_pipe = px.bar(
                    df_pipe_bar, 
                    x="valor", 
                    y="estagio", 
                    orientation="h", 
                    color="estagio", 
                    color_discrete_map=cores_pipeline, 
                    text="valor"
                )
                fig_bar_pipe.update_traces(marker_line_color="white", marker_line_width=1, texttemplate="R$ %{x:,.0f}", textposition="outside")
                fig_bar_pipe.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color=text_app),
                    xaxis_title="Valor (R$)",
                    yaxis_title="",
                    yaxis=dict(autorange="reversed"),
                    margin=dict(l=30, r=40, t=20, b=10)
                )
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
                
                cores_status = {
                    "🆕 Novo Lead": "#38BDF8",
                    "📞 Primeiro Contato": "#60A5FA",
                    "💬 Em Atendimento": "#8B5CF6",
                    "📋 Proposta Enviada": "#F59E0B",
                    "⏳ Aguardando Resposta": "#FBBF24",
                    "🤝 Negociação": "#F97316",
                    "✅ Venda Fechada": "#22C55E",
                    "❌ Venda Perdida": "#EF4444",
                    "🔄 Pós-Venda": "#10B981"
                }
                
                fig_status = px.bar(
                    df_status, 
                    x="status", 
                    y="quantidade", 
                    color="status", 
                    color_discrete_map=cores_status,
                    text="quantidade"
                )
                fig_status.update_traces(texttemplate='%{y}', textposition='outside')
                fig_status.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color=text_app),
                    margin=dict(t=30, b=10)
                )
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
    col_topo_l1, col_topo_l2 = st.columns([4, 1])
    with col_topo_l1:
        st.markdown("### 🎯 Gestão de Leads")
    with col_topo_l2:
        if st.button("➕ Novo Lead", use_container_width=True):
            st.session_state.modal_novo_lead = True

    total_leads_count = len(df_clientes) if not df_clientes.empty else 0
    novos_hoje_count = len(df_clientes[df_clientes["data"] == str(date.today())]) if not df_clientes.empty else 0
    primeiro_contato_count = len(df_clientes[df_clientes["status"].str.contains("Primeiro Contato", case=False, na=False)]) if not df_clientes.empty else 0
    atendimento_count = len(df_clientes[df_clientes["status"].str.contains("Atendimento|Novo Lead", case=False, na=False)]) if not df_clientes.empty else 0
    proposta_count = len(df_clientes[df_clientes["status"].str.contains("Proposta", case=False, na=False)]) if not df_clientes.empty else 0
    negociacao_count = len(df_clientes[df_clientes["status"].str.contains("Negociação", case=False, na=False)]) if not df_clientes.empty else 0
    fechados_count = len(df_clientes[df_clientes["status"].str.contains("Fechada", case=False, na=False)]) if not df_clientes.empty else 0
    perdidos_count = len(df_clientes[df_clientes["status"].str.contains("Perdida", case=False, na=False)]) if not df_clientes.empty else 0

    valor_potencial = df_clientes["valor_estimado"].sum() if not df_clientes.empty and "valor_estimado" in df_clientes.columns else 0.0
    taxa_conversao = (fechados_count / total_leads_count * 100) if total_leads_count > 0 else 0.0

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("📊 Total de Leads", total_leads_count)
    mc2.metric("✨ Novos Hoje", novos_hoje_count)
    mc3.metric("📞 1º Contato", primeiro_contato_count)
    mc4.metric("💬 Em Atendimento", atendimento_count)
    mc5.metric("📋 Propostas", proposta_count)

    mc6, mc7, mc8, mc9, mc10 = st.columns(5)
    mc6.metric("🤝 Negociação", negociacao_count)
    mc7.metric("✅ Fechados", fechados_count)
    mc8.metric("❌ Perdidos", perdidos_count)
    mc9.metric("💰 Valor Potencial", f"R$ {valor_potencial:,.2f}")
    mc10.metric("📈 Taxa de Conversão", f"{taxa_conversao:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.get("modal_novo_lead", False):
        with st.expander("📝 Cadastro Completo do Lead", expanded=True):
            with st.form("form_novo_lead_completo"):
                st.markdown("##### Dados Básicos")
                nc1, nc2, nc3 = st.columns(3)
                with nc1:
                    l_nome = st.text_input("Nome *")
                    l_cargo = st.text_input("Cargo")
                    l_cidade = st.text_input("Cidade")
                with nc2:
                    l_empresa = st.text_input("Empresa")
                    l_email = st.text_input("E-mail")
                    l_estado = st.text_input("Estado (UF)")
                with nc3:
                    l_telefone = st.text_input("Telefone")
                    l_whatsapp = st.text_input("WhatsApp")

                st.markdown("##### Dados Comerciais & Controle")
                cc1, cc2, cc3, cc4 = st.columns(4)
                with cc1:
                    l_origem = st.selectbox("Origem", ["Google Ads", "Instagram", "Site", "Indicação", "WhatsApp", "Prospecção Ativa"])
                with cc2:
                    l_status = st.selectbox("Status", ["🆕 Novo Lead", "📞 Primeiro Contato", "💬 Em Atendimento", "📋 Proposta Enviada", "⏳ Aguardando Resposta", "🤝 Negociação", "✅ Venda Fechada", "❌ Venda Perdida"])
                with cc3:
                    l_prioridade = st.selectbox("Prioridade", ["🔴 Alta", "🟡 Média", "🟢 Baixa"])
                with cc4:
                    l_responsavel = st.text_input("Responsável", value="Carlos")

                l_valor = st.number_input("Valor Estimado (R$)", value=0.0, format="%.2f")
                l_data = st.text_input("Data de Cadastro", value=str(date.today()))

                salvar_lead = st.form_submit_button("Cadastrar Lead")
                if salvar_lead:
                    if l_nome:
                        conn = conectar()
                        conn.execute("""
                            INSERT INTO clientes (nome, empresa, email, telefone, status, origem, responsavel, valor_estimado, data, prioridade)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (l_nome, l_empresa, l_email, l_telefone, l_status, l_origem, l_responsavel, l_valor, l_data, l_prioridade))
                        conn.commit()
                        conn.close()
                        st.success("Lead cadastrado com sucesso!")
                        st.session_state.modal_novo_lead = False
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o nome do lead.")

    st.markdown("### 📋 Tabela de Leads")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead cadastrado.")

elif selected == "Agenda":
    st.markdown("### 📅 Agenda de Compromissos")
    st.info("Gerencie seus compromissos, reuniões e ligações com clientes.")
    
    col_ag1, col_ag2 = st.columns(2)
    with col_ag1:
        st.date_input("Data do Compromisso", value=date.today())
        st.time_input("Horário")
        st.text_input("Título do Evento")
    with col_ag2:
        st.selectbox("Tipo", ["Reunião", "Ligação", "Demonstração", "Follow-up"])
        st.text_input("Cliente / Empresa Relacionada")
        st.text_area("Observações")
    
    if st.button("Salvar Compromisso"):
        st.success("Compromisso agendado com sucesso!")

elif selected == "Atividades":
    st.markdown("### 📋 Gestão de Atividades")
    st.info("Acompanhe as tarefas pendentes, em andamento e concluídas.")
    
    st.selectbox("Filtrar Atividades", ["Todas as atividades", "Pendentes", "Concluídas"])
    st.markdown("---")
    st.text_input("Nova Atividade / Tarefa")
    if st.button("Adicionar Tarefa"):
        st.success("Tarefa adicionada!")

elif selected == "Pipeline":
    st.markdown("### 🔄 Pipeline de Vendas")
    st.info("Visualize os negócios em andamento por estágio no funil de vendas.")
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True, hide_index=True)
    else:
        st.info("Pipeline vazio.")

elif selected == "Vendas":
    st.markdown("### 💰 Histórico de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada.")

elif selected == "Propostas":
    st.markdown("### 📄 Gestão de Propostas Comerciais")
    st.info("Crie, envie e acompanhe o status das propostas comerciais enviadas aos clientes.")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação de Dados")
    st.info("Exporte relatórios gerenciais em PDF, Excel ou CSV e configure disparos automáticos por e-mail.")
    
    with st.form("form_exportacao"):
        tipo_rel = st.selectbox("Selecione o Relatório", ["Vendas", "Clientes", "Receita", "Pipeline"])
        formato_arq = st.selectbox("Formato", ["PDF", "Excel", "CSV"])
        email_dest = st.text_input("E-mail do Destinatário", value="sergiolmendes2026@gmail.com")
        
        btn_gerar = st.form_submit_button("Gerar e Enviar Relatório")
        if btn_gerar:
            buffer_ficticio = io.BytesIO(b"Dados do relatorio comercial do CRM Pro")
            sucesso = disparar_email_automatico(email_dest, buffer_ficticio.getvalue(), f"relatorio_{tipo_rel.lower()}.{formato_arq.lower()}")
            if sucesso:
                st.success("Relatório gerado e enviado por e-mail com sucesso!")
            else:
                st.error("Erro ao enviar o e-mail. Verifique as credenciais SMTP.")

elif selected == "Metas":
    st.markdown("### 🏔️ Metas Comerciais")
    st.info("Acompanhe as metas individuais e de equipe.")

elif selected == "Campanhas":
    st.markdown("### 📣 Campanhas de Marketing e Vendas")
    st.info("Dispare campanhas por e-mail ou WhatsApp para sua base de leads.")

elif selected == "Usuários":
    st.markdown("### 👤 Gestão de Usuários")
    st.info("Cadastre e gerencie os usuários com acesso ao CRM.")

elif selected == "Permissões":
    st.markdown("### 🔒 Controle de Permissões")
    st.info("Defina o nível de acesso de cada perfil de usuário.")

elif selected == "Notificações":
    st.markdown("### 🔔 Central de Notificações")
    st.info("Visualize alertas sobre leads quentes, prazos vencidos e metas atingidas.")

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    tema_escolhido = st.selectbox("Tema do Sistema", ["🌙 Escuro", "☀️ Claro"], index=0 if is_escuro else 1)
    if tema_escolhido != st.session_state.tema_sistema:
        st.session_state.tema_sistema = tema_escolhido
        st.rerun()
