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

st.set_page_config(
    page_title="CRM Pro - Workspace v2.0", page_icon="📊", layout="wide" 
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
        
        [data-testid="stSidebar"] button div p {{
            font-size: 15px !important;
            font-weight: 600 !important;
        }}

        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; 
            text-align: left; 
            background-color: transparent !important;
            color: #f1f5f9 !important; 
            border: none !important; 
            border-radius: 8px !important;
            padding: 6px 10px !important; 
            margin-bottom: 2px;
            transition: all 0.2s ease-in-out;
        }}
        
        [data-testid="stSidebar"] div.stButton > button:hover {{ 
            background-color: rgba(37, 99, 235, 0.15) !important; 
            color: #ffffff !important;
            transform: translateX(4px);
        }}
        
        .sidebar-section-title {{
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 14px;
            margin-bottom: 4px;
            padding-left: 10px;
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
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    
    # Novas tabelas solicitadas
    cursor.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, horario TEXT, cliente TEXT, responsavel TEXT, tipo TEXT, local TEXT, status TEXT, observacoes TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS atividades (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, atividade TEXT, responsavel TEXT, data TEXT, hora TEXT, prioridade TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS propostas (id INTEGER PRIMARY KEY AUTOINCREMENT, numero TEXT, cliente TEXT, produto TEXT, valor REAL, data TEXT, validade TEXT, responsavel TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor TEXT, meta_mensal REAL, valor_vendido REAL, comissao REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS campanhas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, canal TEXT, inicio TEXT, fim TEXT, investimento REAL, leads_gerados INTEGER, conversoes INTEGER, roi REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS whatsapp (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, ultima_mensagem TEXT, status TEXT, responsavel TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cargo TEXT, email TEXT, perfil TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS permissoes (id INTEGER PRIMARY KEY AUTOINCREMENT, modulo TEXT, admin TEXT, gerente TEXT, vendedor TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS notificacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, mensagem TEXT, data TEXT, lida INTEGER)")

    # Dados iniciais padrão se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO usuarios (nome, cargo, email, perfil, status) VALUES (?, ?, ?, ?, ?)", [
            ("João Silva", "Administrador", "joao@crm.com", "Admin", "Ativo"),
            ("Ana Souza", "Gerente Comercial", "ana@crm.com", "Gerente", "Ativo"),
            ("Carlos Lima", "Vendedor", "carlos@crm.com", "Vendedor", "Ativo"),
        ])

    cursor.execute("SELECT COUNT(*) FROM agenda")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO agenda (data, horario, cliente, responsavel, tipo, local, status, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
            (str(date.today()), "10:00", "Empresa Alpha", "Carlos", "Reunião", "Online", "Agendado", "Apresentar nova proposta v2"),
            (str(date.today()), "14:30", "Empresa Beta", "Ana", "Demonstração", "Escritório", "Confirmado", "Demonstrar o sistema"),
        ])

    cursor.execute("SELECT COUNT(*) FROM propostas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO propostas (numero, cliente, produto, valor, data, validade, responsavel, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
            ("PROP-001", "Empresa Alpha", "Software A", 15000.0, "2026-06-01", "2026-06-30", "Carlos", "Em negociação"),
            ("PROP-002", "Empresa Beta", "Software B", 25000.0, "2026-06-05", "2026-07-05", "Ana", "Aprovada"),
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

    # PRINCIPAL
    st.markdown('<p class="sidebar-section-title">Principal</p>', unsafe_allow_html=True)
    menu_button("Dashboard", "🏠", "nav_dashboard")
    menu_button("Clientes", "👥", "nav_clientes")
    menu_button("Leads", "🎯", "nav_leads")
    menu_button("Agenda", "📅", "nav_agenda")
    menu_button("Atividades", "📞", "nav_atividades")

    # COMERCIAL
    st.markdown('<p class="sidebar-section-title">Comercial</p>', unsafe_allow_html=True)
    menu_button("Pipeline", "📈", "nav_pipeline")
    menu_button("Vendas", "💰", "nav_vendas")
    menu_button("Propostas", "📄", "nav_propostas")
    menu_button("Relatórios", "📊", "nav_relatorios")
    menu_button("Metas", "🎯", "nav_metas")

    # MARKETING
    st.markdown('<p class="sidebar-section-title">Marketing</p>', unsafe_allow_html=True)
    menu_button("Campanhas", "📧", "nav_campanhas")
    menu_button("WhatsApp", "💬", "nav_whatsapp")

    # SISTEMA
    st.markdown('<p class="sidebar-section-title">Sistema</p>', unsafe_allow_html=True)
    menu_button("Integrações", "🔌", "nav_integracoes")
    menu_button("Usuários", "👤", "nav_usuarios")
    menu_button("Permissões", "🔒", "nav_permissoes")
    menu_button("Notificações", "🔔", "nav_notificacoes")
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
        msg.attach(MIMEText("Olá! Segue o relatório comercial.", 'plain'))
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
    except Exception:
        return False

@st.cache_data(ttl=1)
def carregar_dados_gerais():
    conn = conectar()
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados_gerais()

# --- TOPO COM BUSCA GLOBAL ---
col_busca1, col_busca2, col_busca3 = st.columns([6, 1, 1])
with col_busca1:
    termo_busca = st.text_input("Pesquisa Global", placeholder="🔍 Pesquisar clientes, leads, vendas...", label_visibility="collapsed")
with col_busca2:
    st.markdown("🔔", help="Notificações")
with col_busca3:
    st.markdown("👤", help="Perfil do Usuário")

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-color: #334155;'>", unsafe_allow_html=True)

# --- RENDERIZAÇÃO DAS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty else 0.0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and len(df_vendas) > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Leads", f"{total_leads}")
    c2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    c3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    c4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    st.info("Painel principal carregado com sucesso.")

elif selected == "Clientes":
    st.markdown("### 👥 Gestão de Clientes")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead cadastrado.")

elif selected == "Agenda":
    st.markdown("### 📅 Agenda de Compromissos Comerciais")
    
    with st.expander("➕ Novo Compromisso", expanded=False):
        with st.form("form_agenda"):
            ac1, ac2 = st.columns(2)
            with ac1:
                ag_data = st.text_input("Data", value=str(date.today()))
                ag_hora = st.text_input("Horário", value="09:00")
                ag_cliente = st.text_input("Cliente")
                ag_resp = st.text_input("Responsável", value="Carlos")
            with ac2:
                ag_tipo = st.selectbox("Tipo de compromisso", ["Reunião", "Ligação", "Demonstração", "Visita", "Videoconferência"])
                ag_local = st.text_input("Local", value="Online")
                ag_status = st.selectbox("Status", ["Agendado", "Confirmado", "Concluído", "Cancelado"])
                ag_obs = st.text_input("Observações")
            if st.form_submit_button("Salvar Compromisso"):
                conn = conectar()
                conn.execute("INSERT INTO agenda (data, horario, cliente, responsavel, tipo, local, status, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (ag_data, ag_hora, ag_cliente, ag_resp, ag_tipo, ag_local, ag_status, ag_obs))
                conn.commit()
                conn.close()
                st.success("Compromisso salvo!")
                st.rerun()

    conn = conectar()
    df_agenda = pd.read_sql("SELECT * FROM agenda", conn)
    conn.close()
    if not df_agenda.empty:
        st.dataframe(df_agenda, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum compromisso agendado.")

elif selected == "Atividades":
    st.markdown("### 📞 Histórico de Atividades")
    
    with st.expander("➕ Nova Atividade", expanded=False):
        with st.form("form_atividades"):
            at1, at2 = st.columns(2)
            with at1:
                at_cli = st.text_input("Cliente")
                at_ativ = st.selectbox("Atividade", ["Ligação", "E-mail", "WhatsApp", "Reunião", "Tarefa", "Follow-up"])
                at_resp = st.text_input("Responsável", value="Carlos")
            with at2:
                at_data = st.text_input("Data", value=str(date.today()))
                at_hora = st.text_input("Hora", value="11:00")
                at_prio = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
                at_status = st.selectbox("Status", ["Pendente", "Concluída", "Atrasada"])
            if st.form_submit_button("Registrar Atividade"):
                conn = conectar()
                conn.execute("INSERT INTO atividades (cliente, atividade, responsavel, data, hora, prioridade, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (at_cli, at_ativ, at_resp, at_data, at_hora, at_prio, at_status))
                conn.commit()
                conn.close()
                st.success("Atividade registrada!")
                st.rerun()

    conn = conectar()
    df_ativ = pd.read_sql("SELECT * FROM atividades", conn)
    conn.close()
    
    # Dashboard rápido de atividades
    c_at1, c_at2, c_at3, c_at4 = st.columns(4)
    c_at1.metric("Atividades do Dia", len(df_ativ))
    c_at2.metric("Pendentes", len(df_ativ[df_ativ['status'] == 'Pendente']) if not df_ativ.empty else 0)
    c_at3.metric("Concluídas", len(df_ativ[df_ativ['status'] == 'Concluída']) if not df_ativ.empty else 0)
    c_at4.metric("Atrasadas", len(df_ativ[df_ativ['status'] == 'Atrasada']) if not df_ativ.empty else 0)

    st.markdown("<br>", unsafe_allow_html=True)
    if not df_ativ.empty:
        st.dataframe(df_ativ, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma atividade registrada.")

elif selected == "Pipeline":
    st.markdown("### 📈 Pipeline Comercial")
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True, hide_index=True)
    else:
        st.info("Pipeline vazio.")

elif selected == "Vendas":
    st.markdown("### 💰 Vendas Realizadas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda.")

elif selected == "Propostas":
    st.markdown("### 📄 Controle de Propostas Comerciais")
    
    with st.expander("➕ Nova Proposta", expanded=False):
        with st.form("form_propostas"):
            pr1, pr2 = st.columns(2)
            with pr1:
                p_num = st.text_input("Número da Proposta", value="PROP-003")
                p_cli = st.text_input("Cliente")
                p_prod = st.text_input("Produto")
                p_val = st.number_input("Valor (R$)", value=10000.0)
            with pr2:
                p_dt = st.text_input("Data", value=str(date.today()))
                p_val_d = st.text_input("Validade", value="2026-12-31")
                p_resp = st.text_input("Responsável", value="Carlos")
                p_status = st.selectbox("Status", ["Em elaboração", "Enviada", "Em negociação", "Aprovada", "Recusada", "Cancelada"])
            if st.form_submit_button("Salvar Proposta"):
                conn = conectar()
                conn.execute("INSERT INTO propostas (numero, cliente, produto, valor, data, validade, responsavel, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (p_num, p_cli, p_prod, p_val, p_dt, p_val_d, p_resp, p_status))
                conn.commit()
                conn.close()
                st.success("Proposta salva!")
                st.rerun()

    conn = conectar()
    df_prop = pd.read_sql("SELECT * FROM propostas", conn)
    conn.close()

    total_p = len(df_prop)
    valor_total_p = df_prop['valor'].sum() if not df_prop.empty else 0.0
    aprovadas = len(df_prop[df_prop['status'] == 'Aprovada']) if not df_prop.empty else 0
    taxa_aprov = (aprovadas / total_p * 100) if total_p > 0 else 0.0

    cp1, cp2, cp3, cp4 = st.columns(4)
    cp1.metric("Total de Propostas", total_p)
    cp2.metric("Valor Total", f"R$ {valor_total_p:,.2f}")
    cp3.metric("Taxa de Aprovação", f"{taxa_aprov:.1f}%")
    cp4.metric("Propostas Vencidas", 0)

    st.markdown("<br>", unsafe_allow_html=True)
    if not df_prop.empty:
        st.dataframe(df_prop, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma proposta cadastrada.")

elif selected == "Relatórios":
    st.markdown("### 📊 Relatórios e Exportações")
    st.info("Utilize a ferramenta de exportação em Excel, CSV ou PDF.")

elif selected == "Metas":
    st.markdown("### 🎯 Controle de Metas da Equipe")
    
    conn = conectar()
    df_metas = pd.read_sql("SELECT * FROM metas", conn)
    conn.close()
    
    if df_metas.empty:
        conn = conectar()
        conn.executemany("INSERT INTO metas (vendedor, meta_mensal, valor_vendido, comissao) VALUES (?, ?, ?, ?)", [
            ("Carlos", 50000.0, 42000.0, 2100.0),
            ("Ana", 60000.0, 65000.0, 3250.0)
        ])
        conn.commit()
        conn.close()
        conn = conectar()
        df_metas = pd.read_sql("SELECT * FROM metas", conn)
        conn.close()

    df_metas['Percentual'] = (df_metas['valor_vendido'] / df_metas['meta_mensal']) * 100
    st.dataframe(df_metas, use_container_width=True, hide_index=True)

    fig = px.bar(df_metas, x='vendedor', y=['meta_mensal', 'valor_vendido'], barmode='group', title="Meta vs Realizado por Vendedor")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Campanhas":
    st.markdown("### 📢 Campanhas de Marketing")
    conn = conectar()
    df_camp = pd.read_sql("SELECT * FROM campanhas", conn)
    conn.close()
    if df_camp.empty:
        conn = conectar()
        conn.execute("INSERT INTO campanhas (nome, canal, inicio, fim, investimento, leads_gerados, conversoes, roi) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     ("Campanha Google Q2", "Google Ads", "2026-04-01", "2026-06-30", 5000.0, 120, 15, 3.2))
        conn.commit()
        conn.close()
        conn = conectar()
        df_camp = pd.read_sql("SELECT * FROM campanhas", conn)
        conn.close()
    st.dataframe(df_camp, use_container_width=True, hide_index=True)

elif selected == "WhatsApp":
    st.markdown("### 💬 Controle de Conversas (WhatsApp)")
    conn = conectar()
    df_wpp = pd.read_sql("SELECT * FROM whatsapp", conn)
    conn.close()
    if df_wpp.empty:
        conn = conectar()
        conn.execute("INSERT INTO whatsapp (cliente, ultima_mensagem, status, responsavel) VALUES (?, ?, ?, ?)",
                     ("João Silva", "Olá, gostaria de saber mais sobre o software.", "Pendente", "Carlos"))
        conn.commit()
        conn.close()
        conn = conectar()
        df_wpp = pd.read_sql("SELECT * FROM whatsapp", conn)
        conn.close()
    st.dataframe(df_wpp, use_container_width=True, hide_index=True)

elif selected == "Usuários":
    st.markdown("### 👤 Cadastro de Usuários do Sistema")
    conn = conectar()
    df_user = pd.read_sql("SELECT * FROM usuarios", conn)
    conn.close()
    st.dataframe(df_user, use_container_width=True, hide_index=True)

elif selected == "Permissões":
    st.markdown("### 🔒 Controle de Acesso e Permissões")
    dados_perm = [
        {"Módulo": "Dashboard", "Admin": "✅", "Gerente": "✅", "Vendedor": "✅"},
        {"Módulo": "Clientes", "Admin": "✅", "Gerente": "✅", "Vendedor": "✅"},
        {"Módulo": "Leads", "Admin": "✅", "Gerente": "✅", "Vendedor": "✅"},
        {"Módulo": "Pipeline", "Admin": "✅", "Gerente": "✅", "Vendedor": "✅"},
        {"Módulo": "Relatórios", "Admin": "✅", "Gerente": "✅", "Vendedor": "❌"},
        {"Módulo": "Configurações", "Admin": "✅", "Gerente": "❌", "Vendedor": "❌"},
        {"Módulo": "Usuários", "Admin": "✅", "Gerente": "❌", "Vendedor": "❌"},
        {"Módulo": "Integrações", "Admin": "✅", "Gerente": "❌", "Vendedor": "❌"},
    ]
    st.dataframe(pd.DataFrame(dados_perm), use_container_width=True, hide_index=True)

elif selected == "Notificações":
    st.markdown("### 🔔 Central de Notificações")
    notif = [
        {"Tipo": "Leads", "Mensagem": "Novo lead cadastrado: João Silva", "Data": "11/08/2026 14:00"},
        {"Tipo": "Vendas", "Mensagem": "Proposta aprovada pela Empresa Beta", "Data": "11/08/2026 12:30"},
        {"Tipo": "Sistema", "Mensagem": "Meta mensal atingida pela equipe comercial", "Data": "10/08/2026 18:00"},
        {"Tipo": "Leads", "Mensagem": "Cliente sem contato há 30 dias: Maria Oliveira", "Data": "09/08/2026 09:15"},
    ]
    st.dataframe(pd.DataFrame(notif), use_container_width=True, hide_index=True)

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e APIs")
    st.text_input("Chave API do Webhook", value="wk_live_99882211")

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações Gerais")
    novo_tema = st.selectbox("Tema do Sistema", ["🌙 Escuro", "☀️ Claro"], index=0 if "Escuro" in st.session_state.tema_sistema else 1)
    if novo_tema != st.session_state.tema_sistema:
        st.session_state.tema_sistema = novo_tema
        st.rerun()
