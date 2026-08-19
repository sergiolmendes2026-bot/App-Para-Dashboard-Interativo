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

# Estilização CSS Avançada para replicar exatamente o layout da imagem na Sidebar
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px string #1e293b;
        padding-top: 10px;
    }
    /* Estilização dos títulos de seção na sidebar */
    .sidebar-section-title {
        font-size: 10px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin: 18px 0 8px 10px;
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
# MENU LATERAL (SIDEBAR EXATA CONFORME MODELO)
# ---------------------------------------------------------
with st.sidebar:
    # 1. Logo e Identidade
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 5px 0 2px 0;">
            <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                🔷
            </div>
            <div>
                <span style="color: #ffffff; font-size: 16px; font-weight: 700;">LaryMB <span style="color: #a78bfa;">AI</span> Service</span>
            </div>
        </div>
        <p style="font-size: 10px; color: #64748b; margin: 0 0 15px 38px; letter-spacing: 0.3px;">
            Intelligent IT Service Management Platform
        </p>
    """, unsafe_allow_html=True)
    
    # 2. Barra de Pesquisa no Menu
    st.text_input("Buscar no menu...", placeholder="Buscar no menu... ⌘K", label_visibility="collapsed")
    
    # 3. Seção: NAVEGAÇÃO PRINCIPAL
    st.markdown('<p class="sidebar-section-title">Navegação Principal</p>', unsafe_allow_html=True)
    menu_principal = st.radio(
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
            "🛡️ SLA & Contratos"
        ],
        label_visibility="collapsed",
        key="nav_principal"
    )
    
    # 4. Seção: GESTÃO
    st.markdown('<p class="sidebar-section-title">Gestão</p>', unsafe_allow_html=True)
    menu_gestao = st.radio(
        "Gestão",
        [
            "👥 Usuários",
            "👥 Equipes",
            "📈 Relatórios"
        ],
        label_visibility="collapsed",
        key="nav_gestao"
    )
    
    # 5. Seção: IA & AUTOMAÇÃO
    st.markdown('<p class="sidebar-section-title">IA & Automação</p>', unsafe_allow_html=True)
    menu_ia = st.radio(
        "IA e Automação",
        [
            "✨ IA & Automação",
            "    🔌 Integrações",
            "    🔔 Notificações",
            "    ⚙️ Configurações"
        ],
        label_visibility="collapsed",
        key="nav_ia"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6. Card: Status da Plataforma (Exatamente como na imagem)
    st.markdown("""
        <div style="background-color: #0f172a; border: 1px solid #1e3a8a; padding: 12px; border-radius: 10px; margin-bottom: 15px;">
            <p style="font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px;">Status da Plataforma</p>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block;"></span>
                    <span style="font-size: 13px; color: #ffffff; font-weight: 600;">Operacional</span>
                </div>
                <span style="color: #22c55e; font-size: 14px;">📈</span>
            </div>
            <p style="font-size: 10px; color: #64748b; margin-top: 4px;">Todos os sistemas funcionando normalmente</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 7. Rodapé do Usuário
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #1e293b; padding-top: 12px; margin-top: 5px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #3b82f6; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">
                    SL
                </div>
                <div>
                    <p style="font-size: 13px; color: #ffffff; font-weight: 600; margin: 0;">Sergio Luiz</p>
                    <p style="font-size: 10px; color: #64748b; margin: 0;">Administrador</p>
                </div>
            </div>
            <span style="color: #94a3b8; cursor: pointer; font-size: 16px;">🚪</span>
        </div>
    """, unsafe_allow_html=True)

# Captura qual aba foi selecionada (priorizando a navegação principal ou submenus)
menu_ativo = menu_principal if menu_principal else menu_gestao

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL: DASHBOARD DE TI (PRESERVADO INTACTO)
# ---------------------------------------------------------
if "Dashboard" in menu_ativo:
    
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
    st.title(f"Módulo Selecionado")
    st.write("Ambiente de gerenciamento e controle integrado ao ecossistema LaryMB AI Service.")
