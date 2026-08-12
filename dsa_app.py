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

if "modal_nova_atividade" not in st.session_state:
    st.session_state.modal_nova_atividade = False
if "filtro_atividades" not in st.session_state:
    st.session_state.filtro_atividades = "Todas as atividades"

st.set_page_config(page_title="CRM LMB Pro", layout="wide")

# --- CSS GLOBAL E CENTRALIZADO ---
st.markdown("""
    <style>
        /* Fundo do App */
        .stApp { background-color: #0e1117; color: #ffffff; }

        /* Sidebar Container */
        [data-testid="stSidebar"] { 
            background-color: #0b0f19 !important; 
            border-right: 1px solid #1e293b;
        }

        /* Ajuste do Option Menu para garantir que não sobrescreva */
        div[data-testid="stSidebar"] .nav-link {
            background-color: transparent !important;
            border-radius: 8px !important;
            margin: 2px 0px !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-testid="stSidebar"] .nav-link:hover {
            background-color: #1e293b !important;
        }

        div[data-testid="stSidebar"] .nav-link-selected {
            background-color: #1e293b !important;
            border-left: 4px solid #3b82f6 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Inicialização de estados
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"


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
        
        /* Ajuste do Sidebar Container */
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg}; 
            border-right: 1px solid #1e293b;
            padding: 0 !important;
        }}
        
        /* Estilização dos Botões */
        [data-testid="stSidebar"] div.stButton > button {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
            width: 100%; 
            background-color: transparent !important;
            color: #94a3b8 !important; 
            border: none !important; 
            border-radius: 8px !important;
            padding: 10px 16px !important; 
            margin-bottom: 2px;
            transition: all 0.2s ease;
            font-size: 14px !important;
            font-weight: 500 !important;
        }}
        
        [data-testid="stSidebar"] div.stButton > button:hover {{ 
            background-color: #1e293b !important; 
            color: #ffffff !important;
        }}
        
        .sidebar-section-title {{
            color: #475569;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin: 20px 0 8px 16px;
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

from streamlit_option_menu import option_menu

with st.sidebar:
    # Cabeçalho da Sidebar
    st.markdown("""
        <div style="padding: 10px 0px 20px 10px;">
            <span style="font-weight: 700; font-size: 20px; color: white;">📊 CRM PRO</span>
        </div>
    """, unsafe_allow_html=True)

    # Menu lateral limpo (Sem WhatsApp e sem Integrações duplicadas)
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
                fig_linha = px.line(df_v_linha, x="data", y="valor", markers=True)
                fig_linha.update_traces(
                    line=dict(color="#38BDF8", width=3),
                    fill='tozeroy',
                    fillcolor="rgba(56, 189, 248, 0.15)"
                )
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
                
                # Mapeamento de cores personalizadas para cada status
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
    
    with st.form("form_novo_pipeline"):
        st.markdown("##### Adicionar Novo Negócio ao Pipeline")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            p_titulo = st.text_input("Título do Negócio *")
            p_estagio = st.selectbox("Estágio", ["Prospecção", "Qualificação", "Proposta", "Fechamento"])
            p_valor = st.number_input("Valor (R$)", min_value=0.0, value=10000.0, step=1000.0)
        with p_col2:
            p_empresa = st.text_input("Empresa", value="Empresa Exemplo")
            p_resp = st.text_input("Responsável", value="Carlos")
            p_contato = st.text_input("Contato", value="Nome do Contato")
        
        btn_add_pipe = st.form_submit_button("Salvar no Pipeline")
        if btn_add_pipe:
            if p_titulo:
                conn = conectar()
                conn.execute("INSERT INTO pipeline (titulo, estagio, valor, empresa, responsavel, contato) VALUES (?, ?, ?, ?, ?, ?)", 
                             (p_titulo, p_estagio, p_valor, p_empresa, p_resp, p_contato))
                conn.commit()
                conn.close()
                st.success("Negócio adicionado ao pipeline com sucesso!")
                st.rerun()
            else:
                st.error("Informe o título do negócio.")

    st.markdown("<br>", unsafe_allow_html=True)
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum negócio no pipeline.")

elif selected == "Vendas":
    st.markdown("### 🏆 Histórico de Vendas Realizadas")
    
    with st.form("form_nova_venda"):
        st.markdown("##### Registrar Nova Venda")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            v_cliente = st.text_input("Cliente / Empresa *")
            v_valor = st.number_input("Valor da Venda (R$)", min_value=0.0, value=5000.0, step=500.0)
            v_produto = st.text_input("Produto / Serviço", value="Software A")
        with v_col2:
            v_data = st.text_input("Data da Venda", value=str(date.today()))
            v_resp = st.text_input("Responsável", value="Carlos")
            v_status = st.selectbox("Status", ["Pago", "Pendente", "Cancelado"])
            
        btn_add_venda = st.form_submit_button("Registrar Venda")
        if btn_add_venda:
            if v_cliente:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel, status, produto) VALUES (?, ?, ?, ?, ?, ?)",
                             (v_cliente, v_valor, v_data, v_resp, v_status, v_produto))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Informe o nome do cliente.")

    st.markdown("<br>", unsafe_allow_html=True)
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada.")

elif selected == "Relatórios":
    st.markdown("### 📄 Relatórios e Exportações")
    st.markdown("Selecione o tipo de relatório e o formato desejado para exportação.")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        tipo_rel = st.selectbox("Tipo de Relatório", ["Vendas", "Clientes", "Pipeline"])
        formato_rel = st.selectbox("Formato", ["CSV", "Excel", "PDF"])
    with r_col2:
        dest_email = st.text_input("Enviar por E-mail (Opcional)", value="sergiolmendes2026@gmail.com")
        
    if st.button("Gerar e Exportar Relatório", use_container_width=True):
        if tipo_rel == "Vendas":
            df_export = df_vendas.copy()
        elif tipo_rel == "Clientes":
            df_export = df_clientes.copy()
        else:
            df_export = df_pipeline.copy()

        buffer = io.BytesIO()
        
        if formato_rel == "Excel":
            try:
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_export.to_excel(writer, index=False, sheet_name=tipo_rel)
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                file_extension = "xlsx"
            except Exception:
                st.warning("A biblioteca 'openpyxl' não está instalada no ambiente. Exportando em formato CSV alternativo.")
                buffer.write(df_export.to_csv(index=False).encode('utf-8'))
                mime_type = "text/csv"
                file_extension = "csv"
        elif formato_rel == "PDF":
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Relatorio de {tipo_rel} - CRM Pro", ln=1, align="c")
                pdf.ln(10)
                pdf.set_font("Arial", size=8)
                for index, row in df_export.iterrows():
                    linha_txt = " | ".join([str(val) for val in row.values])
                    pdf.cell(200, 8, txt=linha_txt, ln=1)
                pdf_output = pdf.output(dest='S').encode('latin1')
                buffer.write(pdf_output)
            except Exception:
                buffer.write(df_export.to_string().encode('utf-8'))
            mime_type = "application/pdf"
            file_extension = "pdf"
        else:
            buffer.write(df_export.to_csv(index=False).encode('utf-8'))
            mime_type = "text/csv"
            file_extension = "csv"

        nome_arq = f"relatorio_{tipo_rel.lower()}_{date.today()}.{file_extension}"
        
        st.download_button(
            label=f"📥 Baixar Arquivo Gerado ({file_extension.upper()})",
            data=buffer.getvalue(),
            file_name=nome_arq,
            mime=mime_type
        )
        
        if dest_email:
            sucesso_email = disparar_email_automatico(dest_email, buffer.getvalue(), nome_arq)
            if sucesso_email:
                st.success(f"Relatório enviado com sucesso para {dest_email}!")
            else:
                st.warning("Relatório gerado, mas houve um erro ao enviar por e-mail.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📜 Histórico de Exportações")
    conn = conectar()
    df_hist = pd.read_sql("SELECT * FROM historico_exportacoes", conn)
    conn.close()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum histórico de exportação.")

elif selected == "Atividades":
    col_atv_t1, col_atv_t2 = st.columns([4, 1])
    with col_atv_t1:
        st.markdown("### 📞 Painel de Atividades")
    with col_atv_t2:
        if st.button("➕ Nova Atividade", use_container_width=True):
            st.session_state.modal_nova_atividade = True
            st.rerun()

    cols_filtros = st.columns(7)
    opcoes_menu_atv = [
        "Todas as atividades", "Minhas atividades", "Pendentes", 
        "Concluídas", "Atrasadas", "Hoje", "Próximas atividades"
    ]
    
    for i, op in enumerate(opcoes_menu_atv):
        with cols_filtros[i]:
            if st.button(op, use_container_width=True, key=f"btn_filtro_atv_{i}"):
                st.session_state.filtro_atividades = op
                st.rerun()

    st.markdown(f"##### 📌 Exibindo: *{st.session_state.get('filtro_atividades', 'Todas as atividades')}*")

    hoje_str = str(date.today())
    df_atv_view = df_atividades.copy() if 'df_atividades' in globals() and not df_atividades.empty else pd.DataFrame()

    total_atv = len(df_atv_view)
    pendentes_atv = len(df_atv_view[df_atv_view["status"] == "Pendente"]) if not df_atv_view.empty else 0
    hoje_atv_count = len(df_atv_view[df_atv_view["data"] == hoje_str]) if not df_atv_view.empty else 0
    atrasadas_atv = len(df_atv_view[(df_atv_view["data"] < hoje_str) & (df_atv_view["status"] == "Pendente")]) if not df_atv_view.empty else 0
    concluidas_atv = len(df_atv_view[df_atv_view["status"] == "Concluída"]) if not df_atv_view.empty else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total de Atividades", total_atv)
    kpi2.metric("Pendentes", pendentes_atv)
    kpi3.metric("Hoje", hoje_atv_count)
    kpi4.metric("Atrasadas", atrasadas_atv)
    kpi5.metric("Concluídas", concluidas_atv)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.get("modal_nova_atividade", False):
        with st.expander("📝 Cadastrar Nova Atividade", expanded=True):
            with st.form("form_nova_atividade"):
                fa1, fa2, fa3 = st.columns(3)
                with fa1:
                    atv_tipo = st.selectbox("Tipo", ["Ligação", "Reunião", "WhatsApp", "E-mail", "Compromisso", "Tarefa", "Proposta", "Follow-up"])
                    atv_cliente = st.text_input("Cliente / Lead *", placeholder="Nome do cliente")
                with fa2:
                    atv_respons = st.text_input("Responsável", value="Carlos")
                    atv_data = st.date_input("Data", value=date.today())
                with fa3:
                    atv_hora = st.text_input("Hora", value="09:00")
                    atv_prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])

                fa4, fa5 = st.columns(2)
                with fa4:
                    atv_status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluída"])
                with fa5:
                    atv_lembrete = st.selectbox("Lembrete", ["Sim", "Não"])

                atv_desc = st.text_area("Descrição / Observação")

                btn_salvar_atv, btn_fechar_atv = st.columns(2)
                with btn_salvar_atv:
                    submit_atv = st.form_submit_button("Salvar Atividade", use_container_width=True)
                with btn_fechar_atv:
                    close_atv = st.form_submit_button("Cancelar", use_container_width=True)

                if submit_atv:
                    if atv_cliente:
                        conn = conectar()
                        conn.execute("""
                            INSERT INTO atividades (tipo, cliente, responsavel, data, hora, prioridade, status, descricao, lembrete)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (atv_tipo, atv_cliente, atv_respons, str(atv_data), atv_hora, atv_prioridade, atv_status, atv_desc, atv_lembrete))
                        conn.commit()
                        conn.close()
                        st.session_state.modal_nova_atividade = False
                        st.success("Atividade cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Informe o nome do cliente ou lead.")

                if close_atv:
                    st.session_state.modal_nova_atividade = False
                    st.rerun()

    filtro_atual = st.session_state.get("filtro_atividades", "Todas as atividades")
    if not df_atv_view.empty:
        if filtro_atual == "Minhas atividades":
            df_atv_view = df_atv_view[df_atv_view["responsavel"] == "Carlos"]
        elif filtro_atual == "Pendentes":
            df_atv_view = df_atv_view[df_atv_view["status"] == "Pendente"]
        elif filtro_atual == "Concluídas":
            df_atv_view = df_atv_view[df_atv_view["status"] == "Concluída"]
        elif filtro_atual == "Atrasadas":
            df_atv_view = df_atv_view[(df_atv_view["data"] < hoje_str) & (df_atv_view["status"] == "Pendente")]
        elif filtro_atual == "Hoje":
            df_atv_view = df_atv_view[df_atv_view["data"] == hoje_str]
        elif filtro_atual == "Próximas atividades":
            df_atv_view = df_atv_view[df_atv_view["data"] > hoje_str]

    st.markdown("#### Agenda de Atividades")
    if not df_atv_view.empty:
        colunas_exibir = [c for c in ['data', 'hora', 'cliente', 'tipo', 'responsavel', 'prioridade', 'status', 'descricao'] if c in df_atv_view.columns]
        st.dataframe(df_atv_view[colunas_exibir], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma atividade encontrada para este filtro.")

# <--- FIM DO BLOCO PARA COLAR --->


    st.markdown("### ⚙️ Configurações do Sistema")
    
    # --- Colunas Principais ---
    c_conf1, c_conf2 = st.columns(2)
    
    with c_conf1:
        st.markdown("#### 🎨 Aparência")
        novo_tema = st.selectbox("Tema do Sistema", ["🌙 Escuro", "☀️ Claro"], 
                                 index=0 if "Escuro" in st.session_state.get("tema_sistema", "Escuro") else 1)
        if novo_tema != st.session_state.get("tema_sistema", "Escuro"):
            st.session_state.tema_sistema = novo_tema
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🌐 Preferências Regionais")
        st.selectbox("Moeda Padrão", ["Real (R$)", "Dólar ($)", "Euro (€)"])
        st.selectbox("Formato de Data", ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"])

    with c_conf2:
        st.markdown("#### 🏢 Informações da Empresa")
        st.text_input("Nome da Organização", value="LMB Pro Solutions")
        st.text_input("CNPJ / ID", value="00.000.000/0001-00")
        
        st.markdown("---")
        st.markdown("#### 🔌 Chaves de Integração (API)")
        st.text_input("Token API WhatsApp", type="password", placeholder="Cole seu token aqui")
        st.text_input("Chave Google Sheets API", type="password", placeholder="Cole sua chave aqui")

    # Botão de salvar no rodapé
    st.markdown("---")
    if st.button("💾 Salvar Alterações Gerais", use_container_width=True):
        st.success("Configurações do sistema atualizadas com sucesso!") 
