import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from streamlit_option_menu import option_menu

# Configuração da Página
st.set_page_config(
    page_title="CRM Pro - Gestão Comercial",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS GLOBAL E CENTRALIZADO ---
text_app = "#ffffff"
bg_app = "#16222A"

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

# Inicialização do Banco de Dados SQLite
def conectar():
    conn = sqlite3.connect("crm_pro.db", timeout=10)
    return conn

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            empresa TEXT,
            email TEXT,
            telefone TEXT,
            status TEXT,
            origem TEXT,
            responsavel TEXT,
            prioridade TEXT,
            data TEXT,
            ultimo_contato TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            valor REAL,
            data TEXT,
            responsavel TEXT,
            status TEXT,
            produto TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            valor REAL,
            estagio TEXT,
            responsavel TEXT,
            cliente TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_exportacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            data TEXT,
            usuario TEXT
        )
    """)
    conn.commit()
    conn.close()

criar_tabelas()

# Função de Disparo de E-mail Automático
def disparar_email_automatico(destinatario, arquivo_bytes, nome_arquivo):
    servidor_smtp = "smtp.gmail.com"
    porta_smtp = 587
    remetente = "sergiolmendes2026@gmail.com"
    senha_app = "sua_senha_de_app_aqui"

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = "📊 Dashboard  & Indicadores de Desempenho"

    corpo = "Olá,\n\nSegue em anexo o relatório comercial consolidado gerado automaticamente pelo CRM Pro.\n\nAtenciosamente,\nEquipe CRM Pro"
    msg.attach(MIMEText(corpo, 'plain'))

    parte = MIMEBase('application', 'octet-stream')
    parte.set_payload(arquivo_bytes)
    encoders.encode_base64(parte)
    parte.add_header('Content-Disposition', f'attachment; filename= {nome_arquivo}')
    msg.attach(parte)

    try:
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

# Inicialização de Estados de Sessão
if "modal_novo_lead" not in st.session_state:
    st.session_state.modal_novo_lead = False
if "modal_nova_atividade" not in st.session_state:
    st.session_state.modal_nova_atividade = False
if "modal_nova_oportunidade" not in st.session_state:
    st.session_state.modal_nova_oportunidade = False

# Sidebar de Navegação
with st.sidebar:
    st.markdown("## 💼 CRM Pro 2026")
    st.markdown("---")
    selected = option_menu(
        menu_title="Menu Principal",
        options=[
            "Dashboard", "Leads", "Agenda", "Atividades", "Pipeline", 
            "Vendas", "Propostas", "Relatórios", "Metas", "Campanhas", 
            "Usuários", "Permissões", "Notificações", "Configurações"
        ],
        icons=[
            "speedometer2", "people", "calendar-check", "check2-square", "kanban",
            "cash-stack", "file-earmark-text", "bar-chart", "trophy", "megaphone",
            "person-badge", "shield-lock", "bell", "gear"
        ],
        menu_icon="cast",
        default_index=0,
    )
    st.markdown("---")
    st.markdown("👤 **Usuário:** Carlos Mendes")
    st.markdown("🟢 **Status:** Online")

# Carregamento de Dados Globais
conn = conectar()
df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
conn.close()

# Roteamento das Telas
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard Executivo & Indicadores de Desempenho")
    
    col1, col2, col3, col4 = st.columns(4)
    total_leads = len(df_clientes)
    total_vendas_val = df_vendas['valor'].sum() if not df_vendas.empty else 0.0
    total_vendas_qtd = len(df_vendas)
    ticket_medio = total_vendas_val / total_vendas_qtd if total_vendas_qtd > 0 else 0.0

    with col1:
        st.metric("Total de Leads", f"{total_leads}", "+12% este mês")
    with col2:
        st.metric("Vendas Fechadas", f"R$ {total_vendas_val:,.2f}", "+8.5%")
    with col3:
        st.metric("Negócios Ganhos", f"{total_vendas_qtd}", "+4 novos")
    with col4:
        st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}", "+2.1%")

    st.markdown("---")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("#### 📈 Evolução de Vendas Mensais")
        if not df_vendas.empty and 'data' in df_vendas.columns:
            st.line_chart(df_vendas.groupby('data')['valor'].sum())
        else:
            st.info("Sem dados suficientes para o gráfico de linhas.")
    with ch2:
        st.markdown("#### 🍩 Leads por Origem")
        if not df_clientes.empty and 'origem' in df_clientes.columns:
            st.bar_chart(df_clientes['origem'].value_counts())
        else:
            st.info("Sem dados suficientes para o gráfico de barras.")

elif selected == "Leads":
    st.markdown("### 👥 Gestão Avançada de Leads e Clientes")
    
    col_l1, col_l2 = st.columns([3, 1])
    with col_l1:
        pesquisa_lead = st.text_input("🔍 Pesquisar Lead por Nome, Empresa ou E-mail", "")
    with col_l2:
        if st.button("➕ Novo Lead Completo", use_container_width=True):
            st.session_state.modal_novo_lead = True

    if st.session_state.get("modal_novo_lead", False):
        st.markdown("---")
        st.markdown("#### 📝 Cadastro e Qualificação de Novo Lead")
        
        with st.form("form_novo_lead_completo"):
            # 1. Informações do Lead
            st.markdown("##### 1. Informações do Lead")
            cc1, cc2, cc3, cc4 = st.columns(4)
            with cc1:
                l_nome = st.text_input("Nome do Contato *")
                l_empresa = st.text_input("Empresa")
                l_cargo = st.text_input("Cargo")
                l_segmento = st.text_input("Segmento da Empresa")
            with cc2:
                l_email = st.text_input("E-mail")
                l_telefone = st.text_input("Telefone")
                l_tipo_pessoa = st.selectbox("Tipo de Cliente", ["Pessoa Jurídica", "Pessoa Física"])
                l_origem = st.selectbox("Origem", ["Google Ads", "Indicação", "LinkedIn", "Instagram", "Outros"])
            with cc3:
                l_cidade = st.text_input("Cidade/Estado")
                l_site = st.text_input("Site")
                l_linkedin = st.text_input("LinkedIn")
                l_tags = st.text_input("Tags (ex: VIP, Q3, Inbound)")
            with cc4:
                l_status = st.selectbox("Status", [
                    "🆕 Novo Lead", "📞 Primeiro Contato", "💬 Em Atendimento",
                    "📋 Proposta Enviada", "⏳ Aguardando Resposta", "🤝 Negociação",
                    "✅ Venda Fechada", "❌ Venda Perdida", "🔄 Pós-Venda"
                ])
                l_prioridade = st.selectbox("Prioridade", ["🔴 Alta", "🟡 Média", "🟢 Baixa"])
                l_responsavel = st.selectbox("Responsável", ["Carlos", "Ana", "Larissa"])

            st.markdown("---")
            # 2. Qualificação Comercial
            st.markdown("##### 2. Qualificação Comercial ⭐")
            qc1, qc2, qc3, qc4, qc5 = st.columns(5)
            with qc1:
                l_temperatura = st.selectbox("Temperatura", ["🔥 Quente", "⛅ Morno", "❄️ Frio"])
            with qc2:
                l_score = st.slider("Score do Lead (0-100)", 0, 100, 50)
            with qc3:
                l_potencial = st.selectbox("Potencial de Compra", ["Alto", "Médio", "Baixo"])
            with qc4:
                l_probabilidade = st.slider("Probabilidade de Conversão (%)", 0, 100, 30)
            with qc5:
                l_previsao_fechamento = st.text_input("Previsão de Fechamento", value=str(date.today()))

            qi1, qi2 = st.columns(2)
            with qi1:
                l_interesse_principal = st.text_input("Interesse Principal")
            with qi2:
                l_necessidade = st.text_input("Necessidade do Cliente")

            st.markdown("---")
            # 3. Informações Comerciais & Financeiras
            st.markdown("##### 3. Informações Comerciais & Financeiras")
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                l_valor = st.number_input("Valor Estimado (R$)", min_value=0.0, value=10000.0, step=1000.0)
            with fc2:
                l_produto = st.selectbox("Produto/Serviço de Interesse", ["Software A", "Software B", "Consultoria"])
            with fc3:
                l_forma_pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Boleto", "Cartão", "À vista", "Parcelado"])
            with fc4:
                l_desconto = st.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=100.0)

            st.markdown("---")
            # 4. Controle de Relacionamento
            st.markdown("##### 4. Controle de Relacionamento")
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                l_canal_contato = st.selectbox("Canal de Contato Preferido", ["WhatsApp", "E-mail", "Telefone", "Reunião", "Instagram", "Site"])
            with rc2:
                l_proxima_acao = st.text_input("Próxima Ação", value="Enviar proposta comercial")
            with rc3:
                l_data_proximo_contato = st.text_input("Data do Próximo Contato", value=str(date.today()))

            l_obs = st.text_area("5. Histórico Inicial / Observações")

            btn_salvar_lead = st.form_submit_button("💾 Salvar Lead Completo")
            if btn_salvar_lead:
                if l_nome:
                    conn = conectar()
                    # Certifique-se de ajustar a query caso seu banco possua mais colunas correspondentes
                    conn.execute("""
                        INSERT INTO clientes (
                            nome, empresa, email, telefone, status, origem, responsavel, prioridade, 
                            data, ultimo_contato, valor, produto, temperatura, score, proxima_acao
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        l_nome, l_empresa, l_email, l_telefone, l_status, l_origem, l_responsavel, l_prioridade, 
                        str(date.today()), str(date.today()), l_valor, l_produto, l_temperatura, l_score, l_proxima_acao
                    ))
                    conn.commit()
                    conn.close()
                    st.success("Lead cadastrado com sucesso!")
                    st.session_state.modal_novo_lead = False
                    st.rerun()
                else:
                    st.error("O campo Nome do Contato é obrigatório.")

        if st.button("❌ Fechar Formulário"):
            st.session_state.modal_novo_lead = False
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Tabela Dinâmica de Leads")
    
    # Filtros Avançados na Tabela
    with st.expander("🔎 Filtros Avançados da Tabela"):
        fa1, fa2, fa3, fa4 = st.columns(4)
        with fa1:
            filtro_status = st.selectbox("Filtrar por Status", ["Todos"] + [
                "🆕 Novo Lead", "📞 Primeiro Contato", "💬 Em Atendimento",
                "📋 Proposta Enviada", "⏳ Aguardando Resposta", "🤝 Negociação",
                "✅ Venda Fechada", "❌ Venda Perdida", "🔄 Pós-Venda"
            ])
        with fa2:
            filtro_temp = st.selectbox("Filtrar por Temperatura", ["Todas", "🔥 Quente", "⛅ Morno", "❄️ Frio"])
        with fa3:
            filtro_prioridade = st.selectbox("Filtrar por Prioridade", ["Todas", "🔴 Alta", "🟡 Média", "🟢 Baixa"])
        with fa4:
            filtro_resp = st.selectbox("Filtrar por Responsável", ["Todos", "Carlos", "Ana", "Larissa"])

    # Lógica de exibição com os filtros aplicados
    if 'df_clientes' in locals() and not df_clientes.empty:
        df_filtrado = df_clientes.copy()
        
        # Aplicação da barra de pesquisa geral
        if pesquisa_lead:
            df_filtrado = df_filtrado[
                df_filtrado['nome'].str.contains(pesquisa_lead, case=False, na=False) |
                df_filtrado['empresa'].str.contains(pesquisa_lead, case=False, na=False) |
                df_filtrado['email'].str.contains(pesquisa_lead, case=False, na=False)
            ]
            
        # Aplicação dos filtros do expander
        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
        if filtro_temp != "Todas":
            df_filtrado = df_filtrado[df_filtrado['temperatura'] == filtro_temp]
        if filtro_prioridade != "Todas":
            df_filtrado = df_filtrado[df_filtrado['prioridade'] == filtro_prioridade]
        if filtro_resp != "Todos":
            df_filtrado = df_filtrado[df_filtrado['responsavel'] == filtro_resp]

        if not df_filtrado.empty:
            colunas_exibicao = [c for c in ['id', 'nome', 'empresa', 'status', 'temperatura', 'valor', 'responsavel', 'proxima_acao'] if c in df_filtrado.columns]
            st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum lead encontrado com os filtros selecionados.")
    else:
        st.info("Nenhum lead cadastrado no sistema.")

