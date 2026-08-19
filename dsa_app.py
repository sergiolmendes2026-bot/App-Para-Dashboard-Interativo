import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="LaryMB AI Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None

if 'show_new_ticket_modal' not in st.session_state:
    st.session_state.show_new_ticket_modal = False

if 'ai_analyzed' not in st.session_state:
    st.session_state.ai_analyzed = False

# Estados específicos para a aba de Incidentes
if 'selected_incident' not in st.session_state:
    st.session_state.selected_incident = None

if 'show_new_incident_modal' not in st.session_state:
    st.session_state.show_new_incident_modal = False

if 'incident_ai_analyzed' not in st.session_state:
    st.session_state.incident_ai_analyzed = False

# ---------------------------------------------------------
# 2. ESTILIZAÇÃO CSS AVANÇADA (UI DESIGN DARK MODE)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    header, footer {
        visibility: hidden;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1322;
        border-right: 1px solid #1e293b;
        padding-top: 10px;
    }
    [data-testid="stSidebar"] div.row-widget.stRadio > div {
        gap: 2px;
    }
    [data-testid="stSidebar"] div.row-widget.stRadio label {
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
        font-size: 13px;
        transition: all 0.2s ease;
        width: 100%;
        border: 1px solid transparent;
    }
    [data-testid="stSidebar"] div.row-widget.stRadio label:hover {
        background-color: #111827;
        color: #ffffff;
    }
    [data-testid="stSidebar"] div.row-widget.stRadio label:has(input:checked) {
        background: #1d4ed8 !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-icon {
        width: 42px;
        height: 42px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .dashboard-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px;
        height: 100%;
    }
    .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #f3f4f6;
        margin-bottom: 12px;
    }
    .card-footer-link {
        font-size: 11px;
        color: #3b82f6;
        text-align: right;
        margin-top: 8px;
        cursor: pointer;
        font-weight: 500;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SIDEBAR (NAVEGAÇÃO)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0 2px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    🔷
                </div>
                <div>
                    <span style="color: #ffffff; font-size: 15px; font-weight: 700;">LaryMB <span style="color: #a78bfa;">AI</span> Service</span>
                </div>
            </div>
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 4px 8px; border-radius: 6px; color: #94a3b8; font-size: 11px; cursor: pointer;">
                &lt;&lt;
            </div>
        </div>
        <p style="font-size: 10px; color: #64748b; margin: 2px 0 12px 38px; letter-spacing: 0.3px;">
            Intelligent IT Service Management Platform
        </p>
    """, unsafe_allow_html=True)
    
    st.text_input("Buscar no menu...", placeholder="🔍  Buscar no menu...     Ctrl K", label_visibility="collapsed")
    
    opcoes_menu = [
        "📊 Dashboard",
        "🎫 Chamados",
        "🚨 Incidentes",
        "📝 Solicitações",
        "⚠️ Problemas",
        "🔄 Mudanças",
        "📚 Base de Conhecimento",
        "🖥️ Sistemas SaaS",
        "💻 Ativos de TI",
        "🛡️ SLA & Contratos",
        "👥 Usuários",
        "👥 Equipes",
        "📈 Relatórios",
        "✨ IA & Automação",
        "    🔌 Integrações",
        "    🔔 Notificações",
        "    ⚙️ Configurações"
    ]

    menu_selecionado = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background-color: #061e14; border: 1px solid #065f46; padding: 12px; border-radius: 10px; margin-bottom: 12px;">
            <p style="font-size: 9px; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px;">STATUS DA PLATAFORMA</p>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #22c55e;"></span>
                    <span style="font-size: 13px; color: #ffffff; font-weight: 600;">Operacional</span>
                </div>
                <span style="color: #22c55e; font-size: 14px;">📈</span>
            </div>
            <p style="font-size: 10px; color: #64748b; margin-top: 4px;">Todos os sistemas funcionando normalmente</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #1e293b; padding-top: 10px; margin-top: 5px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #2563eb; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">
                    SL
                </div>
                <div>
                    <p style="font-size: 12px; color: #ffffff; font-weight: 600; margin: 0;">Sergio Luiz</p>
                    <p style="font-size: 9px; color: #64748b; margin: 0;">Administrador</p>
                </div>
            </div>
            <span style="color: #94a3b8; cursor: pointer; font-size: 14px;">🚪</span>
        </div>
    """, unsafe_allow_html=True)

aba_activa = menu_selecionado.strip().split(" ", 1)[-1]

