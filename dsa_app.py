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
    page_title="CRM LMB Pro - Workspace v2.0", page_icon="📊", layout="wide" 
)

# --- FUNÇÃO DE CONEXÃO ---
def conectar():
    return sqlite3.connect("crm.db")

# --- BANCO DE DADOS E TABELA DE AUTOMAÇÕES ---
def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, empresa TEXT, email TEXT, telefone TEXT, regiao TEXT, status TEXT, origem TEXT, motivo_perda TEXT, data TEXT, data_fechamento TEXT, responsavel TEXT, prioridade TEXT, ultimo_contato TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agendamentos (id INTEGER PRIMARY KEY, ativo INTEGER, frequencia TEXT, destinatario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE,
            ativo INTEGER
        )
    """)
    
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
        ])
    
    cursor.execute("SELECT COUNT(*) FROM pipeline")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO pipeline (titulo, estagio, valor, responsavel) VALUES (?, ?, ?, ?)", [
            ("Projeto X", "Prospecção", 50000.0, "Carlos"),
            ("Projeto Y", "Qualificação", 30000.0, "Ana"),
        ])

    conn.commit()
    conn.close()

inicializar_banco()

# --- FUNÇÃO DE EXECUÇÃO DE AUTOMAÇÕES ---
def executar_automacao_evento(tipo_evento, dados_contexto=""):
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
        st.toast(f"⚡ Automação disparada: {tipo_evento} - {dados_contexto}", icon="🚀")

# --- INICIALIZAÇÃO DO ESTADO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro"
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"

cor_hex = "#2563EB"
is_escuro = "Escuro" in st.session_state.tema_sistema

bg_app = "#0e1117" if is_escuro else "#ffffff"
text_app = "#ffffff" if is_escuro else "#1e293b"
sidebar_bg = "#0b0f19" if is_escuro else "#f8fafc"

# --- CSS ---
st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_app}; color: {text_app}; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid #1e293b; padding-top: 10px; }}
        h1, h2, h3, h4 {{ color: {text_app}; }}
        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; text-align: left; background-color: transparent !important;
            color: #94a3b8 !important; border: none !important; border-radius: 8px !important;
            padding: 8px 12px !important; font-size: 14px !important; font-weight: 500 !important;
            margin-bottom: 2px; transition: all 0.2s ease-in-out;
        }}
        [data-testid="stSidebar"] div.stButton > button:hover {{ background-color: rgba(255, 255, 255, 0.05) !important; color: #ffffff !important; }}
        .sidebar-section-title {{ color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; margin-top: 18px; margin-bottom: 6px; padding-left: 12px; }}
    </style>
""", unsafe_allow_html=True)

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

def disparar_email_automatico(destinatario, arquivo_bytes, nome_arquivo):
    try:
        servidor_smtp = "smtp.gmail.com"
        porta = 587
        remetente = "sergiolmendes2026@gmail.com"
        senha = "fjdqmlqokejswhtn"

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = "📊 Relatório Automático - CRM Pro"
        msg.attach(MIMEText("Olá! Segue em anexo o relatório.", 'plain'))

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

# --- NAVEGAÇÃO DE PÁGINAS ---
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Leads", f"{total_leads}")
    c2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    c3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    
    st.divider()
    
    # Gráficos restaurados
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### 📈 Vendas por Responsável")
        if not df_vendas.empty and "responsavel" in df_vendas.columns:
            fig_resp = px.bar(df_vendas, x="responsavel", y="valor", color="responsavel", text_auto=True)
            st.plotly_chart(fig_resp, use_container_width=True)
        else:
            st.info("Sem dados de vendas suficientes para o gráfico.")
            
    with col_g2:
        st.markdown("#### 🥧 Pipeline por Estágio")
        if not df_pipeline.empty and "estagio" in df_pipeline.columns:
            fig_pipe = px.pie(df_pipeline, names="estagio", values="valor", hole=0.4)
            st.plotly_chart(fig_pipe, use_container_width=True)
        else:
            st.info("Sem dados no pipeline suficientes para o gráfico.")