elif selected == "Agenda":
    st.markdown("### 📅 Agenda e Compromissos Comerciais")
    ag1, ag2 = st.columns([2, 1])
    with ag1:
        st.markdown("#### 🗓️ Calendário de Reuniões & Demonstrações")
        st.date_input("Selecione a Data para Visualizar:", value=date.today())
        st.markdown("---")
        st.markdown("##### ⏰ Próximos Compromissos Hoje")
        st.info("• **10:00** - Reunião de Alinhamento com Tech Solutions (Carlos)\n• **14:30** - Demonstração Software A - Inova Corp (Ana)\n• **16:00** - Fechamento de Proposta - Global Ltda (Carlos)")
    with ag2:
        st.markdown("#### ➕ Agendar Novo Evento")
        with st.form("form_novo_evento"):
            ev_titulo = st.text_input("Título do Evento")
            ev_tipo = st.selectbox("Tipo", ["Reunião", "Ligação", "Demonstração", "Follow-up"])
            ev_data = st.date_input("Data do Evento")
            ev_resp = st.selectbox("Responsável", ["Carlos", "Ana", "Larissa"])
            ev_submit = st.form_submit_button("📅 Agendar na Agenda")
            if ev_submit:
                st.success(f"Evento '{ev_titulo}' agendado com sucesso para {ev_data}!")