# ---------------------------------------------------------
# 4. HEADER DA APLICAÇÃO (BARRA SUPERIOR)
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    sub_map = {
        "Dashboard": "Visão geral dos principais indicadores de TI & Operações",
        "Chamados": "Gerenciamento completo de solicitações, incidentes e suporte de TI",
        "Incidentes": "Monitoramento e gestão avançada de incidentes críticos e interrupções de serviços"
    }
    subtitulo_header = sub_map.get(aba_activa, "Gerenciamento e operação de serviços de TI")
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 18px; color: #94a3b8; cursor: pointer;">☰</span>
            <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">{aba_activa}</h2>
        </div>
        <p style="margin: 2px 0 0 30px; font-size: 11px; color: #64748b;">{subtitulo_header}</p>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px;">
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 6px 12px; border-radius: 6px; font-size: 11px; color: #9ca3af;">
                📅 01/06/2026 - 31/05/2026
            </div>
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 6px 12px; border-radius: 6px; font-size: 11px; color: #9ca3af; cursor: pointer;">
                🌪️ Filtros
            </div>
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 6px 10px; border-radius: 6px; font-size: 12px; color: #9ca3af; position: relative;">
                🔔 <span style="background-color: #ef4444; color: white; font-size: 8px; padding: 1px 4px; border-radius: 10px; position: absolute; top: 2px; right: 2px;">7</span>
            </div>
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 6px 10px; border-radius: 6px; font-size: 12px; color: #9ca3af;">
                🌙
            </div>
            <div style="background-color: #2563eb; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">
                SL
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. ROTEAMENTO DE MÓDULOS
# ---------------------------------------------------------
if aba_activa == "Dashboard":

    # --- LINHA 1: MÉTRICAS PRINCIPAIS ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-icon" style="background-color: #1e3a8a; color: #3b82f6;">📋</div><div><p style="margin: 0; font-size: 10px; color: #9ca3af;">Chamados Abertos</p><h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">128</h3><p style="margin: 0; font-size: 10px; color: #3b82f6;">↑ 12 hoje</p></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="metric-icon" style="background-color: #064e3b; color: #10b981;">✅</div><div><p style="margin: 0; font-size: 10px; color: #9ca3af;">Chamados Resolvidos</p><h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">342</h3><p style="margin: 0; font-size: 10px; color: #10b981;">↑ 28 hoje</p></div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><div class="metric-icon" style="background-color: #78350f; color: #f59e0b;">🕒</div><div><p style="margin: 0; font-size: 10px; color: #9ca3af;">Em Andamento</p><h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">45</h3><p style="margin: 0; font-size: 10px; color: #f59e0b;">↑ 5 hoje</p></div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><div class="metric-icon" style="background-color: #7f1d1d; color: #ef4444;">⚠️</div><div><p style="margin: 0; font-size: 10px; color: #9ca3af;">SLA Fora do Prazo</p><h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">12</h3><p style="margin: 0; font-size: 10px; color: #ef4444;">↓ 3 hoje</p></div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="metric-card"><div class="metric-icon" style="background-color: #4c1d95; color: #a855f7;">⏱️</div><div><p style="margin: 0; font-size: 10px; color: #9ca3af;">MTTR (h)</p><h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">3,2</h3><p style="margin: 0; font-size: 10px; color: #a855f7;">↓ 0,6h</p></div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="metric-card"><div class="metric-icon" style="background-color: #0e7490; color: #06b6d4;">🖥️</div><div><p style="margin: 0; font-size: 10px; color: #9ca3af;">Sistemas Online</p><h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">95%</h3><p style="margin: 0; font-size: 10px; color: #06b6d4;">↑ 2%</p></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LINHA 2: GRÁFICO PRIORIDADE, TABELA RECENTES, INCIDENTES SAAS ---
    col_l2_1, col_l2_2, col_l2_3 = st.columns([1, 1.6, 1])

    with col_l2_1:
        st.markdown('<div class="dashboard-card"><p class="card-title">Chamados Abertos por Prioridade</p>', unsafe_allow_html=True)
        df_prioridade = pd.DataFrame({
            'Prioridade': ['Crítica', 'Alta', 'Média', 'Baixa'],
            'Quantidade': [28, 36, 42, 22]
        })
        fig_donut = px.pie(
            df_prioridade, names='Prioridade', values='Quantidade', hole=0.65,
            color='Prioridade',
            color_discrete_map={'Crítica': '#dc2626', 'Alta': '#ea580c', 'Média': '#facc15', 'Baixa': '#16a34a'}
        )
        fig_donut.update_traces(textinfo='percent', textfont_size=11)
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', height=210, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True, legend=dict(orientation="v", y=0.5, x=1.0, font=dict(size=10))
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('<p style="font-size: 11px; color: #9ca3af; text-align: right; margin: 0;">Total <b style="color: white;">128</b></p></div>', unsafe_allow_html=True)

    with col_l2_2:
        st.markdown('<div class="dashboard-card"><p class="card-title">Chamados Recentes</p>', unsafe_allow_html=True)
        df_recentes = pd.DataFrame({
            'ID': ['#CH-10234', '#CH-10233', '#CH-10232', '#CH-10231', '#CH-10230'],
            'Título': ['Erro ao acessar o ERP', 'Falha na integração com API', 'Impressora sem resposta', 'Solicitação de acesso VPN', 'Tela azul no Windows 11'],
            'Solicitante': ['Ana Souza', 'Carlos Mendes', 'João Ferreira', 'Mariana Lima', 'Pedro Oliveira'],
            'Prioridade': ['Alta', 'Crítica', 'Média', 'Baixa', 'Alta'],
            'Status': ['Em Andamento', 'Em Andamento', 'Novo', 'Novo', 'Em Andamento'],
            'Abertura': ['31/05/2026 10:23', '31/05/2026 09:58', '31/05/2026 09:41', '31/05/2026 09:15', '31/05/2026 08:52']
        })
        st.dataframe(df_recentes, use_container_width=True, hide_index=True, height=210)
        st.markdown('<p class="card-footer-link">Ver todos os chamados →</p></div>', unsafe_allow_html=True)

    with col_l2_3:
        st.markdown('<div class="dashboard-card"><p class="card-title">Incidentes por Sistema SaaS</p>', unsafe_allow_html=True)
        df_saas = pd.DataFrame({'Sistema': ['Microsoft 365', 'Salesforce', 'SAP Business One', 'Totvs Protheus', 'Google Workspace'], 'Incidentes': [24, 18, 15, 10, 8]})
        fig_bar = px.bar(df_saas, x='Incidentes', y='Sistema', orientation='h', text='Incidentes', color_discrete_sequence=['#0ea5e9'])
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', height=210, margin=dict(t=5, b=5, l=5, r=5),
            xaxis=dict(showgrid=False, visible=False), 
            yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="white"))
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('<p class="card-footer-link">Ver todos os sistemas →</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LINHA 3: SLA CUMPRIMENTO, ATENDIMENTOS POR CATEGORIA, EQUIPES, STATUS SAAS ---
    col_l3_1, col_l3_2, col_l3_3, col_l3_4 = st.columns([1, 1, 1.4, 1])

    with col_l3_1:
        st.markdown('<div class="dashboard-card"><p class="card-title">SLA - Cumprimento</p>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 87,
            number = {'suffix': "%", 'font': {'size': 24, 'color': 'white'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#22c55e"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 70], 'color': '#7f1d1d'},
                    {'range': [70, 90], 'color': '#78350f'},
                    {'range': [90, 100], 'color': '#064e3b'}
                ],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', height=140, margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("""
            <div style="font-size: 11px; color: #9ca3af; margin-top: -10px;">
                🟢 Dentro do prazo: <b>312 (87%)</b><br>
                🔴 Fora do prazo: <b>38 (11%)</b><br>
                🟡 Pausado: <b>8 (2%)</b>
            </div>
            <p style="font-size: 11px; color: #9ca3af; text-align: right; margin: 4px 0 0 0;">Total <b style="color: white;">358</b></p>
        </div>""", unsafe_allow_html=True)

    with col_l3_2:
        st.markdown('<div class="dashboard-card"><p class="card-title">Atendimentos por Categoria</p>', unsafe_allow_html=True)
        st.markdown("""
            <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                🔵 <b>Acesso / Permissões</b> &nbsp;&nbsp;&nbsp;&nbsp; 56 (26%)<br>
                🟢 <b>Falhas / Erros</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 48 (22%)<br>
                🟢 <b>Solicitações</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 46 (21%)<br>
                🟣 <b>Hardware</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 24 (11%)<br>
                🟣 <b>Software</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 20 (9%)<br>
                🟠 <b>Outros</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 18 (8%)
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<p class="card-footer-link" style="margin-top: 14px;">Ver todas as categorias →</p></div>', unsafe_allow_html=True)

    with col_l3_3:
        st.markdown('<div class="dashboard-card"><p class="card-title">Atendimentos por Equipe</p>', unsafe_allow_html=True)
        df_equipes = pd.DataFrame({
            'Equipe': ['N1 - Suporte', 'N2 - Especialista', 'Infraestrutura', 'Sistemas'],
            'Abertos': [72, 32, 14, 10],
            'Em Andam.': [28, 12, 5, 4],
            'Resolv.': [152, 98, 56, 36],
            'SLA': ['91%', '85%', '88%', '90%']
        })
        st.dataframe(df_equipes, use_container_width=True, hide_index=True, height=140)
        st.markdown('<p class="card-footer-link" style="margin-top: 4px;">Ver todas as equipes →</p></div>', unsafe_allow_html=True)

    with col_l3_4:
        st.markdown('<div class="dashboard-card"><p class="card-title">Status dos Sistemas SaaS</p>', unsafe_allow_html=True)
        df_status_saas = pd.DataFrame({
            'Status': ['Operacional', 'Atenção', 'Indisponível'],
            'Qtd': [76, 18, 6]
        })
        fig_donut_saas = px.pie(
            df_status_saas, names='Status', values='Qtd', hole=0.65,
            color='Status',
            color_discrete_map={'Operacional': '#16a34a', 'Atenção': '#f59e0b', 'Indisponível': '#dc2626'}
        )
        fig_donut_saas.update_traces(textinfo='none')
        fig_donut_saas.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', height=130, margin=dict(t=5, b=5, l=5, r=5),
            showlegend=False
        )
        st.plotly_chart(fig_donut_saas, use_container_width=True)
        st.markdown("""
            <div style="font-size: 10px; color: #9ca3af; margin-top: -5px;">
                🟢 Operacional: <b>76 (76%)</b> &nbsp;&nbsp;&nbsp;&nbsp; 🟠 Atenção: <b>18 (18%)</b> &nbsp;&nbsp;&nbsp;&nbsp; 🔴 Indisponível: <b>6 (6%)</b>
            </div>
            <p style="font-size: 11px; color: #9ca3af; text-align: right; margin: 2px 0 0 0;">Total <b style="color: white;">100</b></p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LINHA 4: BASE DE CONHECIMENTO E IA & AUTOMAÇÃO ---
    col_l4_1, col_l4_2 = st.columns([1, 1])

    with col_l4_1:
        st.markdown("""
            <div class="dashboard-card">
                <p class="card-title">Base de Conhecimento - Artigos Populares</p>
                <div style="font-size: 12px; color: #e2e8f0; line-height: 2.2;">
                    📄 Como redefinir senha no AD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 👁️ 124 &nbsp; <b>Acessos</b> &nbsp;&nbsp;&nbsp;&nbsp; Atualizado: 29/05/2026<br>
                    📄 Erro ao conectar no Outlook &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 👁️ 98 &nbsp;&nbsp; <b>Microsoft 365</b> &nbsp; Atualizado: 28/05/2026<br>
                    📄 VPN não conecta &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 👁️ 85 &nbsp;&nbsp; <b>Rede</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Atualizado: 27/05/2026
                </div>
                <p class="card-footer-link" style="margin-top: 8px;">Ver todos os artigos →</p>
            </div>
        """, unsafe_allow_html=True)

    with col_l4_2:
        st.markdown("""
            <div class="dashboard-card">
                <p class="card-title">🤖 IA & Automação (Insights)</p>
                <p style="font-size: 11px; color: #94a3b8; margin-bottom: 12px;">A IA identificou padrões nos chamados e sugere ações automáticas para acelerar a resolução.</p>
                <div style="display: flex; gap: 10px; justify-content: space-between;">
                    <div style="background-color: #0f172a; border: 1px solid #1e293b; padding: 10px; border-radius: 8px; flex: 1; text-align: center;">
                        <p style="font-size: 16px; margin: 0; color: #38bdf8;">🤖</p>
                        <h4 style="margin: 4px 0 2px 0; color: #fff; font-size: 16px;">128</h4>
                        <p style="font-size: 9px; color: #9ca3af; margin: 0;">Chamados categorizados automaticamente</p>
                        <p style="font-size: 9px; color: #22c55e; margin: 2px 0 0 0;">↑ 18% este mês</p>
                    </div>
                    <div style="background-color: #0f172a; border: 1px solid #1e293b; padding: 10px; border-radius: 8px; flex: 1; text-align: center;">
                        <p style="font-size: 16px; margin: 0; color: #a855f7;">💡</p>
                        <h4 style="margin: 4px 0 2px 0; color: #fff; font-size: 16px;">45</h4>
                        <p style="font-size: 9px; color: #9ca3af; margin: 0;">Soluções sugeridas pela IA</p>
                        <p style="font-size: 9px; color: #22c55e; margin: 2px 0 0 0;">↑ 21% este mês</p>
                    </div>
                    <div style="background-color: #0f172a; border: 1px solid #1e293b; padding: 10px; border-radius: 8px; flex: 1; text-align: center;">
                        <p style="font-size: 16px; margin: 0; color: #10b981;">⚡</p>
                        <h4 style="margin: 4px 0 2px 0; color: #fff; font-size: 16px;">32%</h4>
                        <p style="font-size: 9px; color: #9ca3af; margin: 0;">Dos tickets resolvidos com apoio da IA</p>
                        <p style="font-size: 9px; color: #22c55e; margin: 2px 0 0 0;">↑ 12% este mês</p>
                    </div>
                </div>
                <p class="card-footer-link" style="margin-top: 8px;">Ver painel de IA →</p>
            </div>
        """, unsafe_allow_html=True)

elif aba_activa == "Chamados":

    # =========================================================
    # 6. MÓDULO DE CHAMADOS ITSM
    # =========================================================
    if st.session_state.selected_ticket:
        t_id = st.session_state.selected_ticket
        
        if st.button("← Voltar para a lista de chamados"):
            st.session_state.selected_ticket = None
            st.rerun()

        st.markdown(f"""
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 10px; margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #ffffff;">🎫 {t_id} — Erro ao acessar ERP</h3>
                    </div>
                    <div>
                        <span style="background-color: #7f1d1d; color: #f87171; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold;">🔴 Alta Prioridade</span>
                    </div>
                </div>
                <div style="display: flex; gap: 20px; margin-top: 15px; font-size: 13px; color: #9ca3af;">
                    <div>Status: <b style="color: #ffffff;">Em atendimento</b></div>
                    <div>SLA Restante: <b style="color: #38bdf8;">01:42 restante</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_det1, col_det2, col_det3, col_det4 = st.columns(4)
        with col_det1:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">👤 Solicitante</p><p style="font-size: 14px; color: #ffffff; font-weight: 600; margin: 4px 0 0 0;">Ana Souza</p></div>', unsafe_allow_html=True)
        with col_det2:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">🖥️ Sistema</p><p style="font-size: 14px; color: #ffffff; font-weight: 600; margin: 4px 0 0 0;">SAP</p></div>', unsafe_allow_html=True)
        with col_det3:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">📂 Categoria</p><p style="font-size: 14px; color: #ffffff; font-weight: 600; margin: 4px 0 0 0;">Acesso / Permissões</p></div>', unsafe_allow_html=True)
        with col_det4:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">👨‍💻 Responsável</p><p style="font-size: 14px; color: #ffffff; font-weight: 600; margin: 4px 0 0 0;">Carlos Mendes</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_desc, tab_coment, tab_anexos, tab_hist, tab_ia, tab_rag = st.tabs(["📝 Descrição", "💬 Comentários", "📎 Anexos", "🕐 Histórico", "🤖 Análise da IA", "🔎 RAG & Base de Conhecimento"])

        with tab_desc:
            st.markdown("#### Descrição Detalhada do Problema")
            st.info("Usuária informa que não consegue acessar o sistema ERP desde esta manhã. Apresenta erro de timeout e credenciais rejeitadas ao tentar realizar o login corporativo.")

        with tab_coment:
            st.markdown("#### Interações & Comentários")
            st.text_area("Adicionar novo comentário...", placeholder="Escreva uma nota ou resposta ao solicitante...")
            if st.button("Enviar Comentário"):
                st.success("Comentário adicionado com sucesso!")

        with tab_anexos:
            st.markdown("#### Arquivos Anexados")
            st.file_uploader("Enviar anexo", type=['png', 'jpg', 'pdf', 'txt'])

        with tab_hist:
            st.markdown("#### Histórico de Atividades")
            st.markdown("- 🟢 **31/05/2026 08:30** — Chamado criado por Ana Souza.\n- 🤖 **31/05/2026 08:31** — IA classificou automaticamente como *Acesso / Permissões*.\n- 👤 **31/05/2026 08:34** — Atribuído para Carlos Mendes.")

        with tab_ia:
            st.markdown('<div style="background-color: #0f172a; border: 1px solid #1e293b; padding: 15px; border-radius: 10px;"><h4 style="color: #a78bfa; margin-top: 0;">🤖 Análise Inteligente de Causa Raiz</h4><p style="font-size: 13px; color: #cbd5e1;">O padrão de erro indica expiração de credenciais no Active Directory sincronizado com o SAP.</p></div>', unsafe_allow_html=True)

        with tab_rag:
            st.markdown("#### 📚 Base de Conhecimento Relacionada (RAG)")
            st.markdown("- 📄 **Artigo #402:** Como redefinir credenciais integradas SAP/AD (Relevância: 94%)\n- 📄 **Artigo #115:** Solução de Erros de Timeout em ERPs Corporativos (Relevância: 88%)")

        st.markdown("<br>", unsafe_allow_html=True)
        
        act_col1, act_col2 = st.columns([1, 4])
        with act_col1:
            if st.button("⬆️ Escalonar para N2", use_container_width=True):
                st.warning("Chamado escalonado para a equipe N2 - Especialista.")
        with act_col2:
            if st.button("✅ Resolver chamado", use_container_width=True):
                st.success("Chamado marcado como resolvido com sucesso!")
                st.session_state.selected_ticket = None
                st.rerun()

    else:
        col_top1, col_top2 = st.columns([2, 2])
        with col_top1:
            pesquisa_chamado = st.text_input("Buscar chamado", placeholder="🔎 Buscar por ID, título ou solicitante...", label_visibility="collapsed")
        with col_top2:
            bc1, bc2, bc3, bc4 = st.columns(4)
            with bc1:
                if st.button("➕ Novo", use_container_width=True):
                    st.session_state.show_new_ticket_modal = not st.session_state.show_new_ticket_modal
            with bc2:
                if st.button("🎛️ Filtros", use_container_width=True):
                    st.toast("Filtros avançados ativados.")
            with bc3:
                if st.button("📥 Exportar", use_container_width=True):
                    st.success("Lista de chamados exportada para CSV com sucesso!")
            with bc4:
                if st.button("🔄 Atualizar", use_container_width=True):
                    st.rerun()

        if st.session_state.show_new_ticket_modal:
            st.markdown('<div style="background-color: #111827; border: 1px solid #3b82f6; padding: 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 20px;"><h3 style="color: #ffffff; margin-top: 0;">➕ Criar Novo Chamado / Incidente com Apoio de IA</h3></div>', unsafe_allow_html=True)
            
            with st.form("form_novo_chamado"):
                f_solicitante = st.text_input("Nome do Solicitante", value="Ana Souza")
                f_descricao = st.text_area("Descreva o problema (A IA preencherá o restante automaticamente)", value="Não consigo acessar o SAP desde esta manhã.")
                
                if st.form_submit_button("🤖 Analisar com IA"):
                    st.session_state.ai_analyzed = True
                    st.success("IA analisou o texto com sucesso!")
                
                if st.session_state.ai_analyzed:
                    st.markdown('<div style="background-color: #0f172a; border: 1px solid #7c3aed; padding: 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 15px;"><h4 style="color: #a78bfa; margin-top: 0;">🤖 Análise Automática da IA</h4>', unsafe_allow_html=True)
                    st.markdown("- **Tipo:** Incidente\n- **Categoria:** Acesso / Permissões\n- **Prioridade sugerida:** Alta\n- **Sistema identificado:** SAP\n- **Artigos relacionados:** 3 artigos na Base de Conhecimento\n- **Equipe sugerida:** N1 - Suporte")
                    if st.form_submit_button("✓ Aceitar classificação da IA"):
                        st.toast("Classificação da IA aplicada com sucesso!")

                f_tipo = st.selectbox("Tipo", ["Incidente", "Solicitação", "Problema", "Dúvida"], index=0)
                f_categoria = st.selectbox("Categoria", ["Acesso / Permissões", "Hardware", "Software", "Rede", "E-mail", "Segurança", "Sistemas SaaS", "Integração", "Infraestrutura", "Outros"], index=0)
                f_prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"], index=2)

                sla_map = {"Crítica": "1 hora", "Alta": "4 horas", "Média": "8 horas", "Baixa": "24 horas"}
                f_sla_calculado = sla_map.get(f_prioridade, "4 horas")
                st.info(f"⏱️ **SLA Definido Automaticamente:** {f_sla_calculado} (com base na prioridade {f_prioridade})")

                f_sistema = st.selectbox("Sistema / Alvo", ["SAP", "Microsoft 365", "Salesforce", "Rede / VPN", "Hardware"], index=0)
                
                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    submit_btn = st.form_submit_button("💾 Salvar Chamado")
                with col_btn2:
                    cancel_btn = st.form_submit_button("❌ Cancelar")
                
                if submit_btn:
                    st.success("Chamado criado com sucesso!")
                    st.session_state.show_new_ticket_modal = False
                    st.session_state.ai_analyzed = False
                    st.rerun()
                if cancel_btn:
                    st.session_state.show_new_ticket_modal = False
                    st.session_state.ai_analyzed = False
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        ic1, ic2, ic3, ic4, ic5, ic6, ic7, ic8 = st.columns(8)
        with ic1: st.metric("Total", "342")
        with ic2: st.metric("Novos", "28")
        with ic3: st.metric("Em Atendimento", "45")
        with ic4: st.metric("Aguardando", "17")
        with ic5: st.metric("Resolvidos", "230")
        with ic6: st.metric("Críticos", "12")
        with ic7: st.metric("SLA Risco", "8")
        with ic8: st.metric("SLA Violado", "5", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("🎛️ Filtros Avançados de Chamados (Status, Prioridade, Categoria, Sistema)"):
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1: st.selectbox("Status", ["Todos", "Novo", "Em triagem", "Em atendimento", "Resolvido"])
            with fc2: st.selectbox("Prioridade", ["Todas", "Baixa", "Média", "Alta", "Crítica"])
            with fc3: st.selectbox("Categoria", ["Todas", "Acesso / Permissões", "Hardware", "Software", "Rede", "Sistemas SaaS"])
            with fc4: st.selectbox("Sistema", ["Todos", "Microsoft 365", "Salesforce", "SAP"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Lista de Chamados Ativos")
        
        chamados_data = [
            {"ID": "#CH-10234", "Título": "Erro ao acessar o ERP", "Solicitante": "Ana Souza", "Tipo": "Incidente", "Prioridade": "🔴 Alta", "Sistema": "SAP", "Responsável": "Carlos", "SLA": "01:42", "Status": "Em atendimento"},
            {"ID": "#CH-10233", "Título": "Falha na integração com API", "Solicitante": "Carlos Mendes", "Tipo": "Incidente", "Prioridade": "🚨 Crítica", "Sistema": "API", "Responsável": "João", "SLA": "00:35", "Status": "Em atendimento"},
            {"ID": "#CH-10232", "Título": "Impressora sem resposta", "Solicitante": "João Ferreira", "Tipo": "Solicitação", "Prioridade": "🟡 Média", "Sistema": "Hardware", "Responsável": "Maria", "SLA": "05:20", "Status": "Novo"},
            {"ID": "#CH-10231", "Título": "Solicitação de acesso VPN", "Solicitante": "Mariana Lima", "Tipo": "Solicitação", "Prioridade": "🟢 Baixa", "Sistema": "Rede", "Responsável": "Pedro", "SLA": "12:00", "Status": "Novo"},
            {"ID": "#CH-10230", "Título": "Tela azul no Windows 11", "Solicitante": "Pedro Oliveira", "Tipo": "Incidente", "Prioridade": "🔴 Alta", "Sistema": "M365", "Responsável": "Carlos", "SLA": "00:15", "Status": "Em atendimento"}
        ]
        
        header_cols = st.columns([1, 2.3, 1.2, 1, 1.1, 1, 1.1, 0.9, 1.2, 0.9])
        header_cols[0].markdown("**ID**")
        header_cols[1].markdown("**Título**")
        header_cols[2].markdown("**Solicitante**")
        header_cols[3].markdown("**Tipo**")
        header_cols[4].markdown("**Prioridade**")
        header_cols[5].markdown("**Sistema**")
        header_cols[6].markdown("**Responsável**")
        header_cols[7].markdown("**SLA**")
        header_cols[8].markdown("**Status**")
        header_cols[9].markdown("**Ação**")
        
        st.markdown("<hr style='margin: 4px 0; border-color: #3b82f6;'>", unsafe_allow_html=True)

        for row in chamados_data:
            if pesquisa_chamado and pesquisa_chamado.lower() not in row['ID'].lower() and pesquisa_chamado.lower() not in row['Título'].lower() and pesquisa_chamado.lower() not in row['Solicitante'].lower():
                continue
            cols = st.columns([1, 2.3, 1.2, 1, 1.1, 1, 1.1, 0.9, 1.2, 0.9])
            cols[0].markdown(f"**{row['ID']}**")
            cols[1].markdown(f"{row['Título']}")
            cols[2].markdown(f"{row['Solicitante']}")
            cols[3].markdown(f"{row['Tipo']}")
            cols[4].markdown(f"{row['Prioridade']}")
            cols[5].markdown(f"{row['Sistema']}")
            cols[6].markdown(f"{row['Responsável']}")
            cols[7].markdown(f"{row['SLA']}")
            cols[8].markdown(f"{row['Status']}")
            if cols[9].button("Abrir", key=f"btn_{row['ID']}"):
                st.session_state.selected_ticket = row['ID']
                st.rerun()
            st.markdown("<hr style='margin: 4px 0; border-color: #1e293b;'>", unsafe_allow_html=True)

elif aba_activa == "Incidentes":

    # =========================================================
    # 7. MÓDULO DE INCIDENTES ITSM (NOVA ESTRUTURA COMPLETA)
    # =========================================================
    if st.session_state.selected_incident:
        inc_id = st.session_state.selected_incident
        
        if st.button("← Voltar para a lista de incidentes"):
            st.session_state.selected_incident = None
            st.rerun()

        # CABEÇALHO DO INCIDENTE DETALHADO
        st.markdown(f"""
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 10px; margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #ffffff;">🚨 {inc_id} — Indisponibilidade do ERP Corporativo</h3>
                    </div>
                    <div>
                        <span style="background-color: #7f1d1d; color: #f87171; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold;">🔴 P1 — Crítica</span>
                    </div>
                </div>
                <div style="display: flex; gap: 20px; margin-top: 15px; font-size: 13px; color: #9ca3af;">
                    <div>Sistema: <b style="color: #ffffff;">SAP</b></div>
                    <div>Serviço: <b style="color: #ffffff;">ERP Financeiro</b></div>
                    <div>Responsável: <b style="color: #38bdf8;">Carlos Mendes</b></div>
                    <div>Equipe: <b style="color: #ffffff;">N2 — Especialistas</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 7. IMPACTO (SEÇÃO DEDICADA)
        st.markdown("#### 📊 Impacto Operacional")
        imp1, imp2, imp3, imp4, imp5 = st.columns(5)
        with imp1:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">👥 Usuários Afetados</p><h3 style="margin: 4px 0 0 0; color: #fff; font-size: 18px;">48</h3></div>', unsafe_allow_html=True)
        with imp2:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">🏢 Departamentos</p><h3 style="margin: 4px 0 0 0; color: #fff; font-size: 18px;">2</h3></div>', unsafe_allow_html=True)
        with imp3:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">🖥️ Sistemas</p><h3 style="margin: 4px 0 0 0; color: #fff; font-size: 18px;">1</h3></div>', unsafe_allow_html=True)
        with imp4:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">📍 Localidades</p><h3 style="margin: 4px 0 0 0; color: #fff; font-size: 18px;">3</h3></div>', unsafe_allow_html=True)
        with imp5:
            st.markdown('<div style="background-color: #111827; border: 1px solid #1f2937; padding: 12px; border-radius: 8px;"><p style="font-size: 11px; color: #9ca3af; margin: 0;">⚡ Disponibilidade</p><h3 style="margin: 4px 0 0 0; color: #ef4444; font-size: 18px;">72%</h3></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ABAS DE INVESTIGAÇÃO DO INCIDENTE
        tab_inv, tab_ia_inc, tab_time, tab_rca, tab_rel = st.tabs([
            "🔍 Investigação & Descrição", 
            "🤖 LaryMB AI (Análise)", 
            "🕐 Timeline", 
            "🧠 Root Cause Analysis (RCA)", 
            "🔗 Chamados Relacionados"
        ])

        with tab_inv:
            st.markdown("#### Descrição do Incidente")
            st.info("Usuários do departamento financeiro não conseguem acessar o ERP desde 09:12. Mensagem de erro genérica de timeout ao tentar autenticar via SSO corporativo.")
            st.markdown("#### Ações Imediatas Realizadas")
            st.markdown("- Verificação de integridade dos nós de gateway do SAP.\n- Acionamento preventivo da equipe de banco de dados.")

        with tab_ia_inc:
            st.markdown("""
                <div style="background-color: #0f172a; border: 1px solid #7c3aed; padding: 20px; border-radius: 10px;">
                    <h4 style="color: #a78bfa; margin-top: 0;">🤖 LaryMB AI — Análise Inteligente</h4>
                    <p style="font-size: 13px; color: #cbd5e1;"><b>Incidente:</b> API indisponível / ERP sem resposta<br>
                    <b>Sistema afetado:</b> API de pagamentos & SAP<br>
                    <b>Impacto identificado:</b> Alto<br>
                    <b>Prioridade sugerida:</b> P1</p>
                    <hr style="border-color: #1e293b;">
                    <p style="font-size: 13px; color: #cbd5e1;"><b>Possível causa:</b> Falha na comunicação entre o serviço de pagamentos e o banco de dados principal.<br>
                    <b>Incidentes semelhantes encontrados:</b> 4 ocorrências no histórico.<br>
                    <b>Artigos da Knowledge Base:</b> 3 artigos recomendados para resolução rápida.</p>
                    <p style="font-size: 13px; color: #38bdf8;"><b>Ação recomendada:</b> Verificar disponibilidade do serviço, logs da API e conexão com o banco.</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_ia_b1, col_ia_b2, col_ia_b3, col_ia_b4 = st.columns(4)
            with col_ia_b1:
                if st.button("⚙️ Executar diagnóstico", use_container_width=True):
                    st.success("Diagnóstico automatizado executado com sucesso!")
            with col_ia_b2:
                if st.button("📚 Ver Knowledge Base", use_container_width=True):
                    st.info("Redirecionando para artigos da base...")
            with col_ia_b3:
                if st.button("🔎 Analisar com RAG", use_container_width=True):
                    st.success("Busca vetorial RAG concluída! 3 diretrizes cruzadas.")
            with col_ia_b4:
                if st.button("⬆️ Escalar para N2", use_container_width=True):
                    st.warning("Escalonado para engenharia avançada de sistemas.")

        with tab_time:
            st.markdown("#### 🕐 Timeline do Incidente")
            st.markdown("""
            - 🔴 **09:12** — Incidente detectado por monitoramento sintético
            - 🤖 **09:15** — IA classificou automaticamente como P1
            - 👨‍💻 **09:18** — Equipe N1 iniciou investigação preliminar
            - ⬆️ **09:30** — Escalonado para N2 (Especialistas SAP)
            - 🔎 **09:42** — Causa provável identificada (expiração de certificado)
            - 🔧 **10:05** — Correção aplicada pelo time de infraestrutura
            - 🧪 **10:20** — Monitoramento ativo iniciado
            - ✅ **10:45** — Serviço normalizado e validado com usuários
            - 📋 **11:00** — Incidente encerrado formalmente
            """)

        with tab_rca:
            st.markdown("#### 🧠 Root Cause Analysis (RCA)")
            st.markdown("""
            - **Causa raiz:** Falha no serviço de autenticação do ERP devido a timeout de conexão síncrona.
            - **Fator contribuinte:** Expiração inesperada de certificado SSL no middleware de integração.
            - **Ação corretiva:** Renovação manual do certificado e reinicialização do pool de conexões.
            - **Ação preventiva:** Criação de alerta automatizado de monitoramento para certificados próximos do vencimento (30 dias antes).
            """)
            st.success("💡 Esta RCA foi gravada na base de conhecimento para alimentar os modelos de IA da LaryMB.")

        with tab_rel:
            st.markdown("#### 🔗 Chamados Relacionados a este Incidente")
            st.markdown("Para evitar o tratamento individualizado de dezenas de chamados, os seguintes tickets estão atrelados centralmente a este incidente (`INC-1024`):")
            df_rels = pd.DataFrame({
                'ID Chamado': ['#CH-10234', '#CH-10235', '#CH-10236', '#CH-10237', '#CH-10238'],
                'Título': ['Erro ao acessar o ERP', 'Falha de login financeiro', 'Tela travada no sistema', 'Erro 504 no ERP', 'Lentidão severa SAP'],
                'Solicitante': ['Ana Souza', 'Carlos Mendes', 'João Ferreira', 'Maria Lima', 'Pedro Oliveira'],
                'Status': ['Vinculado', 'Vinculado', 'Vinculado', 'Vinculado', 'Vinculado']
            })
            st.dataframe(df_rels, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Fechar / Resolver Incidente Definitivemente"):
            st.success("Incidente resolvido com sucesso! A timeline e a RCA foram arquivadas.")
            st.session_state.selected_incident = None
            st.rerun()

    else:
        # 1. INDICADORES NO TOPO (CARDS)
        ic_m1, ic_m2, ic_m3, ic_m4, ic_m5, ic_m6, ic_m7, ic_m8 = st.columns(8)
        with ic_m1:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #1e3a8a; color: #3b82f6; width: 32px; height: 32px; font-size: 14px;">🚨</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Incidentes Abertos</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">18</h3></div></div>', unsafe_allow_html=True)
        with ic_m2:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #7f1d1d; color: #ef4444; width: 32px; height: 32px; font-size: 14px;">🔴</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Críticos</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">3</h3></div></div>', unsafe_allow_html=True)
        with ic_m3:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #78350f; color: #f59e0b; width: 32px; height: 32px; font-size: 14px;">🟠</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Alta Prioridade</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">6</h3></div></div>', unsafe_allow_html=True)
        with ic_m4:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #1e3a8a; color: #38bdf8; width: 32px; height: 32px; font-size: 14px;">🔵</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Em Investigação</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">7</h3></div></div>', unsafe_allow_html=True)
        with ic_m5:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #374151; color: #9ca3af; width: 32px; height: 32px; font-size: 14px;">⏳</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Aguardando</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">4</h3></div></div>', unsafe_allow_html=True)
        with ic_m6:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #064e3b; color: #10b981; width: 32px; height: 32px; font-size: 14px;">✅</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Resolvidos Hoje</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">12</h3></div></div>', unsafe_allow_html=True)
        with ic_m7:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #4c1d95; color: #a855f7; width: 32px; height: 32px; font-size: 14px;">⏱️</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">MTTR</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">3,2 h</h3></div></div>', unsafe_allow_html=True)
        with ic_m8:
            st.markdown('<div class="metric-card" style="padding: 10px;"><div class="metric-icon" style="background-color: #0e7490; color: #06b6d4; width: 32px; height: 32px; font-size: 14px;">🛡️</div><div><p style="margin: 0; font-size: 9px; color: #9ca3af;">Sistemas Impact.</p><h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #fff;">5</h3></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. BOTÕES PRINCIPAIS NO TOPO
        b_top1, b_top2, b_top3, b_top4, b_top5 = st.columns(5)
        with b_top1:
            if st.button("➕ Novo Incidente", use_container_width=True):
                st.session_state.show_new_incident_modal = not st.session_state.show_new_incident_modal
        with b_top2:
            pesquisa_incidente = st.text_input("Pesquisar incidente", placeholder="🔎 Pesquisar...", label_visibility="collapsed")
        with b_top3:
            if st.button("🎛️ Filtros", use_container_width=True):
                st.toast("Painel de filtros de incidentes ativo.")
        with b_top4:
            if st.button("📊 Análise", use_container_width=True):
                st.toast("Relatório analítico de incidentes gerado.")
        with b_top5:
            if st.button("📤 Exportar", use_container_width=True):
                st.success("Relatório de incidentes exportado para CSV com sucesso!")

        # MODAL / FORMULÁRIO DE NOVO INCIDENTE COM IA
        if st.session_state.show_new_incident_modal:
            st.markdown('<div style="background-color: #111827; border: 1px solid #ef4444; padding: 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 20px;"><h3 style="color: #ffffff; margin-top: 0;">➕ Abrir Novo Incidente Crítico com Apoio de IA</h3></div>', unsafe_allow_html=True)
            
            with st.form("form_novo_incidente"):
                inc_titulo = st.text_input("Título / Descrição resumida", value="Indisponibilidade no sistema de faturamento")
                inc_desc = st.text_area("Descrição detalhada do impacto", value="Módulo financeiro inativo para toda a filial São Paulo.")
                
                if st.form_submit_button("🤖 Analisar Incidente com IA"):
                    st.session_state.incident_ai_analyzed = True
                    st.success("IA analisou o incidente com sucesso!")
                
                if st.session_state.incident_ai_analyzed:
                    st.markdown('<div style="background-color: #0f172a; border: 1px solid #7c3aed; padding: 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 15px;"><h4 style="color: #a78bfa; margin-top: 0;">🤖 Diagnóstico Preliminar da IA</h4>', unsafe_allow_html=True)
                    st.markdown("- **Impacto sugerido:** Alto\n- **Urgência sugerida:** Alta\n- **Prioridade sugerida:** P1 — Crítica\n- **Sistema afetado:** SAP\n- **Equipe recomendada:** N2 — Especialistas")
                    if st.form_submit_button("✓ Aplicar Recomendações da IA"):
                        st.toast("Parâmetros aplicados com sucesso!")

                inc_sistema = st.selectbox("Sistema Afetado", ["Microsoft 365", "SAP", "Salesforce", "Google Workspace", "VPN", "ERP", "API", "Infraestrutura", "Outros"], index=1)
                inc_impacto = st.selectbox("Impacto", ["Usuário", "Departamento", "Unidade", "Empresa", "Organização inteira"], index=3)
                inc_urgencia = st.selectbox("Urgência", ["Baixa", "Média", "Alta", "Crítica"], index=3)
                inc_prioridade = st.selectbox("Prioridade", ["P4 — Baixa", "P3 — Média", "P2 — Alta", "P1 — Crítica"], index=3)
                
                col_ibtn1, col_ibtn2 = st.columns([1, 5])
                with col_ibtn1:
                    isubmit = st.form_submit_button("💾 Salvar Incidente")
                with col_ibtn2:
                    icancel = st.form_submit_button("❌ Cancelar")
                
                if isubmit:
                    st.success("Incidente registrado com sucesso e notificação enviada ao plantão de TI!")
                    st.session_state.show_new_incident_modal = False
                    st.session_state.incident_ai_analyzed = False
                    st.rerun()
                if icancel:
                    st.session_state.show_new_incident_modal = False
                    st.session_state.incident_ai_analyzed = False
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. FILTROS AVANÇADOS
        with st.expander("🎛️ Filtros Avançados de Incidentes (Status, Impacto, Urgência, Prioridade, Sistema)"):
            fi1, fi2, fi3, fi4, fi5 = st.columns(5)
            with fi1: st.selectbox("Status", ["Todos", "Novo", "Investigando", "Identificado", "Em resolução", "Monitoramento", "Resolvido", "Fechado"])
            with fi2: st.selectbox("Impacto", ["Todos", "Usuário", "Departamento", "Unidade", "Empresa", "Organização inteira"])
            with fi3: st.selectbox("Urgência", ["Todas", "Baixa", "Média", "Alta", "Crítica"])
            with fi4: st.selectbox("Prioridade", ["Todas", "P1 — Crítica", "P2 — Alta", "P3 — Média", "P4 — Baixa"])
            with fi5: st.selectbox("Sistema", ["Todos", "Microsoft 365", "SAP", "Salesforce", "Google Workspace", "VPN", "ERP", "API", "Infraestrutura"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Lista de Incidentes Ativos")

        # 4. TABELA PRINCIPAL DE INCIDENTES
        incidentes_data = [
            {"ID": "INC-1024", "Título": "Indisponibilidade do ERP", "Sistema": "SAP", "Impacto": "Alto", "Prioridade": "🔴 P1", "Status": "Investigando", "Responsável": "Carlos", "Início": "09:12", "MTTR": "2h"},
            {"ID": "INC-1023", "Título": "Falha de autenticação", "Sistema": "Microsoft 365", "Impacto": "Médio", "Prioridade": "🟠 P2", "Status": "Em resolução", "Responsável": "João", "Início": "10:30", "MTTR": "1h"},
            {"ID": "INC-1022", "Título": "API indisponível", "Sistema": "Integração", "Impacto": "Alto", "Prioridade": "🔴 P1", "Status": "Monitoramento", "Responsável": "Maria", "Início": "08:45", "MTTR": "3h"},
            {"ID": "INC-1021", "Título": "VPN instável", "Sistema": "VPN", "Impacto": "Médio", "Prioridade": "🟡 P3", "Status": "Resolvido", "Responsável": "Pedro", "Início": "07:20", "MTTR": "1,5h"}
        ]

        h_cols = st.columns([1, 2.2, 1.2, 1, 1, 1.2, 1, 0.9, 0.9, 1.8])
        h_cols[0].markdown("**ID**")
        h_cols[1].markdown("**Incidente**")
        h_cols[2].markdown("**Sistema**")
        h_cols[3].markdown("**Impacto**")
        h_cols[4].markdown("**Prioridade**")
        h_cols[5].markdown("**Status**")
        h_cols[6].markdown("**Resp.**")
        h_cols[7].markdown("**Início**")
        h_cols[8].markdown("**MTTR**")
        h_cols[9].markdown("**Ações**")

        st.markdown("<hr style='margin: 4px 0; border-color: #ef4444;'>", unsafe_allow_html=True)

        for inc in incidentes_data:
            if pesquisa_incidente and pesquisa_incidente.lower() not in inc['ID'].lower() and pesquisa_incidente.lower() not in inc['Título'].lower():
                continue
            cols = st.columns([1, 2.2, 1.2, 1, 1, 1.2, 1, 0.9, 0.9, 1.8])
            cols[0].markdown(f"**{inc['ID']}**")
            cols[1].markdown(f"{inc['Título']}")
            cols[2].markdown(f"{inc['Sistema']}")
            cols[3].markdown(f"{inc['Impacto']}")
            cols[4].markdown(f"{inc['Prioridade']}")
            cols[5].markdown(f"{inc['Status']}")
            cols[6].markdown(f"{inc['Responsável']}")
            cols[7].markdown(f"{inc['Início']}")
            cols[8].markdown(f"{inc['MTTR']}")
            
            # Botões de Ação na Tabela (Abrir | Editar | IA | Escalar)
            btn_col1, btn_col2, btn_col3, btn_col4 = cols[9].columns(4)
            with btn_col1:
                if st.button("👁️", key=f"abrir_{inc['ID']}", help="Abrir Investigação"):
                    st.session_state.selected_incident = inc['ID']
                    st.rerun()
            with btn_col2:
                if st.button("✏️", key=f"edit_{inc['ID']}", help="Editar"):
                    st.toast(f"Editando {inc['ID']}")
            with btn_col3:
                if st.button("🤖", key=f"ia_{inc['ID']}", help="Análise de IA"):
                    st.success(f"IA gerou insights para {inc['ID']}")
            with btn_col4:
                if st.button("⬆️", key=f"esc_{inc['ID']}", help="Escalar"):
                    st.warning(f"{inc['ID']} escalado para N3.")

            st.markdown("<hr style='margin: 4px 0; border-color: #1e293b;'>", unsafe_allow_html=True)

else:
    st.title(f"🛠️ Módulo: {aba_activa}")
    st.info(f"Ambiente operacional configurado para a seção **{aba_activa}** na plataforma LaryMB AI Service.")
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.text_input(f"Pesquisar registros em {aba_activa}...")
    with col_b:
        st.success("Cluster principal de microsserviços sincronizado.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    df_placeholder = pd.DataFrame({
        'ID_Registro': [f"#ID-90{i}" for i in range(1, 6)],
        'Item/Módulo': [f"Parâmetro de {aba_activa} #{i}" for i in range(1, 6)],
        'Status Atual': ['Ativo', 'Processando', 'Sincronizado', 'Otimizado', 'Aguardando'],
        'Responsável': ['Sergio Luiz', 'IA LaryMB', 'Equipe TI', 'Admin Core', 'Suporte N2'],
        'Última Modificação': ['18/08/2026 10:25', '18/08/2026 09:12', '18/08/2026 08:40', '18/08/2026 07:15', '18/08/2026 06:00']
    })
    st.dataframe(df_placeholder, use_container_width=True, hide_index=True)
