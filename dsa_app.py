import pandas as pd
import sqlite3
import streamlit as st
from database import conectar, inicializar_banco
from streamlit_option_menu import option_menu

# Garante que o banco e as tabelas estejam criados
inicializar_banco()

st.set_page_config(
    page_title="Dashboard CRM de Vendas", page_icon="📊", layout="wide"
)

# --- BARRA LATERAL COM MENU MODERNIZADO ---
with st.sidebar:
  st.markdown("### 🚀 dsa app")
  selected = option_menu(
      menu_title=None,
      options=[
          "Dashboard",
          "Cadastro de Clientes",
          "Pipeline de Vendas",
          "Interações",
          "Vendas",
          "Integrações",
      ],
      icons=[
          "speedometer2",
          "people-fill",
          "kanban-fill",
          "chat-dots-fill",
          "cart-fill",
          "plug-fill",
      ],
      menu_icon="cast",
      default_index=0,
      styles={
          "container": {"padding": "0!important", "background-color": "transparent"},
          "icon": {"color": "#ff4b4b", "font-size": "16px"},
          "nav-link": {
              "font-size": "14px",
              "text-align": "left",
              "margin": "4px 0px",
              "--hover-color": "#262730",
          },
          "nav-link-selected": {
              "background-color": "#ff4b4b",
              "color": "white",
          },
      },
  )

# --- FUNÇÃO PARA CARREGAR DADOS DE FORMA SEGURA ---


def carregar_dados():
  conn = conectar()

  df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
  df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
  df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
  df_interacoes = pd.read_sql("SELECT * FROM interacoes", conn)

  conn.close()
  return df_clientes, df_pipeline, df_vendas, df_interacoes


df_clientes, df_pipeline, df_vendas, df_interacoes = carregar_dados()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
  st.title("📊 Dashboard Executivo - CRM de Vendas")
  st.write(
      "Visão geral dos indicadores de clientes, pipeline, interações e"
      " faturamento."
  )

  # Métricas Principais (KPIs)
  total_clientes = len(df_clientes)
  total_vendas_valor = (
      df_vendas["valor"].sum()
      if not df_vendas.empty and "valor" in df_vendas.columns
      else 0.0
  )
  total_oportunidades = len(df_pipeline)
  pipeline_valor = (
      df_pipeline["valor"].sum()
      if not df_pipeline.empty and "valor" in df_pipeline.columns
      else 0.0
  )

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
    if not df_vendas.empty and "produto_servico" in df_vendas.columns:
      df_vendas_grouped = (
          df_vendas.groupby("produto_servico")["valor"].sum().reset_index()
      )
      st.dataframe(df_vendas_grouped, use_container_width=True)
    else:
      st.info("Nenhuma venda registrada para exibir no gráfico.")

  with col_right:
    st.subheader("📈 Oportunidades por Estágio")
    if not df_pipeline.empty and "estagio" in df_pipeline.columns:
      df_pipe_grouped = (
          df_pipeline.groupby("estagio")["valor"].sum().reset_index()
      )
      st.dataframe(df_pipe_grouped, use_container_width=True)
    else:
      st.info("Nenhuma oportunidade no pipeline para exibir.")

  st.divider()

  # Tabela Recente de Clientes
  st.subheader("👥 Clientes Cadastrados Recentemente")
  if not df_clientes.empty:
    colunas_exibir = [
        col
        for col in [
            "nome",
            "empresa",
            "email",
            "telefone",
            "regiao",
            "data_cadastro",
        ]
        if col in df_clientes.columns
    ]
    st.dataframe(df_clientes[colunas_exibir], use_container_width=True)
  else:
    st.info("Nenhum cliente cadastrado ainda.")

elif selected == "Cadastro de Clientes":
  st.title("👥 Cadastro de Clientes")
  st.write("Gerencie os registros de clientes do seu CRM.")
  if not df_clientes.empty:
    st.dataframe(df_clientes, use_container_width=True)
  else:
    st.info("Nenhum cliente cadastrado.")

elif selected == "Pipeline de Vendas":
  st.title("📊 Pipeline de Vendas")
  st.write("Acompanhamento do funil de oportunidades comerciais.")
  if not df_pipeline.empty:
    st.dataframe(df_pipeline, use_container_width=True)
  else:
    st.info("Nenhuma oportunidade no pipeline.")

elif selected == "Interações":
  st.title("💬 Histórico de Interações")
  st.write("Acompanhe o registro de contatos com os clientes.")
  if not df_interacoes.empty:
    st.dataframe(df_interacoes, use_container_width=True)
  else:
    st.info("Nenhuma interação registrada.")

elif selected == "Vendas":
  st.title("💰 Gestão de Vendas")
  st.write("Controle completo de faturamento e vendas realizadas.")
  if not df_vendas.empty:
    st.dataframe(df_vendas, use_container_width=True)
  else:
    st.info("Nenhuma venda cadastrada.")

elif selected == "Integrações":
  st.title("🔌 Configuração de Integrações")
  st.write("Gerencie as conexões com APIs e ferramentas externas.")
  st.info("Nenhuma integração configurada no momento.")
