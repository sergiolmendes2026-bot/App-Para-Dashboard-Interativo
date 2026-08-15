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
    
    # 1. KPIs no Topo
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("📅 Hoje", "4")
    with kpi2:
        st.metric("⏰ Próximos", "8")
    with kpi3:
        st.metric("🤝 Reuniões", "3")
    with kpi4:
        st.metric("📞 Ligações", "2")
    with kpi5:
        st.metric("⚠️ Pendentes", "3")

    st.markdown("---")

    # Layout em abas ou colunas para organizar o Calendário/Lista vs Agendamento
    col_ag1, col_ag2 = st.columns([2, 1])

    with col_ag1:
        st.markdown("#### 📆 Calendário & Próximos Compromissos")
        
        # Filtro rápido de data / visualização
        data_selecionada = st.date_input("Selecione a Data para Visualizar", value=date.today())
        
        st.markdown("##### ⏰ Compromissos de Hoje / Data Selecionada")
        st.info("• 10:00 - 🤝 Reunião de Alinhamento com Tech Solutions (Carlos) | Status: 🟡 Confirmado\n\n"
                "• 14:30 - 💻 Demonstração Software A - Inova Corp (Ana) | Status: 🔵 Agendado\n\n"
                "• 16:00 - 📄 Fechamento de Proposta - Global Ltda (Carlos) | Status: 🟡 Confirmado")

        st.markdown("---")
        
        # 7. Histórico / Todos os Compromissos com Filtros
        st.markdown("#### 📋 Todos os Compromissos")
        f_busca_agenda = st.text_input("🔎 Pesquisar compromisso...", "")
        
        f_periodo = st.radio("Período:", ["Hoje", "Semana", "Mês", "Todos"], horizontal=True)
        
        # Exemplo estruturado de tabela de compromissos
        import pandas as pd
        dados_compromissos = pd.DataFrame([
            {"Horário": "10:00", "Evento": "Reunião", "Lead": "Tech Solutions", "Responsável": "Carlos", "Status": "🟡 Confirmado"},
            {"Horário": "14:30", "Evento": "Demonstração", "Lead": "Inova Corp", "Responsável": "Ana", "Status": "🔵 Agendado"},
            {"Horário": "16:00", "Evento": "Fechamento", "Lead": "Global Ltda", "Responsável": "Carlos", "Status": "🟢 Concluído"}
        ])
        st.dataframe(dados_compromissos, use_container_width=True, hide_index=True)

    with col_ag2:
        st.markdown("#### ➕ Agendar Novo Evento")
        
        with st.form("form_agendar_evento_completo"):
            ev_titulo = st.text_input("Título do Evento")
            ev_tipo = st.selectbox("Tipo de Evento", ["Reunião", "Demonstração", "Ligação", "Follow-up", "Proposta", "Fechamento"])
            
            # Relacionar com Lead/Cliente cadastrado
            ev_lead = st.text_input("Lead / Cliente (Empresa)")
            ev_responsavel = st.selectbox("Responsável", ["Carlos", "Ana", "Larissa"])
            
            ev_data = st.date_input("Data do Evento", value=date.today())
            
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                ev_hora_inicio = st.text_input("Hora Início", value="10:00")
            with col_h2:
                ev_hora_fim = st.text_input("Hora Fim", value="11:00")
                
            ev_local = st.text_input("Local / Link da Reunião", value="Google Meet")
            
            ev_lembrete = st.selectbox("Lembrete", [
                "5 minutos antes", "15 minutos antes", "30 minutos antes", "1 hora antes", "1 dia antes"
            ])
            
            ev_notificar = st.multiselect("Notificar por", ["🔔 Sistema", "📧 E-mail", "💬 WhatsApp"], default=["🔔 Sistema"])
            
            ev_status = st.selectbox("Status do Compromisso", [
                "🔵 Agendado", "🟡 Confirmado", "🟣 Em andamento", "🟢 Concluído", "🔴 Cancelado", "⚠️ Não compareceu", "🔄 Reagendado"
            ])
            
            ev_descricao = st.text_area("Descrição / Pauta da Reunião")

            btn_salvar_evento = st.form_submit_button("💾 Agendar Evento")
            if btn_salvar_evento:
                if ev_titulo:
                    st.success("Compromisso agendado com sucesso!")
                    st.rerun()
                else:
                    st.error("O Título do Evento é obrigatório.")

