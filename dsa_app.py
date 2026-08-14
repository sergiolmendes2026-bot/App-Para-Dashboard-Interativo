import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página e Tema Escuro Premium
st.set_page_config(
    page_title="CRM Pro - Dashboard Premium",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do controle de navegação de páginas se não existir
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "🏠 Dashboard Central"

# Estilização CSS Avançada Premium
st.markdown("""
    <style>
        .stApp { background-color: #0b0c10; color: #ffffff; }
        .metric-card {
            background: linear-gradient(145deg, #1f2833, #151a21);
            padding: 20px; border-radius: 12px; border: 1px solid #45f3ff;
            box-shadow: 0 0 15px rgba(69, 243, 255, 0.2); text-align: left;
        }
        .metric-title { color: #66fcf1; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .metric-value { font-size: 26px; font-weight: 800; color: #ffffff; font-family: 'Courier New', monospace; }
        h2, h3 { color: #66fcf1 !important; font-weight: 300 !important; }
        div[data-testid="stHorizontalBlock"] {
            background-color: #151a21; padding: 10px; border-radius: 8px; margin-bottom: 20px;
        }
        div.stSidebar div.stButton > button {
            background-color: #1f2833 !important; color: #ffffff !important;
            border: 1px solid #45f3ff !important; border-radius: 8px !important;
            transition: all 0.3s ease !important; text-align: left !important; padding: 10px 15px !important;
        }
        div.stSidebar div.stButton > button:hover {
            box-shadow: 0 0 15px rgba(69, 243, 255, 0.6) !important; transform: scale(1.02) !important;
        }
    </style>
""", unsafe_allow_html=True)

def ir_para_pagina(nome_pagina):
    st.session_state.pagina_atual = nome_pagina

# Construção do Menu Lateral
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #45f3ff;'>⚡ CRM PRO</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.button("🏠 Dashboard Central", key="nav_dash", use_container_width=True, on_click=ir_para_pagina, args=("🏠 Dashboard Central",))
    st.button("👥 Gestão de Leads", key="nav_leads", use_container_width=True, on_click=ir_para_pagina, args=("👥 Gestão de Leads",))
    st.button("💰 Funil de Vendas", key="nav_funil", use_container_width=True, on_click=ir_para_pagina, args=("💰 Funil de Vendas",))
    st.button("📈 Relatórios Avançados", key="nav_relat", use_container_width=True, on_click=ir_para_pagina, args=("📈 Relatórios Avançados",))
    st.button("⚙️ Configurações", key="nav_config", use_container_width=True, on_click=ir_para_pagina, args=("⚙️ Configurações",))

# CARD DATA
total_leads = 8
receita_realizada = 90000.00
valor_pipeline = 115000.00
ticket_medio = receita_realizada / total_leads

# ==================== TELA 1: DASHBOARD CENTRAL ====================
if st.session_state.pagina_atual == "🏠 Dashboard Central":
    st.markdown("<h1 style='color: #ffffff; font-weight: 700;'>Dashboard de Performance Comercial</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros
    filtro_col1, filtro_col2, filtro_col3, filtro_col4, filtro_col5, filtro_col6 = st.columns(6)
    with filtro_col1: st.selectbox("Período", ["Mês Atual", "Mês Anterior"])
    with filtro_col2: st.selectbox("Produto", ["Todos", "Software A", "Software C"])
    with filtro_col3: st.selectbox("Equipe", ["Todas", "Norte", "Sul"])
    with filtro_col4: st.selectbox("Compra", ["Todas", "Premium"])
    with filtro_col5: st.selectbox("Consultor", ["Todos", "Alex Silva"])
    with filtro_col6: st.selectbox("Ticket", ["Todos", "Alto"])

    # Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="metric-card"><div class="metric-title">Total de Leads</div><div class="metric-value">{total_leads}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><div class="metric-title">Valor no Pipeline</div><div class="metric-value">R$ {valor_pipeline:,.2f}</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><div class="metric-title">Receita Realizada</div><div class="metric-value">R$ {receita_realizada:,.2f}</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="metric-card"><div class="metric-title">Ticket Médio Real</div><div class="metric-value" style="color: #45f3ff;">R$ {ticket_medio:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos de forma simples e linear sem estruturas aninhadas perigosas
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("📈 1. Evolução Cronológica das Vendas")
        datas_lista = ["01/08", "03/08", "05/08", "07/08", "10/08", "14/08"]
        vendas_lista = [10000, 25000, 18000, 42000, 31000, 90000]
        dados_vendas = pd.DataFrame()
        dados_vendas["Data"] = datas_lista
        dados_vendas["Vendas"] = vendas_lista
        fig_linha = px.line(dados_vendas, x="Data", y="Vendas", template="plotly_dark")
        fig_linha.update_traces(line_color="#b55fe6", line_width=4, fill='tozeroy', fillcolor='rgba(181, 95, 230, 0.08)')
        fig_linha.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_linha, use_container_width=True)
        
    with col_graf2:
        st.subheader("🎯 2. Índice de Meta vs Realizado")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=78.3, number={'suffix': "%"}, gauge={'bar': {'color': "#00ffcc"}, 'bgcolor': "#151a21"}))
        fig_gauge.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280)
        st.plotly_chart(fig_gauge, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)
    with col_graf3:
        st.subheader("👤 4. Distribuição de Receita por Vendedor")
        vendedores = ["Alex Silva", "Carlos Souza"]
        valores_venda = [55000, 35000]
        dados_vendedores = pd.DataFrame()
        dados_vendedores["Vendedor"] = vendedores
        dados_vendedores["Receita (R$)"] = valores_venda
        fig_vendedor = px.bar(dados_vendedores, x="Vendedor", y="Receita (R$)", color="Vendedor", template="plotly_dark", color_discrete_map={"Alex Silva": "#ff4d6d", "Carlos Souza": "#33b5e5"})
        fig_vendedor.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_vendedor, use_container_width=True)
        
    with col_graf4:
        st.subheader("📦 7. Ranking de Produtos Mais Vendidos")
        produtos = ["Software C", "Software A", "Consultoria"]
        unidades = [12, 8, 4]
        dados_produtos = pd.DataFrame()
        dados_produtos["Produto"] = produtos
        dados_produtos["Unidades Vendidas"] = unidades
        fig_produtos = px.bar(dados_produtos, x="Unidades Vendidas", y="Produto", orientation='h', color="Unidades Vendidas", template="plotly_dark", color_continuous_scale=["#1a8cff", "#00ffcc"])
        fig_produtos.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_produtos, use_container_width=True)