elif selected == "Atividades":
    st.markdown("### 📋 Gestão de Tarefas e Atividades Diárias")
    
    col_at1, col_at2 = st.columns([3, 1])
    with col_at1:
        st.session_state.filtro_atividades = st.selectbox(
            "Filtrar Atividades", 
            ["Todas as atividades", "Pendentes", "Concluídas", "Atrasadas"],
            label_visibility="collapsed"
        )
    with col_at2:
        if st.button("➕ Nova Atividade", use_container_width=True):
            st.session_state.modal_nova_atividade = True

    if st.session_state.modal_nova_atividade:
        with st.form("form_nova_atividade"):
            st.markdown("##### Criar Nova Tarefa")
            t_titulo = st.text_input("Título da Atividade")
            t_desc = st.text_area("Descrição")
            t_vencimento = st.date_input("Data de Vencimento")
            t_resp = st.selectbox("Responsável Atribuído", ["Carlos", "Ana", "Larissa"])
            t_btn = st.form_submit_button("Salvar Tarefa")
            if t_btn:
                st.success("Atividade criada com sucesso!")
                st.session_state.modal_nova_atividade = False
                st.rerun()

    st.markdown("---")
    df_tarefas = pd.DataFrame([
        {"Tarefa": "Ligar para João Silva", "Vencimento": "2026-08-15", "Responsável": "Carlos", "Status": "Pendente", "Prioridade": "🔴 Alta"},
        {"Tarefa": "Enviar proposta comercial Alpha Tech", "Vencimento": "2026-08-14", "Responsável": "Ana", "Status": "Concluída", "Prioridade": "🟡 Média"},
        {"Tarefa": "Revisar contrato Global Ltda", "Vencimento": "2026-08-18", "Responsável": "Carlos", "Status": "Pendente", "Prioridade": "🟢 Baixa"}
    ])
    st.dataframe(df_tarefas, use_container_width=True, hide_index=True)