elif selected == "Atividades":
    st.markdown("### 📋 Gestão de Tarefas e Atividades Diárias")
    
    # 📊 1. KPIs no Topo
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("📋 Total", "24")
    with kpi2:
        st.metric("🔵 Pendentes", "12")
    with kpi3:
        st.metric("🟢 Concluídas", "8")
    with kpi4:
        st.metric("🔴 Atrasadas", "3")
    with kpi5:
        st.metric("⚠️ Alta Prioridade", "5")

    st.markdown("---")

    # Layout dividindo a tela principal entre Tabela/Alertas e o Formulário de Nova Atividade
    col_at1, col_at2 = st.columns([2, 1])

    with col_at1:
        # 🚨 7. Seção de Atividades Atrasadas
        st.markdown("#### 🚨 Atividades Atrasadas")
        st.error(
            "**🔴 Ligar para João Silva**\n"
            "• Vencimento: 14/08/2026 | Responsável: Carlos\n\n"
            "**🔴 Enviar proposta Alpha Tech**\n"
            "• Vencimento: 15/08/2026 | Responsável: Ana"
        )
        
        st.markdown("---")
        
        # 🔎 6. Filtros e Pesquisa da Tabela
        st.markdown("#### 📋 Painel de Atividades")
        f_pesquisa_ativ = st.text_input("🔎 Pesquisar atividade...", "")
        
        f1, f2, f3 = st.columns(3)
        with f1:
            filtro_status_ativ = st.selectbox("Status", ["Todas", "Pendente", "Em andamento", "Concluída", "Cancelada"])
        with f2:
            filtro_periodo_ativ = st.selectbox("Período", ["Hoje", "Semana", "Mês", "Todos"])
        with f3:
            filtro_prioridade_ativ = st.selectbox("Prioridade", ["Todas", "🔴 Alta", "🟡 Média", "🟢 Baixa"])

        # 📋 5. Tabela de Atividades Estilizada
        import pandas as pd
        dados_atividades = pd.DataFrame([
            {
                "Data/Hora": "15/08 10:00", 
                "Tipo": "📞 Ligação", 
                "Atividade": "Follow-up", 
                "Lead/Cliente": "João Silva — Tech Solutions", 
                "Responsável": "Carlos", 
                "Status": "Pendente", 
                "Prioridade": "🔴 Alta"
            },
            {
                "Data/Hora": "16/08 14:00", 
                "Tipo": "📧 E-mail", 
                "Atividade": "Enviar proposta", 
                "Lead/Cliente": "Alpha Tech", 
                "Responsável": "Ana", 
                "Status": "Concluída", 
                "Prioridade": "🟡 Média"
            },
            {
                "Data/Hora": "18/08 09:30", 
                "Tipo": "📄 Tarefa", 
                "Atividade": "Revisar contrato", 
                "Lead/Cliente": "Global Ltda", 
                "Responsável": "Carlos", 
                "Status": "Pendente", 
                "Prioridade": "🟢 Baixa"
            }
        ])
        
        st.dataframe(dados_atividades, use_container_width=True, hide_index=True)

        st.markdown("---")
        
        # 🕐 8. Histórico Recente de Atividades Concluídas
        st.markdown("#### 🕒 Histórico Recente")
        st.markdown(
            "* **Hoje — 14:30** | ✅ Proposta enviada para Alpha Tech *(Carlos)*\n"
            "* **Hoje — 11:20** | 📞 Ligação realizada com João Silva *(Carlos)*\n"
            "* **Ontem — 16:40** | 📧 E-mail enviado para Global Ltda *(Ana)*"
        )

    with col_at2:
        # 📝 2. & 3. & 4. Formulário de Nova Atividade Completo e Vinculado
        st.markdown("#### ➕ Nova Atividade")
        
        with st.form("form_nova_atividade_completo"):
            at_tipo = st.selectbox("Tipo de Atividade", [
                "📞 Ligação", "📧 E-mail", "💬 WhatsApp", "🤝 Reunião", 
                "🔄 Follow-up", "📄 Tarefa", "💻 Demonstração", "📊 Proposta"
            ])
            
            at_titulo = st.text_input("Título / Assunto da Atividade")
            
            # 👤 Vínculo com Lead/Cliente
            at_lead = st.text_input("Lead / Cliente Relacionado", placeholder="Ex: João Silva — Tech Solutions")
            
            at_responsavel = st.selectbox("Responsável", ["Carlos", "Ana", "Larissa"])
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                at_data = st.date_input("Data de Vencimento", value=date.today())
            with col_d2:
                at_hora = st.text_input("Hora", value="10:00")
                
            at_prioridade = st.selectbox("Prioridade", ["🔴 Alta", "🟡 Média", "🟢 Baixa"])
            
            at_status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluída", "Cancelada"])
            
            at_descricao = st.text_area("Descrição / Pauta")
            
            # 🔄 4. Próxima Ação
            st.markdown("---")
            st.markdown("##### 🔄 Próxima Ação (Pós-Atividade)")
            at_resultado = st.text_input("Resultado / Observação")
            at_proxima_acao = st.text_input("Próxima Ação Comercial")
            at_data_proxima = st.date_input("Data da Próxima Ação", value=date.today())

            btn_salvar_ativ = st.form_submit_button("💾 Salvar Atividade")
            if btn_salvar_ativ:
                if at_titulo:
                    st.success("Atividade salva e integrada ao histórico com sucesso!")
                    st.rerun()
                else:
                    st.error("O Título da Atividade é obrigatório.")