elif selected == "Clientes":
    st.markdown("### 📖 Base de Clientes")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    with st.form("form_novo_lead_completo"):
        l_nome = st.text_input("Nome do Lead *")
        l_email = st.text_input("E-mail")
        salvar_lead = st.form_submit_button("Salvar Lead")
        
        if salvar_lead:
            if l_nome:
                conn = conectar()
                conn.execute("INSERT INTO clientes (nome, email, status, origem, data) VALUES (?, ?, ?, ?, ?)", 
                             (l_nome, l_email, "🆕 Novo Lead", "Site", str(date.today())))
                conn.commit()
                conn.close()
                executar_automacao_evento("novo_lead", l_email)
                st.success("Lead cadastrado com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha o nome do lead.")
                
    st.divider()
    st.markdown("#### Leads Cadastrados")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)

elif selected == "Pipeline":
    st.markdown("### 📈 Pipeline de Vendas")
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
    else:
        st.info("Pipeline vazio.")

elif selected == "Vendas":
    st.markdown("### 🏆 Registro de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada.")

elif selected == "Relatórios":
    st.markdown("### 📄 Relatórios Comerciais")
    st.write("Gere e exporte relatórios consolidados em Excel ou CSV.")
    if not df_vendas.empty:
        buffer = io.BytesIO()
        df_vendas.to_excel(buffer, index=False)
        st.download_button("📥 Baixar Relatório de Vendas (Excel)", data=buffer.getvalue(), file_name="relatorio_vendas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Webhooks")
    st.write("Conecte seu CRM a ferramentas externas via API.")
    st.text_input("Chave de API (Token)", value="crm_live_99823749812739", type="password")

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações do Sistema")
    tab_ap, tab_int, tab_aut, tab_log = st.tabs(["🎨 Aparência", "🔌 Integrações & API", "⚡ Automações", "📋 Logs & Histórico"])
    
    with tab_ap:
        st.markdown("#### 🎨 Aparência do Sistema")
        tema = st.selectbox("Escolha o Tema", ["🌙 Escuro", "☀️ Claro"], index=0 if is_escuro else 1)
        if st.button("Salvar Tema"):
            st.session_state.tema_sistema = tema
            st.success("Tema atualizado com sucesso!")
            st.rerun()

    with tab_aut:
        st.markdown("#### ⚡ Seção de Automações")
        st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Regras de disparo automático acionadas por eventos do CRM.</p>", unsafe_allow_html=True)
        
        regras_automacao = {
            "email_boas_vindas": "📧 Disparar e-mail de boas-vindas para novos clientes",
            "tarefa_pipeline": "📋 Criar tarefa após mudança de estágio no Pipeline",
            "alerta_estagnado": "🔔 Enviar alerta de lead estagnado por mais de 5 dias"
        }
        
        conn = conectar()
        for chave, texto in regras_automacao.items():
            cursor = conn.cursor()
            cursor.execute("SELECT ativo FROM automacoes WHERE chave = ?", (chave,))
            res = cursor.fetchone()
            
            padrao = 1 if chave == "email_boas_vindas" else 0
            if res is None:
                cursor.execute("INSERT INTO automacoes (chave, ativo) VALUES (?, ?)", (chave, padrao))
                conn.commit()
                estado_atual = bool(padrao)
            else:
                estado_atual = bool(res[0])
                
            novo_estado = st.checkbox(texto, value=estado_atual, key=f"auto_{chave}")
            if novo_estado != estado_atual:
                conn.execute("UPDATE automacoes SET ativo = ? WHERE chave = ?", (int(novo_estado), chave))
                conn.commit()
        conn.close()
    
    with tab_log:
        st.markdown("#### 📋 Histórico de Logs")
        st.info("As automações executadas em tempo real aparecem em notificações na tela.")
