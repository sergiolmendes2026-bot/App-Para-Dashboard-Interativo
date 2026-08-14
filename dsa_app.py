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

# Estilização CSS Avançada para emular o design futurista da imagem
st.markdown("""
    <style>
        /* Fundo geral e fontes */
        .stApp {
            background-color: #0b0c10;
            color: #ffffff;
        }
        
        /* Estilização dos Cartões do Topo com Efeito de Brilho */
        .metric-card {
            background: linear-gradient(145deg, #1f2833, #151a21);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #45f3ff;
            box-shadow: 0 0 15px rgba(69, 243, 255, 0.2);
            text-align: left;
            transition: transform 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 25px rgba(69, 243, 255, 0.4);
        }
        .metric-title { 
            color: #66fcf1; 
            font-size: 13px; 
            text-transform: uppercase; 
            letter-spacing: 1px;
            margin-bottom: 8px; 
        }
        .metric-value { 
            font-size: 26px; 
            font-weight: 800; 
            color: #ffffff; 
            font-family: 'Courier New', monospace;
        }
        
        /* Ajustes nos títulos das seções */
        h2, h3 {
            color: #66fcf1 !important;
            font-weight: 300 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Menu Lateral Customizado
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #45f3ff;'>⚡ CRM PRO</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.button("🏠 Dashboard Central", use_container_width=True)
    st.button("👥 Gestão de Leads", use_container_width=True)
    st.button("💰 Funil de Vendas", use_container_width=True)
    st.button("📈 Relatórios Avançados", use_container_width=True)
    st.button("⚙️ Configurações", use_container_width=True)

# Título Principal do Dashboard
st.markdown("<h1 style='color: #ffffff; font-weight: 700;'>Dashboard de Performance Comercial</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #c5c6c7;'>Análise de métricas em tempo real com projeções corrigidas.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 3. Dados e Cálculos Corrigidos
total_leads = 8
receita_realizada = 90000.00
valor_pipeline = 115000.00
ticket_medio = receita_realizada / total_leads  # Cálculo exato corrigido

# 4. Renderização dos Novos Cartões Estilizados
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total de Leads</div><div class="metric-value">{total_leads}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Valor no Pipeline</div><div class="metric-value">R$ {valor_pipeline:,.2f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Receita Realizada</div><div class="metric-value">R$ {receita_realizada:,.2f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Ticket Médio Real</div><div class="metric-value" style="color: #45f3ff;">R$ {ticket_medio:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: #1f2833;'><br>", unsafe_allow_html=True)

# 5. Linha de Gráficos Superior (Evolução e Meta)
col_graf1, col_graf2 = st.columns()

with col_graf1:
    st.subheader("📊 1. Evolução Cronológica das Vendas")
    dados_vendas = pd.DataFrame({
        "Data": pd.date_range(start="2026-06-01", periods=6, freq="D"),
        "Vendas": [15000, 22000, 18000, 12000, 28000, 35000]
    })
    fig_linha = px.line(dados_vendas, x="Data", y="Vendas", template="plotly_dark")
    # Aplicando o degradê neon na linha do gráfico
    fig_linha.update_traces(line_color="#45f3ff", line_width=4, fill='tozeroy', fillcolor='rgba(69, 243, 255, 0.05)')
    fig_linha.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1f2833')
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with col_graf2:
    st.subheader("🎯 2. Índice de Meta vs Realizado")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=78.3,  # Percentual calculado da meta
        number={'suffix': "%", 'font': {'color': '#ffffff', 'size': 40}},
        gauge={
            'axis': {'range':, 'tickwidth': 1, 'tickcolor': "#45f3ff"},
            'bar': {'color': "#45f3ff"},
            'bgcolor': "#151a21",
            'borderwidth': 2,
            'bordercolor': "#1f2833",
            'steps': [
                {'range':, 'color': 'rgba(255, 77, 77, 0.2)'},
                {'range':, 'color': 'rgba(255, 165, 0, 0.2)'},
                {'range':, 'color': 'rgba(0, 230, 118, 0.2)'}
            ],
        }
    ))
    fig_gauge.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        height=280,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# 6. Linha de Gráficos Inferior (Vendedores e Produtos)
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("👤 4. Distribuição de Receita por Vendedor")
    dados_vendedores = pd.DataFrame({
        "Vendedor": ["Alex Silva", "Carlos Souza"],
        "Receita (R$)": [60000, 30000]
    })
    # Criando barras verticais limpas com rótulos de dados visíveis
    fig_vendedor = px.bar(
        dados_vendedores, 
        x="Vendedor", 
        y="Receita (R$)", 
        text_auto='.2s', 
        template="plotly_dark"
    )
    fig_vendedor.update_traces(
        marker_color="#45f3ff", 
        textposition="outside",
        cliponaxis=False
    )
    fig_vendedor.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1f2833')
    )
    st.plotly_chart(fig_vendedor, use_container_width=True)

with col_graf4:
    st.subheader("📦 7. Ranking de Produtos Mais Vendidos")
    dados_produtos = pd.DataFrame({
        "Produto": ["Software C", "Software A", "Consultoria Técnica"],
        "Unidades Vendidas": [45, 30, 15]
    })
    # Gráfico horizontal limpo com rótulos numéricos diretos nas barras
    fig_produtos = px.bar(
        dados_produtos, 
        x="Unidades Vendidas", 
        y="Produto", 
        orientation='h', 
        text_auto=True, 
        template="plotly_dark"
    )
    fig_produtos.update_traces(
        marker_color="#1f2833", 
        marker_line_color="#45f3ff",
        marker_line_width=2,
        textposition="inside"
    )
    fig_produtos.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#1f2833'),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_produtos, use_container_width=True)
