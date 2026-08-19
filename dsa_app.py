import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuração inicial da página
st.set_page_config(
    page_title="LaryMB AI Service",
    page_icon="🤖",
    layout="wide"
)

# Estilização visual (Tema escuro customizado)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #161b22;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MENU LATERAL (SIDEBAR) COMPLETO
# ---------------------------------------------------------
st.sidebar.markdown("### 🤖 LaryMB AI Service")
st.sidebar.markdown("---")

menu_escolhido = st.sidebar.radio(
    "Menu Principal",
    [
        "Dashboard de TI",
        "🎫 Service Desk",
        "🖥️ Gestão de Sistemas SaaS",
        "🚨 Incidentes",
        "⏱️ SLA",
        "📚 Base de Conhecimento",
        "🤖 AI Assistant",
        "🔎 RAG",
        "🧠 AI Agents",
        "⚙️ Automação",
        "📊 Analytics",
        "🔐 Segurança",
        "👥 Usuários e Permissões",
        "☁️ Cloud"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("👤 **Usuário:** Sérgio Luís")
st.sidebar.markdown("🟢 **Status:** Online")

# Assistente de IA na Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Copiloto IA")
user_query = st.sidebar.text_input("Consulte a base de dados via IA...")
if user_query:
    st.sidebar.info("IA: Processando RAG nos chamados anteriores...")
    st.sidebar.write("💡 Sugestão: Reinicie o container Docker do serviço afetado.")

# ---------------------------------------------------------
# GERAÇÃO DE DADOS MOCKADOS PARA O ITSM
# ---------------------------------------------------------
np.random.seed(42)
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
sistemas = ['AWS Cloud', 'Salesforce', 'Jira', 'ERP SAP', 'Microsoft 365', 'Slack']
prioridades = ['Baixa', 'Média', 'Alta', 'Crítica']
categorias = ['Acesso', 'Hardware', 'Software', 'Rede', 'Segurança']

# DataFrame para Gráfico 1 (Abertos vs Resolvidos)
df_abertos_resolvidos = pd.DataFrame({
    'Mes': meses,
    'Abertos': np.random.randint(30, 90, 12),
    'Resolvidos': np.random.randint(25, 85, 12),
    'Meta': np.linspace(40, 100, 12)
})

# DataFrame para Demais Gráficos
df_tickets = pd.DataFrame({
    'sistema': np.random.choice(sistemas, 200),
    'prioridade': np.random.choice(prioridades, 200, p=[0.4, 0.3, 0.2, 0.1]),
    'status_sla': np.random.choice(['Dentro do Prazo', 'Fora do Prazo'], 200, p=[0.8, 0.2]),
    'categoria': np.random.choice(categorias, 200),
    'status_sistema': np.random.choice(['Operacional', 'Degradado', 'Fora do Ar'], 200, p=[0.75, 0.2, 0.05]),
    'nivel_suporte': np.random.choice(['N1', 'N2'], 200)
})

# ---------------------------------------------------------
# CORPO DA APLICAÇÃO (DASHBOARD OU MÓDULOS)
# ---------------------------------------------------------
if menu_escolhido == "Dashboard de TI":
    st.title("📊 LaryMB AI Service — Dashboard de TI & Operações")
    st.markdown("Monitoramento em tempo real de infraestrutura, chamados de suporte e performance de IA.")
    
    # Grid de Gráficos (Organização 2x4)
    
    # Linha 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Chamados Abertos vs. Resolvidos")
        fig1 = px.bar(df_abertos_resolvidos, x='Mes', y=['Abertos', 'Resolvidos'], barmode='group')
        fig1.add_scatter(x=df_abertos_resolvidos['Mes'], y=df_abertos_resolvidos['Meta'], mode='lines', name='Meta de Resolução', line=dict(color='red'))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.markdown("### 2. Chamados por Prioridade")
        fig2 = px.pie(df_tickets, names='prioridade', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig2, use_container_width=True)

    # Linha 2
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 3. Incidentes por Sistema SaaS")
        fig3 = px.funnel(df_tickets.groupby('sistema').size().reset_index(name='count'), x='count', y='sistema')
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        st.markdown("### 4. SLA — Dentro vs. Fora do Prazo")
        fig4 = px.histogram(df_tickets, x='sistema', color='status_sla', barmode='group')
        st.plotly_chart(fig4, use_container_width=True)

    # Linha 3
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### 5. Tempo Médio de Resolução (MTTR)")
        df_mttr = pd.DataFrame({'Equipe': ['Redes', 'DevOps', 'Segurança', 'Suporte N1', 'Cloud'], 'Horas': [4.2, 2.5, 6.1, 1.8, 3.4]})
        fig5 = px.funnel(df_mttr, x='Horas', y='Equipe')
        st.plotly_chart(fig5, use_container_width=True)
        
    with col6:
        st.markdown("### 6. Status dos Sistemas SaaS")
        fig6 = px.pie(df_tickets, names='status_sistema', hole=0.6, color_discrete_sequence=['#2ecc71', '#f1c40f', '#e74c3c'])
        st.plotly_chart(fig6, use_container_width=True)

    # Linha 4
    col7, col8 = st.columns(2)
    
    with col7:
        st.markdown("### 7. Performance N1/N2")
        fig7 = px.histogram(df_tickets, x='nivel_suporte', color='status_sla', barmode='stack')
        st.plotly_chart(fig7, use_container_width=True)
        
    with col8:
        st.markdown("### 8. Atendimentos por Categoria")
        fig8 = px.histogram(df_tickets, x='categoria', color='prioridade', barmode='stack')
        st.plotly_chart(fig8, use_container_width=True)

else:
    st.title(f"📁 Módulo: {menu_escolhido}")
    st.write(f"Ambiente de gerenciamento e controle para **{menu_escolhido}** integrado ao ecossistema LaryMB AI Service.")
    
    st.markdown("---")
    st.subheader("Registros e Monitoramento do Banco de Dados")
    st.dataframe(df_tickets.head(10), use_container_width=True)