elif selected == "Pipeline":
    st.markdown("### 🔄 Pipeline de Vendas & Negócios em Andamento")
    
    col_pipe1, col_pipe2 = st.columns([3, 1])
    with col_pipe1:
        st.markdown("Gerencie suas oportunidades atualizando as etapas do funil comercial.")
    with col_pipe2:
        if st.button("➕ Nova Oportunidade", use_container_width=True):
            st.session_state.modal_nova_oportunidade = True

    if not df_pipeline.empty:
        estagios = ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"]
        cols_estagios = st.columns(len(estagios))
        
        for i, estagio in enumerate(estagios):
            with cols_estagios[i]:
                st.markdown(f"<div style='background-color: #1e293b; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;'>{estagio}</div>", unsafe_allow_html=True)
                df_estagio = df_pipeline[df_pipeline["estagio"] == estagio]
                for _, row in df_estagio.iterrows():
                    st.markdown(f"""
                        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 10px; margin-top: 10px;">
                            <strong>{row['titulo']}</strong><br>
                            <span style="color: #38bdf8;">R$ {row['valor']:,.2f}</span><br>
                            <small style="color: #94a3b8;">Resp: {row['responsavel']}</small>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma oportunidade cadastrada no pipeline.")

elif selected == "Vendas":
    st.markdown("### 💰 Registro e Histórico de Vendas Realizadas")
    
    with st.form("form_nova_venda"):
        st.markdown("##### Registrar Nova Venda")
        v_cli = st.text_input("Nome do Cliente / Empresa")
        v_val = st.number_input("Valor da Venda (R$)", min_value=0.0, value=5000.0, step=500.0)
        v_prod = st.selectbox("Produto / Serviço", ["Software A", "Software B", "Consultoria"])
        v_resp = st.selectbox("Consultor Responsável", ["Carlos", "Ana", "Larissa"])
        v_status = st.selectbox("Status do Pagamento", ["Pago", "Pendente", "Parcelado"])
        v_data = st.text_input("Data da Venda", value=str(date.today()))
        
        v_btn = st.form_submit_button("💾 Salvar Venda")
        if v_btn:
            if v_cli:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel, status, produto) VALUES (?, ?, ?, ?, ?, ?)",
                           (v_cli, v_val, v_data, v_resp, v_status, v_prod))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Informe o nome do cliente.")

    st.markdown("---")
    st.markdown("#### 📋 Listagem de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada.")

elif selected == "Propostas":
    st.markdown("### 📄 Gestão de Propostas Comerciais")
    st.info("Aqui você pode criar, editar e enviar propostas comerciais diretamente para seus clientes.")
    
    with st.form("form_proposta"):
        p_cliente = st.text_input("Cliente Destinatário")
        p_servico = st.selectbox("Serviço / Produto", ["Software A", "Software B", "Consultoria Avançada"])
        p_valor = st.number_input("Valor Total Proposto (R$)", value=12000.0)
        p_validade = st.date_input("Validade da Proposta")
        p_condicoes = st.text_area("Condições de Pagamento", value="50% entrada + 50% na entrega")
        
        p_submit = st.form_submit_button("Gerar Proposta Comercial")
        if p_submit:
            st.success(f"Proposta gerada com sucesso para {p_cliente} no valor de R$ {p_valor:,.2f}!")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios Executivos & Central de Exportação")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("#### Exportar Relatório Comercial")
        tipo_rel = st.selectbox("Selecione o Relatório", ["Vendas Consolidadas", "Base de Clientes & Leads", "Pipeline de Oportunidades"])
        formato_rel = st.radio("Formato do Arquivo", ["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"])
        email_destino = st.text_input("Enviar por e-mail para:", value="sergiolmendes2026@gmail.com")
        
        if st.button("🚀 Processar e Enviar Relatório"):
            buffer = io.BytesIO()
            if not df_vendas.empty and tipo_rel == "Vendas Consolidadas":
                df_vendas.to_csv(buffer, index=False)
                nome_arq = "relatorio_vendas.csv"
            else:
                df_clientes.to_csv(buffer, index=False) if not df_clientes.empty else pd.DataFrame().to_csv(buffer)
                nome_arq = "relatorio_geral.csv"
            
            buffer.seek(0)
            sucesso_email = disparar_email_automatico(email_destino, buffer.getvalue(), nome_arq)
            if sucesso_email:
                st.success(f"Relatório gerado e enviado com sucesso para {email_destino}!")
            else:
                st.error("Erro ao enviar o e-mail automático. Verifique as credenciais SMTP.")

    with r_col2:
        st.markdown("#### 🕒 Histórico de Exportações Recentes")
        conn = conectar()
        df_hist = pd.read_sql("SELECT * FROM historico_exportacoes", conn)
        conn.close()
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma exportação recente registrada.")

elif selected == "Metas":
    st.markdown("### ⛰️ Metas Comerciais e Acompanhamento de Equipe")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### 🎯 Meta Geral da Empresa (2026)")
        st.progress(0.72)
        st.markdown("**Progresso Atual:** 72% atingido (R$ 108.000 / R$ 150.000)")
    with col_m2:
        st.markdown("#### 🏆 Metas por Consultor")
        st.markdown("• **Carlos:** 85% da meta mensal atingida\n• **Ana:** 94% da meta mensal atingida\n• **Larissa:** 60% da meta mensal atingida")

elif selected == "Campanhas":
    st.markdown("### 📢 Campanhas de Marketing & Disparos")
    st.info("Gerencie campanhas de e-mail marketing, disparos via WhatsApp e anúncios integrados.")
    
    with st.form("form_campanha"):
        c_nome = st.text_input("Nome da Campanha")
        c_canal = st.selectbox("Canal", ["E-mail Marketing", "WhatsApp", "Remarketing Google Ads"])
        c_publico = st.selectbox("Público-Alvo", ["Todos os Leads", "Leads Frios (> 30 dias)", "Clientes Fechados (Pós-Venda)"])
        c_mensagem = st.text_area("Corpo da Mensagem / Oferta")
        
        c_btn = st.form_submit_button("🚀 Disparar Campanha")
        if c_btn:
            st.success(f"Campanha '{c_nome}' iniciada com sucesso via {c_canal}!")

elif selected == "Usuários":
    st.markdown("### 👤 Gestão de Usuários do Sistema")
    st.markdown("Adicione e gerencie os colaboradores que possuem acesso ao CRM Pro.")
    
    df_usuarios = pd.DataFrame([
        {"Nome": "Carlos Mendes", "E-mail": "carlos@crm.com", "Perfil": "Administrador", "Status": "Ativo"},
        {"Nome": "Ana Paula", "E-mail": "ana@crm.com", "Perfil": "Comercial Sênior", "Status": "Ativo"},
        {"Nome": "Larissa Souza", "E-mail": "larissa@crm.com", "Perfil": "Comercial Júnior", "Status": "Ativo"}
    ])
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

elif selected == "Permissões":
    st.markdown("### 🛡️ Controle de Permissões e Perfis de Acesso")
    st.selectbox("Selecione o Perfil para Editar", ["Administrador", "Gerente Comercial", "Consultor Padrão"])
    st.checkbox("Permitir exclusão de registros", value=True)
    st.checkbox("Permitir visualização de relatórios financeiros", value=False)
    st.checkbox("Permitir exportação de dados", value=True)
    if st.button("Salvar Permissões"):
        st.success("Permissões atualizadas com sucesso!")

elif selected == "Notificações":
    st.markdown("### 🔔 Configuração de Notificações & Alertas")
    st.checkbox("Receber e-mail diário de resumo comercial", value=True)
    st.checkbox("Alertar sobre leads sem contato há mais de 5 dias", value=True)
    st.checkbox("Notificar quando uma venda for fechada", value=True)
    if st.button("Salvar Preferências de Notificação"):
        st.success("Preferências salvas com sucesso!")

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações Gerais do Sistema")
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        st.selectbox("Tema do Sistema", ["🌙 Escuro", "☀️ Claro"], key="tema_sistema")
        st.text_input("Nome da Empresa no Sistema", value="LMB Pro Ltda")
    with col_cfg2:
        st.text_input("Moeda Padrão", value="BRL (R$)")
        st.text_input("E-mail de Suporte Técnico", value="suporte@crmlmb.com")
        
    if st.button("💾 Salvar Configurações Gerais"):
        st.success("Configurações atualizadas com sucesso! Recarregue a página se necessário.")
