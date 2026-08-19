import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página em modo wide para aproveitar o layout do painel
st.set_page_config(
    page_title="LaryMB AI Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para um visual Dark Mode moderno estilo SaaS corporativo
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    div.stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #1f2937;
    }
    .card-container {
        background-color: #111827;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #1f2937;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MENU LATERAL (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🤖 LaryMB AI Service")
    st.markdown("<p style='font-size: 11px; color: #9ca3af;'>Intelligent IT Service Management Platform</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu_selecionado = st.radio(
        "Navegação Principal",
        [
            "Dashboard",
            "Chamados",
            "Incidentes",
            "Solicitações",
            "Problemas",
            "Mudanças",
            "Base de Conhecimento",
            "Sistemas SaaS",
            "Ativos de TI",
            "SLA & Contratos",
            "Usuários",
            "Equipes",
            "Relatórios",
            "IA & Automação",
            "Integrações",
            "Notificações",
            "Configurações"
        ]
    )
    
    st.markdown("---")
    st.markdown("**Status da Plataforma**")
    st.markdown("🟢 Operacional")
    st.markdown("<p style='font-size: 10px; color: #6b7280;'>Versão 1.0.0</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL: DASHBOARD DE TI
# ---------------------------------------------------------
if menu_selecionado == "Dashboard":
    
    # Cabeçalho Superior
    col_title, col_user = st.columns([4, 1])
    with col_title:
        st.title("📊 Dashboard")
    with col_user:
        st.markdown("<div style='text-align: right; padding-top: 10px;'><b>Sergio Luiz</b><br><span style='font-size: 11px; color: #9ca3af;'>Administrador</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Linha 1: Cartões de Métricas Principais (6 blocos)
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric("Chamados Abertos", "128", "+12 hoje")
    with m2:
        st.metric("Chamados Resolvidos", "342", "+28 hoje")
    with m3:
        st.metric("Em Andamento", "45", "+5 hoje")
    with m4:
        st.metric("SLA Fora do Prazo", "12", "-3 hoje", delta_color="inverse")
    with m5:
        st.metric("MTTR (h)", "3,2", "-0,6h")
    with m6:
        st.metric("Sistemas Online", "95%", "+2%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 2: Chamados por Prioridade vs. Chamados Recentes
    col_l2_1, col_l2_2 = st.columns([1, 1.8])
    
    with col_l2_1:
        st.subheader("Chamados Abertos por Prioridade")
        # Gráfico de Rosca (Donut Chart)
        df_prioridade = pd.DataFrame({
            'Prioridade': ['Crítica', 'Alta', 'Média', 'Baixa'],
            'Quantidade': [38, 36, 42, 22]
        })
        fig_donut = px.pie(
            df_prioridade, 
            names='Prioridade', 
            values='Quantidade', 
            hole=0.6,
            color='Prioridade',
            color_discrete_map={'Crítica': '#dc2626', 'Alta': '#ea580c', 'Média': '#facc15', 'Baixa': '#16a34a'}
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="v", y=0.5, x=1.0)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("<div style='text-align: right; font-size: 12px; color: #9ca3af;'>Total: <b>128</b></div>", unsafe_allow_html=True)

    with col_l2_2:
        st.subheader("Chamados Recentes")
        df_recentes = pd.DataFrame({
            'ID': ['#CH-10234', '#CH-10233', '#CH-10232', '#CH-10231', '#CH-10230'],
            'Título': ['Erro ao acessar o ERP', 'Falha na integração com API', 'Impressora sem resposta', 'Solicitação de acesso VPN', 'Tela azul no Windows 11'],
            'Solicitante': ['Ana Souza', 'Carlos Mendes', 'João Ferreira', 'Mariana Lima', 'Pedro Oliveira'],
            'Prioridade': ['Alta', 'Crítica', 'Média', 'Baixa', 'Alta'],
            'Status': ['Em Andamento', 'Em Andamento', 'Novo', 'Novo', 'Em Andamento'],
            'Abertura': ['31/05/2026 10:23', '31/05/2026 09:58', '31/05/2026 09:41', '31/05/2026 09:15', '31/05/2026 08:52']
        })
        st.dataframe(df_recentes, use_container_width=True, hide_index=True)
        st.markdown("<div style='text-align: right;'><a href='#' style='color: #3b82f6; font-size: 13px; text-decoration: none;'>Ver todos os chamados →</a></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 3: Incidentes por Sistema SaaS | SLA - Cumprimento | Atendimentos por Categoria
    col_l3_1, col_l3_2, col_l3_3 = st.columns([1, 1, 1])

    with col_l3_1:
        st.subheader("Incidentes por Sistema SaaS")
        df_saas = pd.DataFrame({
            'Sistema': ['Microsoft 365', 'Salesforce', 'SAP Business One', 'Totvs Protheus', 'Google Workspace'],
            'Incidentes': [24, 18, 15, 10, 8]
        })
        fig_bar = px.bar(
            df_saas, 
            x='Incidentes', 
            y='Sistema', 
            orientation='h',
            color_discrete_sequence=['#3b82f6']
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("<div style='text-align: right;'><a href='#' style='color: #3b82f6; font-size: 13px; text-decoration: none;'>Ver todos os sistemas →</a></div>", unsafe_allow_html=True)

    with col_l3_2:
        st.subheader("SLA - Cumprimento")
        fig_sla = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 87,
            number = {'suffix': "%", 'font': {'color': 'white'}},
            title = {'text': "Dentro do prazo", 'font': {'size': 14, 'color': '#9ca3af'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "white"},
                'bar': {'color': '#10b981'},
                'bgcolor': "#1f2937",
                'steps': [
                    {'range': [0, 80], 'color': '#ef4444'},
                    {'range': [80, 100], 'color': '#065f46'}
                ],
            }
        ))
        fig_sla.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            height=220,
            margin=dict(t=20, b=10, l=20, r=20)
        )
        st.plotly_chart(fig_sla, use_container_width=True)
        st.markdown("<span style='color: #10b981;'>🟢 Dentro do prazo: 312 (87%)</span><br><span style='color: #ef4444;'>🔴 Fora do prazo: 38 (11%)</span><br><span style='color: #f59e0b;'>🟡 Pausado: 8 (2%)</span>", unsafe_allow_html=True)

    with col_l3_3:
        st.subheader("Atendimentos por Categoria")
        st.markdown("""
        - 🔵 **Acesso / Permissões:** 56 (26%)
        - 🔵 **Falhas / Erros:** 48 (22%)
        - 🔵 **Solicitações:** 46 (21%)
        - 🟢 **Hardware:** 24 (11%)
        - 🟣 **Software:** 20 (9%)
        - 🟡 **Outros:** 18 (8%)
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: right;'><a href='#' style='color: #3b82f6; font-size: 13px; text-decoration: none;'>Ver todas as categorias →</a></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 4: Atendimentos por Equipe | Base de Conhecimento | IA & Automação
    col_l4_1, col_l4_2, col_l4_3 = st.columns([1.2, 1, 1])

    with col_l4_1:
        st.subheader("Atendimentos por Equipe")
        df_equipes = pd.DataFrame({
            'Equipe': ['N1 - Suporte', 'N2 - Especialista', 'Infraestrutura', 'Sistemas'],
            'Abertos': [72, 32, 14, 10],
            'Em Andamento': [28, 12, 5, 4],
            'Resolvidos': [152, 98, 56, 36],
            'SLA (%)': ['91%', '85%', '88%', '90%']
        })
        st.dataframe(df_equipes, use_container_width=True, hide_index=True)
        st.markdown("<div style='text-align: right;'><a href='#' style='color: #3b82f6; font-size: 13px; text-decoration: none;'>Ver equipes →</a></div>", unsafe_allow_html=True)

    with col_l4_2:
        st.subheader("Base de Conhecimento")
        st.markdown("""
        **Como redefinir senha no AD**  
        <span style='font-size: 12px; color: #9ca3af;'>Visualizações: 124 | Atualizado: 29/05/2026</span>  
        <hr style='border-color: #1f2937; margin: 5px 0;'>
        
        **Erro ao conectar no Outlook**  
        <span style='font-size: 12px; color: #9ca3af;'>Visualizações: 98 | Atualizado: 28/05/2026</span>  
        <hr style='border-color: #1f2937; margin: 5px 0;'>
        
        **VPN não conecta**  
        <span style='font-size: 12px; color: #9ca3af;'>Visualizações: 85 | Atualizado: 27/05/2026</span>
        """, unsafe_allow_html=True)
        st.markdown("<div style='text-align: right;'><a href='#' style='color: #3b82f6; font-size: 13px; text-decoration: none;'>Ver artigos →</a></div>", unsafe_allow_html=True)

    with col_l4_3:
        st.subheader("IA & Automação (Insights)")
        st.info("🤖 A IA identificou padrões nos chamados e sugere ações automáticas para acelerar a resolução.")
        st.markdown("""
        - ✔️ 128 chamados categorizados automaticamente
        - ✔️ 45 soluções sugeridas pela IA
        - ✔️ 32% dos tickets resolvidos com apoio da IA
        """)
        st.markdown("<div style='text-align: right;'><a href='#' style='color: #3b82f6; font-size: 13px; text-decoration: none;'>Ver painel de IA →</a></div>", unsafe_allow_html=True)

else:
    st.title(f"Módulo: {menu_selecionado}")
    st.write(f"Ambiente de gerenciamento e controle dedicado para **{menu_selecionado}** na plataforma LaryMB AI Service.")
