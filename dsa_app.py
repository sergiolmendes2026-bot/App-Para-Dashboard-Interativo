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
from email.message import EmailMessage
import plotly.express as px
import plotly.graph_objects as go

def atualizar_banco():
    conn = sqlite3.connect("crm_pro.db")
    # Este comando cria a tabela se não existir
    conn.execute("""
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
            ultimo_contato TEXT,
            valor REAL,
            produto TEXT,
            temperatura TEXT,
            score INTEGER,
            proxima_acao TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Tabela verificada/atualizada com sucesso!")

atualizar_banco()

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
    """
    <style>
        /* Fundo com gradiente rico e um brilho difuso (Ambient Glow) */
        .stApp { 
            background: radial-gradient(circle at 15% 15%, #1e293b 0%, #0f172a 45%, #07090e 100%) !important;
        }

        /* Sidebar com transparência suave para absorver o brilho do fundo */
        [data-testid="stSidebar"] { 
            background: rgba(15, 23, 42, 0.45) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }

        /* O Cartão do Menu com profundidade e brilho nas bordas */
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div:first-child {
            background: rgba(30, 41, 59, 0.75) !important;
            border-radius: 20px !important;
            padding: 18px !important;
            margin: 15px 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 
                        0 0 30px rgba(59, 130, 246, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        }

        /* Estilo padrão dos itens do menu */
        .nav-link {
            color: #94a3b8 !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }

        /* Efeito Brilhante ao passar o mouse */
        .nav-link:hover {
            background: rgba(59, 130, 246, 0.18) !important;
            color: #ffffff !important;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3) !important;
            transform: translateX(4px);
        }

        /* Item selecionado com destaque luminoso */
        .nav-link-selected {
            background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%) !important;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5), 0 0 20px rgba(59, 130, 246, 0.4) !important;
            border-radius: 10px !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True
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
    try:
        # Substitua pelas suas configurações reais
        servidor_smtp = "smtp.gmail.com"
        porta = 587
        remetente = "sergiolmendes2026@gmail.com"
        senha = "xkhrditqfoapjtr"

        msg = EmailMessage()
        msg['Subject'] = "Proposta Comercial em Anexo"
        msg['From'] = remetente
        msg['To'] = email_destino
        msg.set_content("Olá, segue em anexo a proposta solicitada.")

        # Anexando o arquivo
        msg.add_attachment(
            arquivo_bytes,
            maintype='application',
            subtype='pdf',
            filename=nome_arquivo
        )

        # Conexão e envio
        with smtplib.SMTP(servidor_smtp, porta) as smtp:
            smtp.starttls()
            smtp.login(remetente, senha)
            smtp.send_message(msg)
            
        return True
    except Exception as e:
        print(f"Erro detalhado no envio do e-mail: {e}")
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
    st.markdown("👤 **Usuário:** Sergio Luiz")
    st.markdown("🟢 **Status:** Online")

# Carregamento de Dados Globais
conn = conectar()
df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
conn.close()

# Roteamento das Telas
# Certifique-se de que o bloco de navegação começa com um 'if' na primeira aba
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard Executivo & Indicadores de Desempenho")
    
    # 🌟 KPIs Principais no Topo
    dk1, dk2, dk3, dk4 = st.columns(4)
    with dk1:
        st.metric("👥 Total Leads", "128", "+12%")
    with dk2:
        st.metric("💰 Faturamento Total", "R$ 125.500", "+15%")
    with dk3:
        st.metric("🎯 Negócios Fechados", "23", "+4")
    with dk4:
        st.metric("📈 Ticket Médio", "R$ 5.456", "+3.5%")

    st.markdown("---")

    # Linha 1: Produção de Vendas (Combo Chart) & Leads por Origem (Donut)
    col_d_1, col_d_2 = st.columns(2)
    
    with col_d_1:
        st.markdown("#### 📈 1. Produção de Vendas (vs. Meta)")
        df_ev_meta = pd.DataFrame({
            'Mes': ['Abr', 'Mai', 'Jun', 'Jul', 'Ago'],
            'Realizado': [20000, 48000, 72000, 95000, 125500],
            'Meta': [25000, 50000, 75000, 100000, 150000]
        })
        
        # Lista de cores diferentes para cada uma das 5 barras
        cores_barras = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        
        fig_vendas = go.Figure()
        fig_vendas.add_trace(go.Bar(
            x=df_ev_meta['Mes'], 
            y=df_ev_meta['Realizado'], 
            name='Realizado', 
            marker_color=cores_barras
        ))
        fig_vendas.add_trace(go.Scatter(
            x=df_ev_meta['Mes'], 
            y=df_ev_meta['Meta'], 
            name='Meta', 
            mode='lines+markers', 
            line=dict(color='#ef4444', width=3)
        ))
        fig_vendas.update_layout(template='plotly_dark', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_vendas, use_container_width=True)

    with col_d_2:
        st.markdown("#### 🎯 2. Leads por Origem")
        df_origem = pd.DataFrame({
            'Origem': ["Google Ads", "Instagram", "WhatsApp", "Site", "Indicação", "LinkedIn"],
            'Leads': [45, 30, 20, 15, 10, 8]
        })
        fig_origem = px.pie(df_origem, values='Leads', names='Origem', hole=0.4, template='plotly_dark')
        fig_origem.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_origem, use_container_width=True)

    st.markdown("---")

    # Linha 2: Pipeline por Etapa (Funil) & Vendas por Consultor (Colunas Agrupadas)
    col_d_3, col_d_4 = st.columns(2)

    with col_d_3:
        st.markdown("#### 🔄 3. Pipeline por Etapa (Valor)")
        df_pipe = pd.DataFrame({
            'Etapa': ["Novo Lead", "Qualificação", "Proposta", "Negociação", "Fechamento"],
            'Valor': [80000, 60000, 42000, 30000, 20000]
        })
        fig_funil = go.Figure(go.Funnel(y=df_pipe['Etapa'], x=df_pipe['Valor'], textinfo="value+percent initial"))
        fig_funil.update_layout(template='plotly_dark', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_funil, use_container_width=True)

    with col_d_4:
        st.markdown("#### 👥 4. Vendas por Consultor (vs. Meta)")
        df_cons = pd.DataFrame({
            'Consultor': ["Ana", "Carlos", "Larissa"],
            'Realizado': [47000, 42500, 36000],
            'Meta': [50000, 50000, 50000]
        })
        fig_cons = go.Figure()
        fig_cons.add_trace(go.Bar(x=df_cons['Consultor'], y=df_cons['Realizado'], name='Realizado', marker_color='#10b981'))
        fig_cons.add_trace(go.Bar(x=df_cons['Consultor'], y=df_cons['Meta'], name='Meta', marker_color='#64748b'))
        fig_cons.update_layout(barmode='group', template='plotly_dark', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_cons, use_container_width=True)

    st.markdown("---")

    # Linha 3: Funil de Conversão Comercial & Status dos Pagamentos
    col_d_5, col_d_6 = st.columns(2)

    with col_d_5:
        st.markdown("#### 🎯 5. Funil de Conversão Geral")
        df_funil_geral = pd.DataFrame({
            'Fase': ['Leads Totais', 'Qualificados', 'Oportunidades', 'Propostas', 'Fechados'],
            'Quantidade': [128, 82, 47, 31, 23]
        })
        fig_fgeral = go.Figure(go.Funnel(y=df_funil_geral['Fase'], x=df_funil_geral['Quantidade']))
        fig_fgeral.update_layout(template='plotly_dark', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_fgeral, use_container_width=True)

    with col_d_6:
        st.markdown("#### 💳 6. Status dos Pagamentos")
        df_pag = pd.DataFrame({
            'Status': ["🟢 Pago", "🟡 Parcial", "🟠 Pendente", "🔴 Em atraso"],
            'Volume': [85000, 25500, 10000, 5000]
        })
        fig_pag = px.pie(df_pag, values='Volume', names='Status', hole=0.6, template='plotly_dark')
        fig_pag.update_traces(marker=dict(colors=['#10b981', '#f59e0b', '#f97316', '#ef4444']))
        fig_pag.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_pag, use_container_width=True)

    st.markdown("---")

    # Linha 4: Vendas por Produto & Atividades Comerciais
    col_d_7, col_d_8 = st.columns(2)

    with col_d_7:
        st.markdown("#### 📦 7. Vendas por Produto / Serviço")
        df_prod = pd.DataFrame({
            'Produto': ["Software A", "Software B", "Enterprise", "Consultoria"],
            'Faturamento': [45000, 32000, 28000, 20500]
        })
        # Adicionado o parâmetro color='Produto' para gerar cores distintas por barra
        fig_prod = px.bar(
            df_prod, 
            x='Faturamento', 
            y='Produto', 
            orientation='h', 
            color='Produto', 
            template='plotly_dark'
        )
        fig_prod.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), 
            height=300, 
            yaxis={'categoryorder':'total ascending'},
            showlegend=False  # Oculta a legenda lateral se preferir o visual mais limpo
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_d_8:
        st.markdown("#### 📋 8. Atividades Comerciais (Concluídas x Pendentes)")
        df_ativ = pd.DataFrame({
            'Tipo': ["Ligações", "E-mails", "WhatsApp", "Reuniões", "Propostas"],
            'Concluídas': [40, 30, 25, 20, 15],
            'Pendentes': [10, 8, 5, 12, 4]
        })
        fig_ativ = go.Figure()
        fig_ativ.add_trace(go.Bar(x=df_ativ['Tipo'], y=df_ativ['Concluídas'], name='Concluídas', marker_color='#10b981'))
        fig_ativ.add_trace(go.Bar(x=df_ativ['Tipo'], y=df_ativ['Pendentes'], name='Pendentes', marker_color='#f59e0b'))
        fig_ativ.update_layout(barmode='stack', template='plotly_dark', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_ativ, use_container_width=True)