# ==================== TELA 2: GESTÃO DE LEADS ====================
elif st.session_state.pagina_atual == "👥 Gestão de Leads":
    st.markdown("<h1 style='color: #ffffff;'>👥 Gestão Estratégica de Leads</h1>", unsafe_allow_html=True)
    
    with st.form("Cadastro de Lead"):
        st.markdown("### 📝 Cadastrar Novo Lead")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            nome = st.text_input("Nome do Lead / Empresa")
            email = st.text_input("E-mail Comercial")
        with f_col2:
            status = st.selectbox("Status Inicial", ["Contato Inicial", "Qualificado", "Proposta Enviada", "Negociação"])
            telefone = st.text_input("Telefone / WhatsApp")
        with f_col3:
            valor_est = st.number_input("Valor Estimado (R$)", min_value=0.0)
            origem = st.selectbox("Origem do Lead", ["Google Ads", "Instagram", "Indicação", "WhatsApp"])
            
        responsavel = st.selectbox("Responsável Comercial", ["Alex Silva", "Carlos Souza"])
        enviar = st.form_submit_button("🚀 Gravar Oportunidade")
        if enviar: st.success("Lead Cadastrado!")

    st.markdown("### 📋 Visão Geral dos Leads Ativos")
    
    # Estruturação limpa da tabela de Leads para evitar quebra de dicionário
    tabela_leads = pd.DataFrame()
    tabela_leads["Data"] = ["02/08/2026", "07/08/2026", "11/08/2026", "13/08/2026"]
    tabela_leads["Cliente / Empresa"] = ["Tech Inova Ltda", "Global Trade Import", "Logix BR", "Nexus Digital"]
    tabela_leads["Estágio Comercial"] = ["Qualificado", "Negociação", "Contato Inicial", "Proposta Enviada"]
    tabela_leads["Proposta (R$)"] = [25000.0, 40000.0, 15000.0, 35000.0]
    tabela_leads["WhatsApp"] = ["(11) 99888-7766", "(21) 98765-4321", "(31) 99123-4567", "(11) 97654-3210"]
    tabela_leads["Canal Origem"] = ["Google Ads", "Indicação", "Instagram", "WhatsApp"]
    tabela_leads["Vendedor"] = ["Alex Silva", "Carlos Souza", "Alex Silva", "Carlos Souza"]
    
    st.dataframe(tabela_leads, use_container_width=True)

# ==================== TELA 3: FUNIL DE VENDAS ====================
elif st.session_state.pagina_atual == "💰 Funil de Vendas":
    st.markdown("<h1 style='color: #ffffff;'>💰 Funil de Vendas (Pipeline)</h1>", unsafe_allow_html=True)
    
    etapas_funil = ["1. Prospecção", "2. Qualificação", "3. Proposta", "4. Negociação", "5. Fechado"]
    valores_funil = [150000, 115000, 95000, 90000, 60000]
    
    df_funil = pd.DataFrame()
    df_funil["Etapa"] = etapas_funil
    df_funil["Volume (R$)"] = valores_funil
