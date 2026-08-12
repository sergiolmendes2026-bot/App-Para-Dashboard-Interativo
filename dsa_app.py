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

# --- INICIALIZAÇÃO DO ESTADO ---
if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Escuro" 
if "selected" not in st.session_state:
    st.session_state.selected = "Dashboard"
if "filtro_atividades" not in st.session_state:
    st.session_state.filtro_atividades = "Todas as atividades"
if "modal_nova_atividade" not in st.session_state:
    st.session_state.modal_nova_atividade = False

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
            font-size: 16px !important;
            font-weight: 600 !important;
            text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.7) !important;
        }}

        [data-testid="stSidebar"] div.stButton > button {{
            width: 100%; 
            text-align: left; 
            background-color: transparent !important;
            color: #f1f5f9 !important; 
            border: none !important; 
            border-radius: 10px !important;
            padding: 8px 12px !important; 
            margin-bottom: 2px;
            transition: all 0.25s ease-in-out;
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
            margin-top: 16px;
            margin-bottom: 4px;
            padding-left: 12px;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);
        }}
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS E CORREÇÃO DE ESQUEMA ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    cursor.execute("""
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
            responsavel TEXT, 
            prioridade TEXT, 
            ultimo_contato TEXT,
            cnpj_cpf TEXT,
            cargo TEXT,
            valor_estimado REAL,
            segmento TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL, empresa TEXT, contato TEXT, telefone TEXT, email TEXT, responsavel TEXT, origem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT, responsavel TEXT, status TEXT, produto TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agendamentos (id INTEGER PRIMARY KEY, ativo INTEGER, frequencia TEXT, destinatario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico_exportacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, relatorio TEXT, formato TEXT, usuario TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS automacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, chave TEXT, ativo INTEGER)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            cliente TEXT,
            responsavel TEXT,
            data TEXT,
            hora TEXT,
            prioridade TEXT,
            status TEXT,
            descricao TEXT,
            lembrete TEXT
        )
    """)
    
    tinfo_clientes = [col[1] for col in cursor.execute("PRAGMA table_info(clientes)").fetchall()]
    novas_colunas = {
        "prioridade": "TEXT DEFAULT 'Média'",
        "ultimo_contato": "TEXT DEFAULT '2026-08-08'",
        "responsavel": "TEXT DEFAULT 'Carlos'",
        "empresa": "TEXT DEFAULT 'Empresa Exemplo'",
        "email": "TEXT DEFAULT 'contato@empresa.com'",
        "telefone": "TEXT DEFAULT '(11) 99999-9999'",
        "cnpj_cpf": "TEXT DEFAULT ''",
        "cargo": "TEXT DEFAULT ''",
        "valor_estimado": "REAL DEFAULT 0.0",
        "segmento": "TEXT DEFAULT 'Geral'"
    }
    for col, def_col in novas_colunas.items():
        if col not in tinfo_clientes:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} {def_col}")

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
        cursor.executemany("""
            INSERT INTO clientes (nome, empresa, email, telefone, status, origem, motivo_perda, data, responsavel, prioridade, ultimo_contato, cnpj_cpf, cargo, valor_estimado, segmento) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("João Silva", "Tech Solutions", "joao@tech.com", "(11) 98888-1111", "🆕 Novo Lead", "Google Ads", "", "2026-06-01", "Carlos", "🔴 Alta", "2026-08-09", "12.345.678/0001-99", "Diretor de TI", 15000.0, "Tecnologia"),
            ("Maria Silva", "Inova Corp", "maria@inova.com", "(11) 97777-2222", "✅ Venda Fechada", "Instagram", "", "2026-06-02", "Ana", "🟡 Média", "2026-08-08", "98.765.432/0001-11", "Gerente Comercial", 25000.0, "Varejo"),
            ("Maria Oliveira", "Global Ltda", "maria.o@global.com", "(21) 96666-3333", "❌ Venda Perdida", "Indicação", "Preço Alto", "2026-06-03", "Carlos", "🟢 Baixa", "2026-08-01", "11.222.333/0001-44", "Compradora", 10000.0, "Indústria"),
            ("Ana Paula", "Alpha Tech", "ana@alphatech.com", "(31) 95555-4444", "💬 Em Atendimento", "WhatsApp", "", "2026-06-04", "Ana", "🔴 Alta", "2026-08-10", "44.555.666/0001-55", "CEO", 30000.0, "Tecnologia"),
        ])

    cursor.execute("SELECT COUNT(*) FROM atividades")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO atividades (tipo, cliente, responsavel, data, hora, prioridade, status, descricao, lembrete) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("Ligação", "João Silva", "Carlos", str(date.today()), "10:00", "Alta", "Pendente", "Ligar para confirmar proposta", "Sim"),
            ("Reunião", "Maria Silva", "Ana", str(date.today()), "14:30", "Média", "Concluída", "Apresentação de software", "Não"),
            ("WhatsApp", "Ana Paula", "Carlos", "2026-08-01", "09:00", "Baixa", "Pendente", "Enviar tabela de preços", "Sim"),
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

@st.cache_data(ttl=1)
def carregar_dados():
    conn = conectar()
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame()
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame()
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame()
    df_atividades = pd.read_sql("SELECT * FROM atividades", conn) if "atividades" in tabelas else pd.DataFrame()
    conn.close()
    return df_clientes, df_pipeline, df_vendas, df_atividades

df_clientes, df_pipeline, df_vendas, df_atividades = carregar_dados()

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
    st.info("Utilize o menu lateral para navegar entre todas as seções do sistema.")

elif selected == "Clientes":
    st.markdown("### 📖 Cadastro Completo de Clientes e Leads")
    
    with st.form("form_cadastro_cliente"):
        c_f1, c_f2 = st.columns(2)
        
        with c_f1:
            novo_nome = st.text_input("Nome do Contato *")
            nova_empresa = st.text_input("Nome da Empresa")
            novo_cnpj = st.text_input("CNPJ / CPF")
            novo_email = st.text_input("E-mail")
            novo_telefone = st.text_input("Telefone / WhatsApp")
            novo_cargo = st.text_input("Cargo / Função")
            nova_regiao = st.selectbox("Região", ["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte"])
            
        with c_f2:
            nova_origem = st.selectbox("Origem do Lead", ["Indicação", "Google Ads", "Instagram", "WhatsApp", "LinkedIn", "Outros"])
            novo_status = st.selectbox("Status do Cliente", ["🆕 Novo Lead", "💬 Em Atendimento", "✅ Venda Fechada", "❌ Venda Perdida"])
            motivo_perda = st.text_input("Motivo de Perda (Se aplicável)")
            novo_resp = st.text_input("Responsável Comercial", value="Carlos")
            novo_segmento = st.selectbox("Segmento / Nicho", ["Geral", "Tecnologia", "Varejo", "Indústria", "Serviços", "Saúde"])
            valor_est = st.number_input("Valor Estimado Potencial (R$)", min_value=0.0, value=0.0, step=1000.0)
            
            c_data1, c_data2 = st.columns(2)
            with c_data1:
                data_cad = st.date_input("Data de Cadastro", value=date.today())
            with c_data2:
                data_fech = st.date_input("Data de Fechamento", value=None)

        btn_salvar_cli = st.form_submit_button("Salvar Cliente no CRM", use_container_width=True)
        
        if btn_salvar_cli:
            if novo_nome:
                conn = conectar()
                conn.execute("""
                    INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, origem, motivo_perda, data, data_fechamento, responsavel, prioridade, ultimo_contato, cnpj_cpf, cargo, valor_estimado, segmento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Média', ?, ?, ?, ?, ?)
                """, (
                    novo_nome, nova_empresa, novo_email, novo_telefone, nova_regiao, 
                    novo_status, nova_origem, motivo_perda, str(data_cad), 
                    str(data_fech) if data_fech else "", novo_resp, str(date.today()),
                    novo_cnpj, novo_cargo, valor_est, novo_segmento
                ))
                conn.commit()
                conn.close()
                st.success("Cliente cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha o campo 'Nome do Contato'.")

    st.markdown("---")
    st.markdown("### 📋 Base de Dados Geral (CRM)")
    if not df_clientes.empty:
        colunas_mostrar = [c for c in ['nome', 'empresa', 'cnpj_cpf', 'cargo', 'segmento', 'telefone', 'origem', 'status', 'responsavel', 'valor_estimado', 'data'] if c in df_clientes.columns]
        st.dataframe(df_clientes[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead cadastrado.")

elif selected == "Agenda":
    st.markdown("### 📅 Agenda de Compromissos")
    st.info("Gerencie compromissos e agendamentos.")

elif selected == "Atividades":
    col_atv_t1, col_atv_t2 = st.columns([4, 1])
    with col_atv_t1:
        st.markdown("### 📞 Painel de Atividades")
    with col_atv_t2:
        if st.button("➕ Nova Atividade", use_container_width=True):
            st.session_state.modal_nova_atividade = True

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

    st.markdown(f"##### 📌 Exibindo: *{st.session_state.filtro_atividades}*")

    hoje_str = str(date.today())
    df_atv_view = df_atividades.copy() if not df_atividades.empty else pd.DataFrame()

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

    if st.session_state.modal_nova_atividade:
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

    filtro_atual = st.session_state.filtro_atividades
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

# --- ABAS DO BLOCO COMERCIAL ---
elif selected == "Pipeline":
    st.markdown("### 📈 Pipeline de Oportunidades")
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True, hide_index=True)
        fig_pipe = px.funnel(df_pipeline, x="valor", y="estagio", color_discrete_sequence=[cor_hex])
        fig_pipe.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=text_app))
        st.plotly_chart(fig_pipe, use_container_width=True)
    else:
        st.info("Nenhuma oportunidade cadastrada no pipeline.")

elif selected == "Vendas":
    st.markdown("### 💰 Gestão e Histórico de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada.")

elif selected == "Propostas":
    st.markdown("### 📄 Gestão de Propostas Comerciais")
    st.info("Painel de elaboração e controle de propostas.")

elif selected == "Relatórios":
    st.markdown("### 📊 Relatórios Comerciais e Exportação")
    st.info("Gere e exporte relatórios consolidados do CRM.")

elif selected == "Metas":
    st.markdown("### 🎯 Metas da Equipe Comercial")
    st.info("Acompanhamento de metas e desempenho.")

elif selected == "Campanhas":
    st.markdown("### 📧 Campanhas de Marketing")

elif selected == "WhatsApp":
    st.markdown("### 💬 Integração WhatsApp")

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações do Sistema")

elif selected == "Usuários":
    st.markdown("### 👤 Gestão de Usuários")

elif selected == "Permissões":
    st.markdown("### 🔒 Permissões e Perfis")

elif selected == "Notificações":
    st.markdown("### 🔔 Central de Notificações")

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações Gerais")

else:
    st.markdown(f"### ⚙️ Seção: {selected}")
    st.info("Painel em funcionamento normal.")