elif selected == "Leads":
    st.markdown("### 👥 Gestão Avançada de Leads e Clientes")
    
    col_l1, col_l2 = st.columns([3, 1])
    with col_l1:
        pesquisa_lead = st.text_input("🔍 Pesquisar Lead por Nome, Empresa ou E-mail", "", key="input_pesquisa_leads_geral")
    with col_l2:
        if st.button("➕ Novo Lead Completo", use_container_width=True):
            st.session_state.modal_novo_lead = True

    # Modal / Seção de Cadastro de Novo Lead Completo
    if st.session_state.get("modal_novo_lead", False):
        st.markdown("---")
        st.markdown("#### 📝 Cadastro e Qualificação de Novo Lead")
        
        with st.form("form_novo_lead_completo"):
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
                    try:
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
                        st.success("Lead cadastrado com sucesso!")
                        st.session_state.modal_novo_lead = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao inserir no banco de dados: {e}")
                    finally:
                        conn.close()
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
            ], key="filtro_status_unique_clean")
            
        with fa2:
            filtro_temp = st.selectbox("Filtrar por Temperatura", ["Todas", "🔥 Quente", "⛅ Morno", "❄️ Frio"], key="filtro_temp_unique_clean")
            
        with fa3:
            filtro_prioridade = st.selectbox("Filtrar por Prioridade", ["Todas", "🔴 Alta", "🟡 Média", "🟢 Baixa"], key="filtro_prioridade_unique_clean")
            
        with fa4:
            filtro_resp = st.selectbox("Filtrar por Responsável", ["Todos", "Carlos", "Ana", "Larissa"], key="filtro_resp_unique_clean")

    # Garante que temos um DataFrame para exibir (se 'df_clientes' não existir ou estiver vazia, cria dados de exemplo para o layout não sumir)
    if 'df_clientes' not in locals() or df_clientes is None or df_clientes.empty:
        # Tenta carregar do banco se a função existir
        try:
            conn = conectar()
            df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
            conn.close()
        except Exception:
            df_clientes = pd.DataFrame(columns=['id', 'nome', 'empresa', 'email', 'status', 'temperatura', 'prioridade', 'valor', 'responsavel', 'proxima_acao'])

    # Se ainda estiver vazio (nenhum dado cadastrado), injetamos um registro de exemplo para você testar os botões visualmente
    if df_clientes.empty:
        df_clientes = pd.DataFrame([{
            'id': 1,
            'nome': 'João Silva (Exemplo)',
            'empresa': 'Empresa ABC',
            'email': 'joao@abc.com',
            'status': '🆕 Novo Lead',
            'temperatura': '🔥 Quente',
            'prioridade': '🔴 Alta',
            'valor': 15000.0,
            'responsavel': 'Carlos',
            'proxima_acao': 'Ligar às 14h'
        }])

    # Lógica de Filtragem
    df_filtrado = df_clientes.copy()
    
    if pesquisa_lead:
        df_filtrado = df_filtrado[
            df_filtrado['nome'].astype(str).str.contains(pesquisa_lead, case=False, na=False) |
            df_filtrado['empresa'].astype(str).str.contains(pesquisa_lead, case=False, na=False) |
            df_filtrado['email'].astype(str).str.contains(pesquisa_lead, case=False, na=False)
        ]
        
    if filtro_status != "Todos":
        df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
    if filtro_temp != "Todas":
        df_filtrado = df_filtrado[df_filtrado['temperatura'] == filtro_temp]
    if filtro_prioridade != "Todas":
        df_filtrado = df_filtrado[df_filtrado['prioridade'] == filtro_prioridade]
    if filtro_resp != "Todos":
        df_filtrado = df_filtrado[df_filtrado['responsavel'] == filtro_resp]

    # Renderização da Tabela com Botões de Ação por Linha
    if not df_filtrado.empty:
        st.markdown("---")
        h_cols = st.columns([0.6, 1.5, 1.5, 1.2, 1, 1, 1.2, 1.2])
        headers = ["ID", "Nome", "Empresa", "Status", "Temp.", "Valor", "Resp.", "Ações"]
        for i, h in enumerate(headers):
            h_cols[i].markdown(f"**{h}**")
        
        st.divider()

        for index, row in df_filtrado.iterrows():
            r_cols = st.columns([0.6, 1.5, 1.5, 1.2, 1, 1, 1.2, 1.2])
            r_cols[0].write(str(row.get('id', '')))
            r_cols[1].write(str(row.get('nome', '')))
            r_cols[2].write(str(row.get('empresa', '')))
            r_cols[3].write(str(row.get('status', '')))
            r_cols[4].write(str(row.get('temperatura', '')))
            
            val_raw = row.get('valor', 0)
            val_fmt = f"R$ {val_raw:,.2f}" if pd.notnull(val_raw) else "R$ 0,00"
            r_cols[5].write(val_fmt)
            
            r_cols[6].write(str(row.get('responsavel', '')))
            
            # Ações Rápidas (Ver Detalhes 👁️, Editar ✏️, Excluir 🗑️)
            act_cols = r_cols[7].columns(3)
            
            if act_cols[0].button("👁️", key=f"ver_{row.get('id', index)}_{index}", help="Ver Detalhes do Lead"):
                st.info(f"Visualizando painel de detalhes de: {row.get('nome', '')}")
            
            if act_cols[1].button("✏️", key=f"edit_{row.get('id', index)}_{index}", help="Editar Lead"):
                st.toast(f"Abrindo edição para: {row.get('nome', '')}")
            
            if act_cols[2].button("🗑️", key=f"del_{row.get('id', index)}_{index}", help="Excluir Lead"):
                lead_id = row.get('id')
                if lead_id:
                    conn = conectar()
                    try:
                        conn.execute("DELETE FROM clientes WHERE id = ?", (lead_id,))
                        conn.commit()
                        st.success(f"Lead excluído com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir no banco de dados: {e}")
                    finally:
                        conn.close()
                else:
                    st.warning("ID do lead inválido para exclusão.")
    else:
        st.warning("Nenhum lead encontrado com os filtros selecionados.")

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
    
    # Métricas do topo baseadas no banco de dados (com fallback seguro)
    try:
        conn = conectar()
        df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
        conn.close()
    except Exception:
        df_vendas = pd.DataFrame(columns=['id', 'cliente', 'produto', 'valor', 'responsavel', 'status', 'data'])

    # Se estiver vazio, cria dados de exemplo para o painel não ficar zerado
    if df_vendas.empty:
        df_vendas = pd.DataFrame([
            {'id': 1, 'cliente': 'Tech Soluções Ltda', 'produto': 'Software A (CRM Pro)', 'valor': 24500.0, 'responsavel': 'Carlos', 'status': 'Fechada', 'data': '2026-08-16'},
            {'id': 2, 'cliente': 'Alpha Ltda', 'produto': 'Consultoria QI', 'valor': 12000.0, 'responsavel': 'Ana', 'status': 'Em Negociação', 'data': '2026-08-14'},
            {'id': 3, 'cliente': 'Global Ltda', 'produto': 'Software B', 'valor': 45000.0, 'responsavel': 'Carlos', 'status': 'Fechada', 'data': '2026-08-10'}
        ])

    total_vendido = df_vendas[df_vendas['status'] == 'Fechada']['valor'].sum()
    qtd_vendas = len(df_vendas[df_vendas['status'] == 'Fechada'])
    ticket_medio = total_vendido / qtd_vendas if qtd_vendas > 0 else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Vendido", f"R$ {total_vendido:,.2f}")
    m2.metric("Vendas Fechadas", str(qtd_vendas))
    m3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    m4.metric("Em Negociação", f"R$ {df_vendas[df_vendas['status'] == 'Em Negociação']['valor'].sum():,.2f}")
    m5.metric("Taxa Perda", "18%")

    st.markdown("---")

    # Layout em duas colunas: Esquerda (Histórico + Pesquisa funcional), Direita (Formulário de Nova Venda)
    col_v_esq, col_v_dir = st.columns([2.2, 1.2])

    with col_v_esq:
        st.markdown("#### 📋 Histórico e Pipeline de Vendas")
        
        # Barra de pesquisa funcional ligada ao DataFrame
        pesquisa_venda = st.text_input("🔍 Pesquisar venda por cliente, empresa ou produto...", "", key="input_pesq_vendas_funcional")
        
        # Filtros rápidos
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            filtro_status_venda = st.selectbox("Status da Venda", ["Todos", "Fechada", "Em Negociação", "Perdida"], key="f_venda_status")
        with f_col2:
            filtro_resp_venda = st.selectbox("Responsável", ["Todos"] + list(df_vendas['responsavel'].unique()), key="f_venda_resp")

        # Aplicação real dos filtros e da barra de pesquisa
        df_v_filtrado = df_vendas.copy()
        
        if pesquisa_venda:
            df_v_filtrado = df_v_filtrado[
                df_v_filtrado['cliente'].astype(str).str.contains(pesquisa_venda, case=False, na=False) |
                df_v_filtrado['produto'].astype(str).str.contains(pesquisa_venda, case=False, na=False)
            ]
        if filtro_status_venda != "Todos":
            df_v_filtrado = df_v_filtrado[df_v_filtrado['status'] == filtro_status_venda]
        if filtro_resp_venda != "Todos":
            df_v_filtrado = df_v_filtrado[df_v_filtrado['responsavel'] == filtro_resp_venda]

        # Tabela de Vendas Filtrada
        if not df_v_filtrado.empty:
            st.dataframe(
                df_v_filtrado[['id', 'cliente', 'produto', 'valor', 'responsavel', 'status', 'data']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Nenhuma venda encontrada com os critérios informados.")

    with col_v_dir:
        st.markdown("#### ➕ Registrar Nova Venda")
        
        with st.form("form_registrar_venda_direta"):
            v_cliente = st.text_input("Lead / Cliente (Empresa) *")
            v_produto = st.selectbox("Produto / Serviço", ["Software A", "Software B", "Consultoria QI", "Sistema CRM Pro"])
            
            vc1, vc2 = st.columns(2)
            with vc1:
                v_valor = st.number_input("Valor Total (R$)", min_value=0.0, value=15000.0, step=1000.0)
            with vc2:
                v_desconto = st.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=100.0)
                
            v_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Boleto", "Cartão de Crédito", "Transferência"])
            v_responsavel = st.selectbox("Responsável da Venda", ["Carlos", "Ana", "Larissa"])
            v_data = st.text_input("Data de Fechamento", value=str(date.today()))
            v_status = st.selectbox("Status da Oportunidade", ["Fechada (Venda Concluída)", "Em Negociação", "Perdida"])
            v_obs = st.text_area("Observações do Contrato / Fechamento")

            btn_salvar_venda = st.form_submit_button("💾 Salvar Venda no CRM")
            
            if btn_salvar_venda:
                if v_cliente:
                    conn = conectar()
                    try:
                        # Garante a criação da tabela caso não exista
                        conn.execute("""
                            CREATE TABLE IF NOT EXISTS vendas (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                cliente TEXT,
                                produto TEXT,
                                valor REAL,
                                responsavel TEXT,
                                status TEXT,
                                data TEXT
                            )
                        """)
                        conn.execute("""
                            INSERT INTO vendas (cliente, produto, valor, responsavel, status, data)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (v_cliente, v_produto, v_valor - v_desconto, v_responsavel, 'Fechada' if 'Fechada' in v_status else v_status, v_data))
                        conn.commit()
                        st.success("Venda registrada e integrada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar venda: {e}")
                    finally:
                        conn.close()
                else:
                    st.error("O campo Cliente é obrigatório.")

elif selected == "Propostas":
    st.markdown("### 📄 Gestão de Propostas Comerciais")
    
    # Métricas rápidas no topo
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Propostas", "24", "+3 este mês")
    m2.metric("Valor Total", "R$ 185.000", "+12%")
    m3.metric("Aprovadas", "12", "50% conv.")
    m4.metric("Em Negociação", "8", "Ativas")

    st.markdown("---")

    # Botão para abrir o formulário de Nova Proposta
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        pesquisa_prop = st.text_input("🔍 Pesquisar Proposta por ID ou Cliente", "", key="pesquisa_propostas_geral")
    with col_p2:
        if st.button("➕ Nova Proposta", use_container_width=True):
            st.session_state.modal_nova_proposta = True

    # ---------------------------------------------------------
    # MODAL / FORMULÁRIO DE NOVA PROPOSTA
    # ---------------------------------------------------------
    if st.session_state.get("modal_nova_proposta", False):
        st.markdown("---")
        st.markdown("#### 📝 Cadastro de Nova Proposta Comercial")
        
        with st.form("form_nova_proposta_completo"):
            
            # Seção 1: Cliente
            st.markdown("##### 👤 1. Informações do Cliente")
            c1, c2, c3 = st.columns(3)
            with c1:
                p_cliente = st.text_input("Nome do Cliente *")
                p_empresa = st.text_input("Empresa")
            with c2:
                p_doc = st.text_input("CNPJ / CPF")
                p_email = st.text_input("E-mail")
            with c3:
                p_telefone = st.text_input("Telefone")
                p_endereco = st.text_input("Endereço")

            st.markdown("---")
            # Seção 2: Dados Comerciais
            st.markdown("##### 💼 2. Dados Comerciais da Proposta")
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                p_num = st.text_input("Nº da Proposta", value="PROP-2026-002")
                p_produto = st.text_input("Produto / Serviço")
            with d2:
                p_qtd = st.number_input("Quantidade", min_value=1, value=1)
                p_valor_unit = st.number_input("Valor Unitário (R$)", min_value=0.0, value=5000.0, step=500.0)
            with d3:
                p_desconto = st.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=100.0)
                p_impostos = st.number_input("Impostos (R$)", min_value=0.0, value=0.0, step=100.0)
            with d4:
                # Cálculo automático do subtotal
                p_subtotal = (p_qtd * p_valor_unit) - p_desconto + p_impostos
                st.markdown(f"**Valor Total Estimado:**")
                st.markdown(f"### R$ {p_subtotal:,.2f}")

            p_descricao = st.text_area("Descrição Detalhada do Escopo")

            st.markdown("---")
            # Seção 3: Condições de Pagamento
            st.markdown("##### 💳 3. Condições de Pagamento")
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_forma_pgto = st.selectbox("Forma de Pagamento", [
                    "Pix", "Boleto", "Cartão de crédito", "Cartão de débito", 
                    "À vista", "Parcelado", "Transferência bancária", "Condição personalizada"
                ])
            with cp2:
                p_parcelas = st.selectbox("Número de Parcelas", ["1x", "2x", "3x", "6x", "12x"])
            with cp3:
                p_vencimento = st.text_input("Vencimento / Prazo", value="30 dias")

            st.markdown("---")
            # Seção 4: Controle e Status
            st.markdown("##### 📅 4. Controle e Status da Proposta")
            cs1, cs2, cs3, cs4 = st.columns(4)
            with cs1:
                p_status = st.selectbox("Status da Proposta", [
                    "📝 Rascunho", "📤 Enviada", "👀 Visualizada", 
                    "💬 Em negociação", "✅ Aprovada", "❌ Recusada", 
                    "⏰ Expirada", "🚫 Cancelada"
                ])
            with cs2:
                p_responsavel = st.selectbox("Responsável", ["Carlos", "Ana", "Larissa"])
            with cs3:
                p_validade = st.text_input("Data de Validade", value="2026-09-30")
            with cs4:
                p_prob = st.slider("Probabilidade de Fechamento (%)", 0, 100, 75)

            p_obs = st.text_area("Observações / Termos e Condições")

            btn_salvar_prop = st.form_submit_button("💾 Salvar Nova Proposta")
            if btn_salvar_prop:
                if p_cliente:
                    st.success("Proposta cadastrada com sucesso!")
                    st.session_state.modal_nova_proposta = False
                    st.rerun()
                else:
                    st.error("O campo Nome do Cliente é obrigatório.")

        if st.button("❌ Fechar Formulário"):
            st.session_state.modal_nova_proposta = False
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Lista Completa de Propostas")

    # DataFrame de Exemplo para Propostas
    df_propostas = pd.DataFrame([
        {
            'id': 'PROP-2026-001',
            'cliente': 'Empresa Exemplo S/A',
            'produto': 'Consultoria / Software',
            'valor': 25000.0,
            'status': '💬 Em negociação',
            'responsavel': 'Carlos',
            'validade': '30/09/2026'
        },
        {
            'id': 'PROP-2026-002',
            'cliente': 'Tech Soluções Ltda',
            'produto': 'Sistema CRM Pro',
            'valor': 12500.0,
            'status': '✅ Aprovada',
            'responsavel': 'Ana',
            'validade': '15/10/2026'
        }
    ])

    # Filtragem por pesquisa
    if pesquisa_prop:
        df_propostas = df_propostas[
            df_propostas['id'].astype(str).str.contains(pesquisa_prop, case=False, na=False) |
            df_propostas['cliente'].astype(str).str.contains(pesquisa_prop, case=False, na=False)
        ]

    # Renderização da Tabela Personalizada com Ações Rápidas (👁️ ✏️ 📄 🗑️)
    if not df_propostas.empty:
        h_cols = st.columns([1.2, 2.0, 1.8, 1.2, 1.5, 1.0, 1.0, 1.5])
        headers = ["Nº Proposta", "Cliente", "Produto", "Valor", "Status", "Resp.", "Validade", "Ações"]
        for i, h in enumerate(headers):
            h_cols[i].markdown(f"**{h}**")
        
        st.divider()

        for index, row in df_propostas.iterrows():
            r_cols = st.columns([1.2, 2.0, 1.8, 1.2, 1.5, 1.0, 1.0, 1.5])
            
            r_cols[0].write(str(row.get('id', '')))
            r_cols[1].write(str(row.get('cliente', '')))
            r_cols[2].write(str(row.get('produto', '')))
            
            val = row.get('valor', 0)
            r_cols[3].write(f"R$ {val:,.2f}" if pd.notnull(val) else "R$ 0,00")
            
            r_cols[4].write(str(row.get('status', '')))
            r_cols[5].write(str(row.get('responsavel', '')))
            r_cols[6].write(str(row.get('validade', '')))
            
            # Mini-colunas para os 4 botões de Ações Rápidas: Ver, Editar, PDF, Excluir
            act_cols = r_cols[7].columns(4)
            
            if act_cols[0].button("👁️", key=f"p_ver_{index}", help="Ver Detalhes"):
                st.info(f"Visualizando detalhes da proposta: {row['id']}")
                
            if act_cols[1].button("✏️", key=f"p_edit_{index}", help="Editar Proposta"):
                st.toast(f"Editando proposta: {row['id']}")
                
            if act_cols[2].button("📄", key=f"p_pdf_{index}", help="Gerar PDF Profissional"):
                st.success(f"PDF da proposta {row['id']} gerado com sucesso!")
                
            if act_cols[3].button("🗑️", key=f"p_del_{index}", help="Excluir Proposta"):
                st.warning(f"Proposta {row['id']} excluída!")
                st.rerun()
                
        # Integração Inteligente: Conversão para Venda se Aprovada
        st.markdown("---")
        st.info("💡 **Dica do CRM:** Quando uma proposta for marcada como **✅ Aprovada**, o sistema oferece automaticamente a conversão direta para o módulo de Vendas e Pagamentos.")
    else:
        st.warning("Nenhuma proposta encontrada.")

elif selected == "Relatórios":
    st.markdown("### 📊 Relatórios Executivos & Central de Exportação")
    
    # 📊 1. KPIs de Resumo no Topo
    rk1, rk2, rk3, rk4 = st.columns(4)
    with rk1:
        st.metric("👥 Leads", "128")
    with rk2:
        st.metric("💰 Vendas", "23")
    with rk3:
        st.metric("💵 Faturamento", "R$ 125.500")
    with rk4:
        st.metric("📈 Conversão", "18%")

    st.markdown("---")

    # 📑 2. Configurar Relatório & Filtros Avançados
    st.markdown("#### 📑 Configurar Relatório")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        tipo_relatorio = st.selectbox(
            "Tipo de Relatório", 
            [
                "📊 Vendas Consolidadas", 
                "👥 Relatório de Leads", 
                "🎯 Conversão de Leads", 
                "💰 Faturamento", 
                "📈 Performance Comercial", 
                "🏆 Performance por Vendedor", 
                "📦 Vendas por Produto", 
                "💳 Relatório de Pagamentos", 
                "📋 Pipeline Comercial", 
                "📅 Atividades e Compromissos", 
                "📄 Propostas", 
                "📣 Campanhas"
            ]
        )
        
        from datetime import date
        rc_dt1, rc_dt2 = st.columns(2)
        with rc_dt1:
            r_ini = st.date_input("Data Inicial", value=date(2026, 8, 1))
        with rc_dt2:
            r_fim = st.date_input("Data Final", value=date(2026, 8, 31))

        r_resp = st.selectbox("Responsável", ["Todos", "Carlos", "Ana", "Larissa"])

    with r_col2:
        r_prod = st.selectbox("Produto / Serviço", ["Todos", "Software A", "Software B", "Enterprise", "Consultoria"])
        r_status = st.selectbox("Status", ["Todos", "Pago", "Pendente", "Em Atraso", "Cancelado"])
        r_origem = st.selectbox("Origem do Lead", ["Todos", "Google Ads", "Instagram", "WhatsApp", "Site"])
        r_pipeline = st.selectbox("Pipeline / Etapa", ["Todas", "Novo Lead", "Qualificação", "Proposta", "Negociação", "Fechamento"])

    st.markdown("---")

    # 👁️ 3. Pré-visualização e Resumo antes da Exportação
    st.markdown("#### 👁️ Pré-visualização dos Dados")
    import pandas as pd
    df_preview = pd.DataFrame([
        {"Cliente": "João Silva", "Produto": "Software A", "Valor": "R$ 5.000", "Responsável": "Carlos", "Status": "Pago"},
        {"Cliente": "Alpha Tech", "Produto": "Software B", "Valor": "R$ 8.500", "Responsável": "Ana", "Status": "Pendente"},
        {"Cliente": "Global Ltda", "Produto": "Enterprise", "Valor": "R$ 12.000", "Responsável": "Carlos", "Status": "Pago"}
    ])
    st.dataframe(df_preview, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 📊 Resumo Executivo Rápido
    st.markdown("#### 📊 Resumo do Relatório Selecionado")
    rs1, rs2, rs3, rs4, rs5, rs6 = st.columns(6)
    with rs1:
        st.metric("Leads", "128")
    with rs2:
        st.metric("Oportunidades", "47")
    with rs3:
        st.metric("Vendas", "23")
    with rs4:
        st.metric("Faturamento", "R$ 125.5k")
    with rs5:
        st.metric("Ticket Médio", "R$ 5.456")
    with rs6:
        st.metric("Conversão", "18%")

    st.markdown("---")

    # 📤 5. Opções de Exportação
    st.markdown("#### 📤 Opções de Exportação")
    
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        formato_export = st.radio("Formato do Arquivo", ["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"], horizontal=True)
    with ex_col2:
        st.markdown("**Opções Adicionais:**")
        chk_resumo = st.checkbox("Incluir resumo executivo", value=True)
        chk_graficos = st.checkbox("Incluir gráficos", value=True)
        chk_filtros = st.checkbox("Incluir filtros aplicados", value=True)

    # Botões de Ação Separados
    ac_ex1, ac_ex2, ac_ex3 = st.columns(3)
    with ac_ex1:
        if st.button("👁️ Visualizar Relatório Completo"):
            st.success("Visualização gerada com sucesso!")
    with ac_ex2:
        if st.button("📥 Exportar Arquivo"):
            st.success(f"Relatório exportado em {formato_export} com sucesso!")
    with ac_ex3:
        if st.button("📧 Enviar por E-mail"):
            st.success("Relatório disparado para os e-mails cadastrados!")

    st.markdown("---")

    # 🕒 6. Histórico de Exportações
    st.markdown("#### 🕒 Histórico de Exportações Recentes")
    df_historico_exp = pd.DataFrame([
        {"Data": "15/08/2026 14:30", "Relatório": "Vendas Consolidadas", "Período": "Agosto", "Formato": "Excel (.xlsx)", "Usuário": "Carlos", "Ações": "📥"},
        {"Data": "15/08/2026 13:10", "Relatório": "Relatório de Leads", "Período": "Agosto", "Formato": "PDF (.pdf)", "Usuário": "Ana", "Ações": "📥"}
    ])
    st.dataframe(df_historico_exp, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Reutilizar Filtros da Última Exportação"):
        st.info("Filtros aplicados com base no histórico selecionado.")   
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
    import plotly.graph_objects as go

    # Dados de exemplo para o gráfico de evolução temporal
    dias_mes = [f"Dia {i*5}" for i in range(1, 7)]
    df_evolucao = pd.DataFrame({
        "Meta Acumulada": [25000, 50000, 75000, 100000, 125000, 150000],
        "Realizado Acumulado": [20000, 48000, 72000, 95000, 108000, 108000]
    }, index=dias_mes)

    # Criando a figura com Plotly para suportar gradiente e estilo SaaS
    fig = go.Figure()

    # Adicionando a linha/área de "Realizado Acumulado" com Gradiente Azul
    fig.add_trace(go.Scatter(
        x=df_evolucao.index,
        y=df_evolucao["Realizado Acumulado"],
        name="Realizado Acumulado",
        mode='lines+markers',
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)', # Gradiente translúcido
        line=dict(color='#3b82f6', width=3, shape='spline') # Linha curva e moderna
    ))

    # Adicionando a linha/área de "Meta Acumulada" com Gradiente Roxo (Tracejada)
    fig.add_trace(go.Scatter(
        x=df_evolucao.index,
        y=df_evolucao["Meta Acumulada"],
        name="Meta Acumulada",
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(168, 85, 247, 0.1)',
        line=dict(color='#a855f7', width=2, dash='dash', shape='spline')
    ))

    # Estilizando o layout para combinar com o Dark Mode do CRM
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c9d1d9'),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickprefix='R$ ')
    )

    # Exibindo no Streamlit sem fundo branco e com largura total adaptável
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

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
    st.markdown("### 👥 Gestão de Usuários e Equipe")
    st.markdown("Gerencie usuários, acessos, perfis e permissões do CRM.")
    
    # 📊 1. Cards no Topo (4 KPIs)
    uk1, uk2, uk3, uk4 = st.columns(4)
    with uk1:
        st.metric("👥 Usuários", "12")
    with uk2:
        st.metric("🟢 Ativos", "10")
    with uk3:
        st.metric("🔴 Inativos", "2")
    with uk4:
        st.metric("🛡️ Admins", "1")

    st.markdown("---")

    # 🔎 Filtros e Botão Novo Usuário
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        pesquisa_usuario = st.text_input("🔎 Pesquisar usuário...", "")
    with f_col2:
        filtro_perfil = st.selectbox("Perfil", ["Todos os perfis", "Administrador", "Gerente", "Comercial Sênior", "Comercial Júnior", "Suporte"])
    with f_col3:
        filtro_status = st.selectbox("Status", ["Todos os status", "🟢 Ativo", "🟡 Ausente", "🔴 Bloqueado", "⚫ Offline"])

    # Botão para expandir formulário de Novo Usuário
    with st.expander("➕ Adicionar Novo Usuário"):
        with st.form("form_novo_usuario"):
            st.markdown("##### Dados Pessoais e Acesso")
            nu1, nu2 = st.columns(2)
            with nu1:
                u_nome = st.text_input("Nome Completo")
                u_email = st.text_input("E-mail")
                u_cargo = st.selectbox("Cargo", ["Administrador", "Gerente", "Comercial Sênior", "Comercial Júnior", "Suporte"])
            with nu2:
                u_telefone = st.text_input("Telefone")
                u_login = st.text_input("Usuário / Login")
                u_senha = st.text_input("Senha Temporária", type="password")

            nu3, nu4 = st.columns(2)
            with nu3:
                u_perfil = st.selectbox("Perfil de Acesso", ["Administrador", "Gerente", "Comercial Sênior", "Comercial Júnior", "Suporte"])
            with nu4:
                u_status_inicial = st.selectbox("Status Inicial", ["🟢 Ativo", "🟡 Ausente", "🔴 Bloqueado"])

            st.markdown("##### 🔐 Matriz de Permissões Rápidas")
            import pandas as pd
            df_perm_modelo = pd.DataFrame([
                {"Módulo": "Leads", "Visualizar": True, "Criar": True, "Editar": True, "Excluir": False},
                {"Módulo": "Vendas", "Visualizar": True, "Criar": True, "Editar": True, "Excluir": False},
                {"Módulo": "Propostas", "Visualizar": True, "Criar": True, "Editar": True, "Excluir": False},
                {"Módulo": "Metas", "Visualizar": True, "Criar": False, "Editar": False, "Excluir": False},
                {"Módulo": "Usuários", "Visualizar": False, "Criar": False, "Editar": False, "Excluir": False}
            ])
            st.data_editor(df_perm_modelo, use_container_width=True, hide_index=True)

            if st.form_submit_button("💾 Salvar Novo Usuário"):
                if u_nome and u_email:
                    st.success(f"Usuário {u_nome} cadastrado com sucesso!")
                else:
                    st.error("Preencha ao menos o Nome e E-mail.")

    st.markdown("---")

    # 📋 Tabela Principal de Usuários & Desempenho Comercial
    st.markdown("#### 📋 Equipe Cadastrada & Desempenho Comercial")
    
    df_usuarios_equipe = pd.DataFrame([
        {
            "Nome": "Carlos Mendes", 
            "Cargo": "Administrador", 
            "Leads": "32 Leads", 
            "Vendas": "R$ 48.500", 
            "Meta": "85%", 
            "Status": "🟢 Ativo", 
            "Último Acesso": "Hoje, 20:15",
            "Ações": "👁️ | ✏️ | 🔒 | 🗑️"
        },
        {
            "Nome": "Ana Souza", 
            "Cargo": "Comercial Sênior", 
            "Leads": "45 Leads", 
            "Vendas": "R$ 62.300", 
            "Meta": "94%", 
            "Status": "🟢 Ativo", 
            "Último Acesso": "Hoje, 19:40",
            "Ações": "👁️ | ✏️ | 🔒 | 🗑️"
        },
        {
            "Nome": "Larissa Lima", 
            "Cargo": "Comercial Júnior", 
            "Leads": "20 Leads", 
            "Vendas": "R$ 31.200", 
            "Meta": "60%", 
            "Status": "🟡 Ausente", 
            "Último Acesso": "Ontem, 18:20",
            "Ações": "👁️ | ✏️ | 🔒 | 🗑️"
        }
    ])

    st.dataframe(df_usuarios_equipe, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 🛡️ Detalhes de Segurança e Auditoria de Acessos
    st.markdown("#### 🛡️ Segurança & Sessões Ativas")
    ac1, ac2 = st.columns(2)
    with ac1:
        st.markdown(
            "🔒 **Ações administrativas rápidas:**\n\n"
            "• [Forçar Logout Geral para Sessões Inativas]\n\n"
            "• [Auditar Logs de Tentativas de Login Falhas]\n\n"
            "• [Exportar Relatório de Atividade da Equipe]"
        )
    with ac2:
        st.info(
            "📌 **Nota de Governança:**\n"
            "A exclusão definitiva de usuários está desativada para preservar a integridade "
            "do histórico de vendas, propostas e conversões vinculadas. Utilize a opção "
            "de **Desativar** para revogar acessos com segurança."
        )

elif selected == "Configurações":
    st.markdown("### ⚙️ Configurações Gerais do Sistema & Painel Administrativo")
    
    # 🧩 Central Administrativa com Abas (Streamlit Tabs)
    tab_geral, tab_comercial, tab_vendas, tab_agenda, tab_notif, tab_seguranca, tab_dados = st.tabs([
        "⚙️ Geral", "👥 Comercial", "💰 Vendas", "📅 Agenda", "🔔 Notificações", "🔐 Segurança", "💾 Dados"
    ])

    with tab_geral:
        st.markdown("#### ⚙️ Configurações Gerais do Sistema")
        with st.form("form_config_geral"):
            cg1, cg2 = st.columns(2)
            with cg1:
                st.text_input("Nome da Empresa", value="LMB Pro Ltda")
                st.text_input("E-mail de Suporte", value="suporte@lmbpro.com")
                st.text_input("Telefone da Empresa", value="(11) 99999-9999")
                st.text_input("Site", value="https://www.lmbpro.com")
                st.file_uploader("Logo da Empresa", type=["png", "jpg", "jpeg"])
            with cg2:
                st.selectbox("Moeda Padrão", ["BRL (R$)", "USD ($)", "EUR (€)"])
                st.selectbox("Idioma", ["Português (Brasil)", "English", "Español"])
                st.selectbox("Fuso Horário", ["America/Sao_Paulo", "America/New_York", "Europe/Lisbon"])
                st.selectbox("Formato de Data", ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"])
                st.selectbox("Primeiro Dia da Semana", ["Segunda-feira", "Domingo"])

            if st.form_submit_button("💾 Salvar Configurações Gerais"):
                st.success("Configurações gerais salvas com sucesso!")

    with tab_comercial:
        st.markdown("#### 👥 Configurações Comerciais")
        with st.form("form_config_comercial"):
            st.text_area("Pipeline Padrão (Etapas separadas por vírgula)", value="Novo Lead, Qualificação, Proposta, Negociação, Fechamento")
            st.text_area("Status de Leads", value="Novo, Contatado, Qualificado, Em negociação, Convertido, Perdido")
            st.text_area("Prioridades", value="Alta, Média, Baixa")
            st.text_area("Temperatura", value="🔥 Quente, 🟡 Morno, 🔵 Frio")
            
            if st.form_submit_button("💾 Salvar Configurações Comerciais"):
                st.success("Configurações comerciais atualizadas!")

    with tab_vendas:
        st.markdown("#### 💰 Configurações de Vendas")
        with st.form("form_config_vendas"):
            st.text_area("Formas de Pagamento", value="PIX, Cartão, Boleto, Transferência, Dinheiro")
            st.text_area("Condições de Pagamento", value="À vista, Parcelado")
            st.text_area("Status de Pagamento", value="Pago, Parcial, Pendente, Em atraso, Cancelado, Estornado")
            
            if st.form_submit_button("💾 Salvar Configurações de Vendas"):
                st.success("Configurações de vendas atualizadas!")

    with tab_agenda:
        st.markdown("#### 📅 Configurações da Agenda")
        with st.form("form_config_agenda"):
            ca1, ca2 = st.columns(2)
            with ca1:
                st.text_input("Horário Comercial", value="08:00 – 18:00")
                st.text_input("Dias Úteis", value="Segunda a Sexta")
                st.selectbox("Duração Padrão das Reuniões", ["15 minutos", "30 minutos", "45 minutos", "1 hora"])
            with ca2:
                st.selectbox("Lembrete Padrão", ["5 minutos antes", "15 minutos antes", "30 minutos antes", "1 hora antes"])
                st.text_area("Tipos de Compromisso", value="Reunião, Demonstração, Ligação, Follow-up, Proposta")
            
            if st.form_submit_button("💾 Salvar Configurações da Agenda"):
                st.success("Configurações da agenda atualizadas!")

    with tab_notif:
        st.markdown("#### 🔔 Configurações de Notificações")
        with st.form("form_config_notif"):
            st.markdown("Selecione os eventos que deseja receber notificações (Sistema | E-mail):")
            
            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1:
                st.checkbox("Novo Lead", value=True)
                st.checkbox("Nova venda", value=True)
            with nc2:
                st.checkbox("Nova proposta", value=True)
                st.checkbox("Atividade vencendo", value=True)
            with nc3:
                st.checkbox("Atividade atrasada", value=True)
                st.checkbox("Novo compromisso", value=True)
            with nc4:
                st.checkbox("Meta atingida", value=True)
                st.checkbox("Meta em risco", value=True)

            if st.form_submit_button("💾 Salvar Preferências de Notificação"):
                st.success("Preferências de notificação salvas!")

    with tab_seguranca:
        st.markdown("#### 🔐 Segurança & Logs de Auditoria")
        
        # Botão fora do form para evitar conflito de API do Streamlit
        if st.button("🔑 Alterar Senha de Administrador"):
            st.info("Painel de alteração de senha acionado.")

        with st.form("form_config_seguranca"):
            s1, s2 = st.columns(2)
            with s1:
                st.checkbox("Autenticação em dois fatores (2FA)", value=False)
                st.number_input("Tempo de expiração da sessão (minutos)", min_value=15, value=60)
            with s2:
                st.selectbox("Bloqueio após tentativas inválidas", ["3 tentativas", "5 tentativas", "Desativado"])
            
            if st.form_submit_button("💾 Salvar Configurações de Segurança"):
                st.success("Configurações de segurança atualizadas!")

        st.markdown("---")
        st.markdown("##### 🛡️ Logs de Auditoria Recentes")
        import pandas as pd
        df_logs = pd.DataFrame([
            {"Ação": "Carlos alterou uma venda", "Data/Hora": "15/08/2026 14:32", "Módulo": "Vendas"},
            {"Ação": "Ana criou um novo Lead", "Data/Hora": "15/08/2026 13:20", "Módulo": "Leads"},
            {"Ação": "Carlos alterou uma proposta", "Data/Hora": "15/08/2026 11:05", "Módulo": "Propostas"}
        ])
        st.dataframe(df_logs, use_container_width=True, hide_index=True)

    with tab_dados:
        st.markdown("#### 💾 Gestão de Dados e Backup")
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown("##### 📥 Exportação e Backup")
            if st.button("📥 Exportar Todos os Dados do CRM"):
                st.success("Arquivo de backup gerado com sucesso!")
            if st.button("📦 Criar Ponto de Restauração (Backup)"):
                st.success("Backup salvo no servidor!")
        with d_col2:
            st.markdown("##### 📤 Importação e Manutenção")
            st.file_uploader("Importar Leads / Clientes (.csv / .xlsx)", type=["csv", "xlsx"])
            if st.button("🧹 Limpar Dados de Teste (Requer Admin)", type="primary"):
                st.warning("Ação restrita a administradores.")
