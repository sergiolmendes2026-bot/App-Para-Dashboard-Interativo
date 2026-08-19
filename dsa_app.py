import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="LaryMB AI Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Avançada (Transforma os radio buttons em um menu SaaS moderno)
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
        padding-top: 10px;
    }
    /* Esconde os radio buttons nativos e transforma em menu profissional */
    [data-testid="stSidebar"] .row-widget.stRadio > div {
        gap: 4px;
    }
    [data-testid="stSidebar"] .row-widget.stRadio label {
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        width: 100%;
    }
    [data-testid="stSidebar"] .row-widget.stRadio label:hover {
        background-color: #1e293b;
        color: #ffffff;
    }
    /* Estilo do item selecionado */
    [data-testid="stSidebar"] .row-widget.stRadio input:checked + div p {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .row-widget.stRadio label:has(input:checked) {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #3b82f6;
    }
    div.stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MENU LATERAL (SIDEBAR PROFISSIONAL)
# ---------------------------------------------------------
with st.sidebar:
    # Logo e Identidade
    st.markdown("""
        <div style="padding: 5px 0 15px 0;">
            <h3 style="color: #ffffff; margin: 0; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                🤖 LaryMB AI Service
            </h3>
            <p style="font-size: 11px; color: #64748b; margin: 4px 0 0 0; letter-spacing: 0.5px;">
                Intelligent IT Service Management
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #1e293b; margin: 5px 0 15px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; letter-spacing: 1px; padding-left: 4px;'>Navegação Principal</p>", unsafe_allow_html=True)

    # Opções do Menu com Ícones Embutidos
    menu_selecionado = st.radio(
        "Navegação Principal",
        [
            "📊 Dashboard",
            "🎫 Chamados",
            "🚨 Incidentes",
            "📝 Solicitações",
            "⚠️ Problemas",
            "🔄 Mudanças",
            "📚 Base de Conhecimento",
            "🖥️ Sistemas SaaS",
            "💻 Ativos de TI",
            "⏱️ SLA & Contratos",
            "👥 Usuários",
            "👥 Equipes",
            "📈 Relatórios",
            "🤖 IA & Automação",
            "🔌 Integrações",
            "🔔 Notificações",
            "⚙️ Configurações"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border-color: #1e293b; margin: 20px 0 15px 0;'>", unsafe_allow_html=True)
    
    # Rodapé da Sidebar (Status)
    st.markdown("""
        <div style="padding: 8px 4px;">
            <p style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 6px;">Status da Plataforma</p>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block;"></span>
                <span style="font-size: 13px; color: #e2e8f0; font-weight: 500;">Operacional</span>
            </div>
            <p style="font-size: 10px; color: #475569; margin-top: 8px;">Versão 1.0.0</p>
        </div>
    """, unsafe_allow_html=True)

# Remove os emojis do nome da string selecionada para tratar a lógica das telas limpas
menu_limpo = menu_selecionado.split(" ", 1)[1] if " " in menu_selecionado else menu_selecionado

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL: DASHBOARD DE TI
# ---------------------------------------------------------
if menu_limpo == "Dashboard":
    
    col_title, col_user = st.columns([4, 1])
    with col_title:
        st.title("📊 Dashboard")
    with col_user:
        st.markdown("<div style='text-align: right; padding-top: 10px;'><b>Sergio Luiz</b><br><span style='font-size: 11px; color: #9ca3af;'>Administrador</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Linha 1: Métricas
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

    # Linha 2
    col_l2_1, col_l2_2 = st.columns([1, 1.8])
    
    with col_l2_1:
        st.subheader("Chamados Abertos por Prioridade")
        df_prioridade = pd.DataFrame({
            'Prioridade': ['Crítica', 'Alta', 'Média', 'Baixa'],
            'Quantidade': [38, 36, 42, 22]
        })
        fig_donut = px.pie(
            df_prioridade, names='Prioridade', values='Quantidade', hole=0.6,
            color='Prioridade',
            color_discrete_map={'Crítica': '#dc2626', 'Alta': '#ea580c', 'Média': '#facc15', 'Baixa': '#16a34a'}
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="v", y=0.5, x=1.0)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

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

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 3
    col_l3_1, col_l3_2, col_l3_3 = st.columns([1, 1, 1])

    with col_l3_1:
        st.subheader("Incidentes por Sistema SaaS")
        df_saas = pd.DataFrame({
            'Sistema': ['Microsoft 365', 'Salesforce', 'SAP Business One', 'Totvs Protheus', 'Google Workspace'],
            'Incidentes': [24, 18, 15, 10, 8]
        })
        fig_bar = px.bar(df_saas, x='Incidentes', y='Sistema', orientation='h', color_discrete_sequence=['#3b82f6'])
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False), yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

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
                'steps': [{'range': [0, 80], 'color': '#ef4444'}, {'range': [80, 100], 'color': '#065f46'}],
            }
        ))
        fig_sla.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=220, margin=dict(t=20, b=10, l=20, r=20))
        st.plotly_chart(fig_sla, use_container_width=True)

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

else:
    st.title(f"Módulo: {menu_limpo}")
    st.write(f"Ambiente de gerenciamento e controle dedicado para **{menu_limpo}** na plataforma LaryMB AI Service.")
