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
        
        /* Estilização dos Cartões */
        .metric-card {
            background: linear-gradient(145deg, #1f2833, #151a21);
            padding: 20px; border-radius: 12px; border: 1px solid #45f3ff;
            box-shadow: 0 0 15px rgba(69, 243, 255, 0.2); text-align: left;
        }
        .metric-title { color: #66fcf1; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .metric-value { font-size: 26px; font-weight: 800; color: #ffffff; font-family: 'Courier New', monospace; }
        h2, h3 { color: #66fcf1 !important; font-weight: 300 !important; }
        
        /* Barra de filtros horizontal */
        div[data-testid="stHorizontalBlock"] {
            background-color: #151a21;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        /* Botões do Menu Lateral Estilizados (Efeito de Seleção Neon) */
        div.stButton > button {
            background-color: #1f2833 !important;
            color: #ffffff !important;
            border: 1px solid #45f3ff !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            text-align: left !important;
            padding: 10px 15px !important;
        }
        div.stButton > button:hover {
            box-shadow: 0 0 15px rgba(69, 243, 255, 0.6) !important;
            transform: scale(1.02) !important;
            background-color: #151a21 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Funções de navegação do menu lateral
def ir_para_pagina(nome_pagina):
    st.session_state.pagina_atual = nome_pagina

# Construção do Menu Lateral (Sidebar)
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #45f3ff;'>⚡ CRM PRO</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Cada botão atualiza o estado de navegação da sessão ao ser clicado
    st.button("🏠 Dashboard Central", key="nav_dash", use_container_width=True, on_click=ir_para_pagina, args=("🏠 Dashboard Central",))
    st.button("👥 Gestão de Leads", key="nav_leads", use_container_width=True, on_click=ir_para_pagina, args=("👥 Gestão de Leads",))
    st.button("💰 Funil de Vendas", key="nav_funil", use_container_width=True, on_click=ir_para_pagina, args=("💰 Funil de Vendas",))
    st.button("📈 Relatórios Avançados", key="nav_relat", use_container_width=True, on_click=ir_para_pagina, args=("📈 Relatórios Avançados",))
    st.button("⚙️ Configurações", key="nav_config", use_container_width=True, on_click=ir_para_pagina, args=("⚙️ Configurações",))


# ==================== TELA 1: DASHBOARD CENTRAL ====================
if st.session_state.pagina_atual == "🏠 Dashboard Central":
    st.markdown("<h1 style='color: #ffffff; font-weight: 700;'>Dashboard de Performance Comercial</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #c5c6c7;'>Análise de métricas em tempo real com projeções e cores vibrantes.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Barra de Filtros Horizontal
    st.markdown("### 🔍 Filtros de Pesquisa")
    filtro_col1, filtro_col2, filtro_col3, filtro_col4, filtro_col5, filtro_col6, filtro_col7 = st.columns([1.5, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2])
    with filtro_col1: st.selectbox("Período", ["Período a 2026", "Período anterior"])
    with filtro_col2: st.selectbox("Produto", ["Todos", "Software A", "Software C"])
    with filtro_col3: st.selectbox("Equipe", ["Todas", "Equipe Norte", "Equipe Sul"])
    with filtro_col4: st.selectbox("Compra", ["Todas", "Econômica", "Premium"])
    with filtro_col5: st.selectbox("Consultor", ["Todos", "Alex Silva", "Carlos Souza"])
    with filtro_col6: st.selectbox("Ticket Médio", ["Todos", "Alto", "Baixo"])
    with filtro_col7:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Aplicar Filtros", key="apply_f")

    st.markdown("<br>", unsafe_allow_html=True)

    # Dados e Cartões 
    total_leads = 8
    receita_realizada = 90000.00
    valor_pipeline = 115000.00
    ticket_medio = receita_realizada / total_leads

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="metric-card"><div class="metric-title">Total de Leads</div><div class="metric-value">{total_leads}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><div class="metric-title">Valor no Pipeline</div><div class="metric-value">R$ {valor_pipeline:,.2f}</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><div class="metric-title">Receita Realizada</div><div class="metric-value">R$ {receita_realizada:,.2f}</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="metric-card"><div class="metric-title">Ticket Médio Real</div><div class="metric-value" style="color: #45f3ff;">R$ {ticket_medio:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #1f2833;'><br>", unsafe_allow_html=True)

    # Gráficos
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("📈 1. Evolução Cronológica das Vendas")
        dados_vendas = pd.DataFrame({"Data": pd.date_range(start="2026-06-01", periods=6, freq="D"), "Vendas": })
        fig_linha = px.line(dados_vendas, x="Data", y="Vendas", template="plotly_dark")
        fig_linha.update_traces(line_color="#b55fe6", line_width=4, fill='tozeroy', fillcolor='rgba(181, 95, 230, 0.08)')
        fig_linha.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2833'))
        st.plotly_chart(fig_linha, use_container_width=True)
    with col_graf2:
        st.subheader("🎯 2. Índice de Meta vs Realizado")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=78.3, number={'suffix': "%"}, gauge={'bar': {'color': "#00ffcc"}, 'bgcolor': "#151a21", 'borderwidth': 2, 'bordercolor': "#1f2833"}))
        fig_gauge.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280)
        st.plotly_chart(fig_gauge, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)
    with col_graf3:
        st.subheader("👤 4. Distribuição de Receita por Vendedor")
        dados_vendedores = pd.DataFrame({"Vendedor": ["Alex Silva", "Carlos Souza"], "Receita (R$)": })
        fig_vendedor = px.bar(dados_vendedores, x="Vendedor", y="Receita (R$)", color="Vendedor", text_auto='.2s', template="plotly_dark", color_discrete_map={"Alex Silva": "#ff4d6d", "Carlos Souza": "#33b5e5"})
        fig_vendedor.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2833'))
        st.plotly_chart(fig_vendedor, use_container_width=True)
    with col_graf4:
        st.subheader("📦 7. Ranking de Produtos Mais Vendidos")
        dados_produtos = pd.DataFrame({"Produto": ["Software C", "Software A", "Consultoria Técnica"], "Unidades Vendidas": })
        fig_produtos = px.bar(dados_produtos, x="Unidades Vendidas", y="Produto", orientation='h', color="Unidades Vendidas", text_auto=True, template="plotly_dark", color_continuous_scale=["#1a8cff", "#00ffcc"])
        fig_produtos.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_produtos, use_container_width=True)


# ==================== TELA 2: GESTÃO DE LEADS ====================
elif st.session_state.pagina_atual == "👥 Gestão de Leads":
    st.markdown("<h1 style='color: #ffffff;'>👥 Gestão de Leads</h1>", unsafe_allow_html=True)
    st.markdown("Gerencie e cadastre contatos comerciais na sua base.")
    
    # Formulário elegante para entrada de dados reais
    with st.form("Cadastro de Lead"):
        st.markdown("### 📝 Cadastrar Novo Lead")
        nome = st.text_input("Nome do Lead / Empresa")
        status = st.selectbox("Status Inicial", ["Contato Inicial", "Qualificado", "Proposta Enviada", "Negociação"])
        valor_estimado = st.number_input("Valor Estimado do Contrato (R$)", min_value=0.0)
        enviar = st.form_submit_button("Salvar Lead no Sistema")
        if enviar:
            st.success(f"Lead '{nome}' cadastrado com sucesso como {status}!")

    # Tabela dinâmica de Leads cadastrados
    st.markdown("### 📋 Leads Ativos na Base")
    leads_ficticios = pd.DataFrame({
        "Empresa/Cliente": ["Tech Inova", "Global Trade", "Logix BR", "Nexus Digital"],
        "Status": ["Qualificado", "Negociação", "Contato Inicial", "Proposta Enviada"],
        "Valor Estimado": ["R$ 25.000", "R$ 40.000", "R$ 15.000", "R$ 35.000"]
    })
    st.dataframe(leads_ficticios, use_container_width=True)


# ==================== TELA 3: FUNIL DE VENDAS ====================
elif st.session_state.pagina_atual == "💰 Funil de Vendas":
    st.markdown("<h1 style='color: #ffffff;'>💰 Funil de Vendas (Pipeline)</h1>", unsafe_allow_html=True)
    st.markdown("Acompanhe a distribuição financeira das propostas abertas.")
    
    # Gráfico de Funil elegante usando Plotly
    dados_funil = pd.DataFrame({
        "Etapa": ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechado"],
