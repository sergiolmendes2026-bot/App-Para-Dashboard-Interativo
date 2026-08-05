import streamlit as st
import sqlite3
import pandas as pd
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas estejam criados
inicializar_banco()

st.set_page_config(
    page_title="Dashboard CRM de Vendas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Executivo - CRM de Vendas")
st.write("Visão geral dos indicadores de clientes, pipeline, interações e faturamento.")

# Funções para carregar dados do SQLite em DataFrames do Pandas
def carregar_dados():
    conn = conectar()
    
    # Clientes
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    
    # Pipeline
    df_pipeline = pd.read_sql("""
        SELECT p.id, p.id_cliente, c.nome as cliente, p.titulo, p.estagio, p.valor 
        FROM pipeline p
        JOIN clientes c ON p.id_cliente = c.id
    """, conn)
    
    # Vendas
    df_vendas = pd.read_sql("""
        SELECT v.id, v.id_cliente, c.nome as cliente, v.valor, v.data_venda, v.produto_servico 
        FROM vendas v
        JOIN clientes c ON v.id_cliente = c.id
    """, conn)
    
    # Interações
    df_interacoes = pd.read_sql("""
        SELECT i.id, i.id_cliente, c.nome as cliente, i.tipo, i.descricao, i.data_interacao 
        FROM interacoes i
        JOIN clientes c ON i.id_cliente = c.id
    """, conn)
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas, df_interacoes

df_clientes, df_pipeline, df_vendas, df_interacoes = carregar_dados()

# Métricas Principais (KPIs)
total_clientes = len(df_clientes)
total_vendas_valor = df_vendas["valor"].sum() if not df_vendas.empty else 0.0
total_oportunidades = len(df_pipeline)
pipeline_valor = df_pipeline["valor"].sum() if not df_pipeline.empty else 0.0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Clientes", total_clientes)
with col2:
    st.metric("Faturamento Total", f"R$ {total_vendas_valor:,.2f}")
with col3:
    st.metric("Oportunidades no Pipeline", total_oportunidades)
with col4:
    st.metric("Valor em Pipeline", f"R$ {pipeline_valor:,.2f}")

st.divider()

# Seção de Gráficos e Tabelas Resumo
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💰 Vendas por Produto / Serviço")
    if not df_vendas.empty:
        df_vendas_grouped = df_vendas.groupby("produto_servico")["valor"].sum().reset_index()
        st.dataframe(df_vendas_grouped, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada para exibir no gráfico.")

with col_right:
    st.subheader("📈 Oportunidades por Estágio")
    if not df_pipeline.empty:
        df_pipe_grouped = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
        st.dataframe(df_pipe_grouped, use_container_width=True)
    else:
        st.info("Nenhuma oportunidade no pipeline para exibir.")

st.divider()

# Tabela Recente de Clientes
st.subheader("👥 Clientes Cadastrados Recentemente")
if not df_clientes.empty:
    st.dataframe(df_clientes[["nome", "empresa", "email", "telefone", "regiao", "data_cadastro"]], use_container_width=True)
else:
    st.info("Nenhum cliente cadastrado ainda. Use a página '1_Cadastro_de_Clientes' para começar.")