elif selected == "Vendas":
    st.markdown("### 💰 Gestão de Vendas e Fechamentos Comerciais")
    
    # 📊 1. KPIs de Vendas no Topo
    kpi_v1, kpi_v2, kpi_v3, kpi_v4, kpi_v5 = st.columns(5)
    with kpi_v1:
        st.metric("💰 Total Vendido", "R$ 148.500", "+12%")
    with kpi_v2:
        st.metric("🎯 Vendas no Mês", "14", "+3")
    with kpi_v3:
        st.metric("📈 Ticket Médio", "R$ 10.600", "+5%")
    with kpi_v4:
        st.metric("⏳ Em Negociação", "R$ 62.000", "5 Propostas")
    with kpi_v5:
        st.metric("❌ Taxa de Perda", "18%", "-2%")

    st.markdown("---")

    # Layout dividindo entre a Tabela/Filtros e o Formulário de Nova Venda
    col_v1, col_v2 = st.columns([2, 1])

    with col_v1:
        # 🔎 6. Filtros e Pesquisa da Tabela de Vendas
        st.markdown("#### 📋 Histórico e Pipeline de Vendas")
        f_pesquisa_venda = st.text_input("🔎 Pesquisar venda por cliente, empresa ou produto...", "")
        
        fv1, fv2, fv3 = st.columns(3)
        with fv1:
            filtro_status_venda = st.selectbox("Status da Venda", ["Todas", "✅ Fechada", "⏳ Em Negociação", "❌ Perdida", "🔄 Recorrente"])
        with fv2:
            filtro_periodo_venda = st.selectbox("Período de Venda", ["Este Mês", "Últimos 3 Meses", "Este Ano", "Todos"])
        with fv3:
            filtro_resp_venda = st.selectbox("Responsável", ["Todos", "Carlos", "Ana", "Larissa"])

        # 📋 5. Tabela de Vendas Estilizada
        import pandas as pd
        dados_vendas = pd.DataFrame([
            {
                "Data": "15/08/2026", 
                "Cliente / Empresa": "João Silva — Tech Solutions", 
                "Produto": "Software A (Enterprise)", 
                "Valor (R$)": "R$ 24.500", 
                "Responsável": "Carlos", 
                "Pagamento": "💳 Cartão (12x)", 
                "Status": "✅ Fechada"
            },
            {
                "Data": "14/08/2026", 
                "Cliente / Empresa": "Alpha Tech", 
                "Produto": "Consultoria Q3", 
                "Valor (R$)": "R$ 12.000", 
                "Responsável": "Ana", 
                "Pagamento": "📄 Boleto", 
                "Status": "⏳ Em Negociação"
            },
            {
                "Data": "12/08/2026", 
                "Cliente / Empresa": "Global Ltda", 
                "Produto": "Software B", 
                "Valor (R$)": "R$ 45.000", 
                "Responsável": "Carlos", 
                "Pagamento": "🔀 PIX / À vista", 
                "Status": "✅ Fechada"
            }
        ])
        
        st.dataframe(dados_vendas, use_container_width=True, hide_index=True)

        st.markdown("---")
        
        # 🕒 8. Resumo Recente de Fechamentos
        st.markdown("#### 🏆 Últimas Conquistas Comerciais")
        st.markdown(
            "* **Hoje — 16:00** | 🎉 Venda fechada com **Tech Solutions** no valor de **R$ 24.500** *(Carlos)*\n"
            "* **12/08 — 14:10** | 🎉 Contrato assinado com **Global Ltda** no valor de **R$ 45.000** *(Carlos)*\n"
            "* **10/08 — 09:30** | 📝 Proposta avançada para **Inova Corp** *(Ana)*"
        )

    with col_v2:
        # 📝 2. & 3. Formulário de Registro de Nova Venda / Fechamento
        st.markdown("#### ➕ Registrar Nova Venda")
        
        with st.form("form_nova_venda_completo"):
            v_cliente = st.text_input("Lead / Cliente (Empresa)", placeholder="Ex: João Silva — Tech Solutions")
            
            v_produto = st.selectbox("Produto / Serviço", ["Software A", "Software B", "Consultoria", "Plano Customizado"])
            
            col_vv1, col_vv2 = st.columns(2)
            with col_vv1:
                v_valor = st.number_input("Valor Final (R$)", min_value=0.0, value=15000.0, step=500.0)
            with col_vv2:
                v_desconto = st.number_input("Desconto Aplicado (R$)", min_value=0.0, value=0.0, step=100.0)
                
            v_pagamento = st.selectbox("Forma de Pagamento", ["🔀 PIX", "📄 Boleto Bancário", "💳 Cartão de Crédito", "💵 À vista", "📊 Parcelado"])
            
            v_responsavel = st.selectbox("Responsável pela Venda", ["Carlos", "Ana", "Larissa"])
            
            v_data = st.date_input("Data do Fechamento", value=date.today())
            
            v_status = st.selectbox("Status da Oportunidade", ["✅ Fechada (Venda Concluída)", "⏳ Em Negociação / Proposta", "❌ Perdida"])
            
            v_observacoes = st.text_area("Observações do Contrato / Fechamento")

            btn_salvar_venda = st.form_submit_button("💾 Salvar Venda")
            if btn_salvar_venda:
                if v_cliente:
                    st.success("Venda registrada com sucesso e integrada ao dashboard!")
                    st.rerun()
                else:
                    st.error("O campo Cliente / Empresa é obrigatório.")

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
    st.markdown("### 📊 Relatórios Executivos & Central de Exportação")
    
    # 📊 1. KPIs do Relatório no Topo
    kpi_r1, kpi_r2, kpi_r3, kpi_r4 = st.columns(4)
    with kpi_r1:
        st.metric("👥 Leads", "128", "+12")
    with kpi_r2:
        st.metric("💰 Vendas", "23", "+4")
    with kpi_r3:
        st.metric("💵 Faturamento", "R$ 125.500", "+15%")
    with kpi_r4:
        st.metric("📈 Conversão", "18%", "+2.5%")

    st.markdown("---")

    # Layout de Configuração do Relatório
    st.markdown("#### 📑 Configurar Relatório")
    
    # 📑 4. Tipos de Relatórios Expandidos
    tipo_relatorio = st.selectbox("Selecione o Tipo de Relatório", [
        "📊 Vendas Consolidadas", "👥 Relatório de Leads", "🎯 Conversão de Leads", 
        "💰 Faturamento", "📈 Performance Comercial", "🏆 Performance por Vendedor", 
        "📦 Vendas por Produto", "💳 Relatório de Pagamentos", "📋 Pipeline Comercial", 
        "📅 Atividades e Compromissos", "📄 Propostas", "📣 Campanhas"
    ])

    # 📊 1. Filtros Avançados do Relatório
    st.markdown("##### 🔎 Filtros do Relatório")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        per_inicio = st.date_input("Data Inicial", value=date(2026, 8, 1))
    with f_col2:
        per_fim = st.date_input("Data Final", value=date(2026, 8, 31))
    with f_col3:
        f_resp = st.selectbox("Responsável", ["Todos", "Carlos", "Ana", "Larissa"])

    f_col4, f_col5, f_col6, f_col7 = st.columns(4)
    with f_col4:
        f_prod = st.selectbox("Produto/Serviço", ["Todos", "Software A", "Software B", "Consultoria"])
    with f_col5:
        f_status = st.selectbox("Status", ["Todos", "Pago / Fechado", "Pendente", "Em Negociação"])
    with f_col6:
        f_origem = st.selectbox("Origem", ["Todas", "Google Ads", "Indicação", "LinkedIn", "Instagram"])
    with f_col7:
        f_pipeline = st.selectbox("Pipeline / Etapa", ["Todas", "Qualificação", "Proposta", "Fechamento"])

    st.markdown("---")

    # 📋 3. Pré-visualização & 📊 2. Resumo
    col_prev1, col_prev2 = st.columns([2, 1])

    with col_prev1:
        st.markdown("#### 👁️ Pré-visualização dos Dados")
        import pandas as pd
        df_preview = pd.DataFrame([
            {"Cliente": "João Silva", "Produto": "Software A", "Valor": "R$ 5.000", "Responsável": "Carlos", "Status": "Pago"},
            {"Cliente": "Alpha Tech", "Produto": "Software B", "Valor": "R$ 8.500", "Responsável": "Ana", "Status": "Pendente"},
            {"Cliente": "Global Ltda", "Produto": "Enterprise", "Valor": "R$ 12.000", "Responsável": "Carlos", "Status": "Pago"}
        ])
        st.dataframe(df_preview, use_container_width=True, hide_index=True)

    with col_prev2:
        st.markdown("#### 📊 Resumo Executivo")
        st.info(
            "• **Total Registros:** 3\n\n"
            "• **Valor Total:** R$ 25.500\n\n"
            "• **Ticket Médio:** R$ 8.500\n\n"
            "• **Taxa de Sucesso:** 66.6%"
        )

    st.markdown("---")

    # 📤 5. Opções de Exportação Avançadas
    st.markdown("#### 📤 Opções de Exportação")
    
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        formato_export = st.radio("Formato de Saída", ["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"], horizontal=True)
    with exp_col2:
        st.markdown("**Configurações Adicionais:**")
        chk_resumo = st.checkbox("Incluir resumo executivo", value=True)
        chk_graficos = st.checkbox("Incluir gráficos analíticos", value=True)
        chk_filtros = st.checkbox("Incluir filtros aplicados no rodapé", value=True)

    # Botões de Ação Separados
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("👁️ Visualizar Relatório Completo", use_container_width=True):
            st.success("Relatório gerado para visualização em tela!")
    with b2:
        if st.button("📥 Exportar Arquivo", use_container_width=True):
            st.success(f"Arquivo exportado com sucesso no formato {formato_export}!")
    with b3:
        if st.button("📧 Enviar por E-mail", use_container_width=True):
            st.success("Relatório enviado por e-mail para a diretoria com sucesso!")

    st.markdown("---")

    # 🕒 6. Histórico de Exportações
    st.markdown("#### 🕒 Histórico de Exportações Recentes")
    df_historico = pd.DataFrame([
        {"Data": "15/08 14:30", "Relatório": "Vendas Consolidadas", "Período": "Agosto/2026", "Formato": "Excel", "Usuário": "Carlos"},
        {"Data": "15/08 13:10", "Relatório": "Relatório de Leads", "Período": "Agosto/2026", "Formato": "PDF", "Usuário": "Ana"}
    ])
    st.dataframe(df_historico, use_container_width=True, hide_index=True)

