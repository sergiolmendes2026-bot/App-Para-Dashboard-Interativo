import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- FUNÇÕES DE GRÁFICOS ---
def plot_vendas_evolucao(df):
    df_g = df.groupby('data')['valor'].sum().reset_index()
    fig = px.line(df_g, x='data', y='valor', title="Evolução das Vendas")
    return fig

def plot_funil(df_pipe):
    # Assume que estagios estão ordenados
    fig = px.funnel(df_pipe, x='valor', y='estagio')
    return fig

def plot_receita_vendedor(df):
    fig = px.bar(df.groupby('responsavel')['valor'].sum().reset_index(), x='responsavel', y='valor', title="Receita por Vendedor")
    return fig

# --- DASHBOARD PRINCIPAL ---
if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    
    # 1. KPIs no Topo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads", len(df_clientes))
    c2.metric("Pipeline", f"R$ {df_pipeline['valor'].sum():,.2f}")
    c3.metric("Receita", f"R$ {df_vendas['valor'].sum():,.2f}")
    c4.metric("Meta", "R$ 500k") # Exemplo fixo ou vindo de banco

    # GRID DE GRÁFICOS
    # Usamos st.columns(2) para organizar em colunas
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1: st.plotly_chart(plot_vendas_evolucao(df_vendas), use_container_width=True)
    with r1_c2: st.plotly_chart(plot_funil(df_pipeline), use_container_width=True)

    r2_c1, r2_c2 = st.columns(2)
    with r2_c1: st.plotly_chart(plot_receita_vendedor(df_vendas), use_container_width=True)
    with r2_c2:
        # Origem dos Leads (Pizza)
        fig = px.pie(df_clientes, names='origem', title="Origem dos Leads", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    # 5. Meta x Realizado (Gauge)
    meta = 500000
    realizado = df_vendas['valor'].sum()
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = realizado,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Meta x Realizado"},
        gauge = {'axis': {'range': [None, meta]}, 'bar': {'color': cor_hex}}
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 6. Produtos mais vendidos (Barras Horizontais)
    # Requer coluna 'produto' no df_vendas
    if 'produto' in df_vendas.columns:
        fig = px.bar(df_vendas.groupby('produto')['valor'].sum().reset_index(), x='valor', y='produto', orientation='h', title="Produtos mais Vendidos")
        st.plotly_chart(fig, use_container_width=True)

    # 7. Clientes por Status (Donut)
    fig_status = px.pie(df_clientes, names='status', title="Clientes por Status", hole=0.5)
    st.plotly_chart(fig_status, use_container_width=True)

    # 8. Motivos de Perda (Barras)
    fig_perda = px.bar(df_clientes[df_clientes['status'] == 'Venda Perdida'].groupby('motivo_perda').size().reset_index(name='count'), x='motivo_perda', y='count', title="Motivos de Perda")
    st.plotly_chart(fig_perda, use_container_width=True)