elif selected == "Metas":
    st.markdown("### 🎯 Metas Comerciais e Acompanhamento de Equipe")
    
    # 📊 1. KPIs no Topo (5 Cards)
    kpi_m1, kpi_m2, kpi_m3, kpi_m4, kpi_m5 = st.columns(5)
    with kpi_m1:
        st.metric("🎯 Meta Total", "R$ 150.000")
    with kpi_m2:
        st.metric("💰 Realizado", "R$ 108.000")
    with kpi_m3:
        st.metric("📊 Atingimento", "72%")
    with kpi_m4:
        st.metric("⏳ Falta", "R$ 42.000")
    with kpi_m5:
        st.metric("📅 Dias Restantes", "16 dias")

    st.markdown("---")

    # Layout Principal em Colunas
    col_m_esq, col_m_dir = st.columns([2, 1])

    with col_m_esq:
        # 🎯 2. Meta Geral Mais Completa & Barra de Progresso
        st.markdown("#### 🎯 Meta Comercial — Agosto 2026")
        
        mg1, mg2, mg3, mg4 = st.columns(4)
        with mg1:
            st.markdown("**Meta:** R$ 150.000")
        with mg2:
            st.markdown("**Realizado:** R$ 108.000")
        with mg3:
            st.markdown("**Faltante:** R$ 42.000")
        with mg4:
            st.markdown("**Atingimento:** 72%")
            
        # Barra de progresso visual do Streamlit
        st.progress(0.72)
        
        mp1, mp2 = st.columns(2)
        with mp1:
            st.info("💡 **Meta diária necessária:** R$ 2.625")
        with mp2:
            st.success("🚀 **Previsão de fechamento:** R$ 164.000 (Superada)")

        st.markdown("---")

        # 📈 8. Gráfico de Evolução (Meta acumulada x Realizado)
        st.markdown("#### 📈 Evolução da Meta (Acumulado)")
        import pandas as pd
        import numpy as np
        
        # Exemplo de dados para o gráfico de evolução temporal
        dias_mes = [f"Dia {i*5}" for i in range(1, 7)]
        df_evolucao = pd.DataFrame({
            "Meta Acumulada": [25000, 50000, 75000, 100000, 125000, 150000],
            "Realizado Acumulado": [20000, 48000, 72000, 95000, 108000, 108000]
        }, index=dias_mes)
        st.line_chart(df_evolucao)

        st.markdown("---")

        # 👥 3. Metas por Consultor (Tabela Detalhada)
        st.markdown("#### 🏆 Desempenho e Metas por Consultor")
        df_consultores = pd.DataFrame([
            {"Consultor": "Ana", "Meta": "R$ 50k", "Realizado": "R$ 47k", "% Atingido": "94%", "Faltante": "R$ 3k", "Previsão": "R$ 61k", "Status": "🟢 Ótimo"},
            {"Consultor": "Carlos", "Meta": "R$ 50k", "Realizado": "R$ 42,5k", "% Atingido": "85%", "Faltante": "R$ 7,5k", "Previsão": "R$ 54k", "Status": "🟢 No Ritmo"},
            {"Consultor": "Larissa", "Meta": "R$ 50k", "Realizado": "R$ 30k", "% Atingido": "60%", "Faltante": "R$ 20k", "Previsão": "R$ 39k", "Status": "🟡 Atenção"}
        ])
        st.dataframe(df_consultores, use_container_width=True, hide_index=True)

        st.markdown("---")

        # 📊 4. Outros Tipos de Metas (Métricas Secundárias)
        st.markdown("#### 📊 Outras Metas Operacionais do Período")
        om1, om2, om3, om4, om5 = st.columns(5)
        with om1:
            st.metric("🧑‍💼 Vendas", "23 / 30")
        with om2:
            st.metric("👥 Leads", "84 / 100")
        with om3:
            st.metric("📞 Atividades", "165 / 200")
        with om4:
            st.metric("📄 Propostas", "42 / 50")
        with om5:
            st.metric("🤝 Reuniões", "35 / 40")

    with col_m_dir:
        # 🏆 7. Ranking Comercial
        st.markdown("#### 🏆 Ranking Comercial")
        st.markdown(
            "🥇 **Ana** — 94% *(R$ 47k)*\n\n"
            "🥈 **Carlos** — 85% *(R$ 42,5k)*\n\n"
            "🥉 **Larissa** — 60% *(R$ 30k)*"
        )
        
        st.markdown("---")

        # 📝 5. & 6. Criar e Configurar Nova Meta
        st.markdown("#### ➕ Criar Nova Meta")
        
        with st.form("form_criar_meta_comercial"):
            m_tipo = st.selectbox("Tipo de Meta", ["Faturamento", "Vendas", "Leads Qualificados", "Atividades", "Propostas", "Reuniões"])
            
            m_responsavel = st.selectbox("Responsável / Equipe", ["Geral (Equipe)", "Carlos", "Ana", "Larissa"])
            
            m_periodo = st.selectbox("Período", ["Mensal", "Diário", "Semanal", "Trimestral", "Anual"])
            
            col_d_ini, col_d_fim = st.columns(2)
            with col_d_ini:
                m_dt_inicio = st.date_input("Data Inicial", value=date(2026, 8, 1))
            with col_d_fim:
                m_dt_fim = st.date_input("Data Final", value=date(2026, 8, 31))
                
            m_valor = st.number_input("Valor / Meta Numérica", min_value=0.0, value=50000.0, step=1000.0)
            
            m_descricao = st.text_area("Descrição da Meta", value="Meta comercial de agosto")

            btn_salvar_meta = st.form_submit_button("💾 Salvar Meta")
            if btn_salvar_meta:
                if m_valor > 0:
                    st.success("Nova meta cadastrada e vinculada com sucesso!")
                    st.rerun()
                else:
                    st.error("O valor da meta deve ser maior que zero.")

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
