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

# Estados específicos para a aba de Problemas (ITSM)
if 'selected_problem' not in st.session_state:
    st.session_state.selected_problem = "PRB-00125"

if 'show_new_problem_modal' not in st.session_state:
    st.session_state.show_new_problem_modal = False

if 'problemas_df' not in st.session_state:
    st.session_state['problemas_df'] = pd.DataFrame([
        {
            "ID": "PRB-00125",
            "Título": "Falha recorrente de acesso ao SAP",
            "Categoria": "Software",
            "Serviço/Sistema": "SAP",
            "Impacto": "Alto",
            "Prioridade": "Crítica",
            "Status": "Em investigação",
            "Responsável": "Carlos",
            "Grupo": "N2 Sistemas",
            "Incidentes relacionados": 18,
            "Causa raiz": "Não identificada",
            "SLA": "04:32",
            "Data de abertura": "19/08/2026",
            "Descrição": "Usuários relatando quedas intermitentes e lentidão ao tentar autenticar no módulo financeiro do SAP.",
            "Subcategoria": "Autenticação",
            "Ambiente": "Produção",
            "Origem": "Monitoramento",
            "Urgência": "Alta",
            "Criticidade": "Crítica",
            "Problema recorrente": "Sim",
            "Sintomas": "Erro 504 Gateway Timeout e falha de token.",
            "Hipótese": "Sobrecarga no pool de conexões do middleware de autenticação.",
            "Plano de ação": "Ajustar o timeout e reiniciar o serviço de diretório em janela controlada.",
            "Ação corretiva": "Revisão de parâmetros de conexão.",
            "Ação preventiva": "Implementar auto-scale no microsserviço de auth.",
            "Mudança necessária": "CHG-00412",
            "Prazo": "20/08/2026 18:00"
        },
        {
            "ID": "PRB-00126",
            "Título": "Lentidão na impressora central do 3º andar",
            "Categoria": "Hardware",
            "Serviço/Sistema": "Impressão",
            "Impacto": "Baixo",
            "Prioridade": "Baixa",
            "Status": "Novos",
            "Responsável": "Ana",
            "Grupo": "Suporte Local",
            "Incidentes relacionados": 4,
            "Causa raiz": "Não identificada",
            "SLA": "22:15",
            "Data de abertura": "19/08/2026",
            "Descrição": "Fila de impressão travando com arquivos PDF grandes.",
            "Subcategoria": "Rede",
            "Ambiente": "Escritório SP",
            "Origem": "Chamados",
            "Urgência": "Baixa",
            "Criticidade": "Baixa",
            "Problema recorrente": "Não",
            "Sintomas": "Jobs pausados na fila.",
            "Hipótese": "Driver desatualizado.",
            "Plano de ação": "Atualizar driver do servidor de impressão.",
            "Ação corretiva": "Reinstalação do driver universal HP.",
            "Ação preventiva": "Atualização padrão de drivers mensais.",
            "Mudança necessária": "Nenhuma",
            "Prazo": "22/08/2026 12:00"
        }
    ])

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
        "Incidentes": "Monitoramento e gestão avançada de incidentes críticos e interrupções de serviços",
        "Problemas": "Foco em causa raiz, recorrência, prevenção e eliminação definitiva de incidentes"
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

        st.markdown("### 📋 Lista de Chamados")
        df_chamados = pd.DataFrame({
            'ID': ['#CH-10234', '#CH-10233', '#CH-10232', '#CH-10231', '#CH-10230'],
            'Título': ['Erro ao acessar o ERP', 'Falha na integração com API', 'Impressora sem resposta', 'Solicitação de acesso VPN', 'Tela azul no Windows 11'],
            'Solicitante': ['Ana Souza', 'Carlos Mendes', 'João Ferreira', 'Mariana Lima', 'Pedro Oliveira'],
            'Prioridade': ['Alta', 'Crítica', 'Média', 'Baixa', 'Alta'],
            'Status': ['Em Andamento', 'Em Andamento', 'Novo', 'Novo', 'Em Andamento'],
            'Abertura': ['31/05/2026 10:23', '31/05/2026 09:58', '31/05/2026 09:41', '31/05/2026 09:15', '31/05/2026 08:52']
        })
        
        for index, row in df_chamados.iterrows():
            cols = st.columns([1, 2.5, 1.5, 1, 1.2, 1.2, 0.8])
            with cols[0]: st.write(row['ID'])
            with cols[1]: st.write(row['Título'])
            with cols[2]: st.write(row['Solicitante'])
            with cols[3]: st.write(row['Prioridade'])
            with cols[4]: st.write(row['Status'])
            with cols[5]: st.write(row['Abertura'])
            with cols[6]:
                if st.button("Abrir", key=f"btn_ticket_{row['ID']}"):
                    st.session_state.selected_ticket = row['ID']
                    st.rerun()
            st.markdown("<hr style='margin:5px 0;opacity:0.2;'>", unsafe_allow_html=True)

elif aba_activa == "Incidentes":
    st.title("🚨 Gestão de Incidentes")
    st.write("Monitoramento e gestão avançada de incidentes críticos e interrupções de serviços.")

elif aba_activa == "Problemas":
    st.title("🛠️ Gestão de Problemas (ITSM)")
    st.markdown("Foco em causa raiz, recorrência, prevenção e eliminação definitiva de incidentes.")
    st.markdown("---")

    # 1. INDICADORES NO TOPO
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1: st.metric("Total", "156")
    with col2: st.metric("Novos", "12")
    with col3: st.metric("Investigação", "18")
    with col4: st.metric("Tratamento", "9")
    with col5: st.metric("Resolvidos", "108")
    with col6: st.metric("Críticos", "5")
    with col7: st.metric("Recorrentes", "14")
    with col8: st.metric("Erros Conhecidos", "7")

    st.markdown("---")

    # AÇÕES DO TOPO (NOVO PROBLEMA)
    col_btn1, col_btn2 = st.columns([8, 2])
    with col_btn2:
        if st.button("➕ Criar Novo Problema", use_container_width=True):
            st.session_state['show_new_problem_modal'] = not st.session_state['show_new_problem_modal']

    # MODAL / FORMULÁRIO DE CRIAÇÃO DE NOVO PROBLEMA
    if st.session_state['show_new_problem_modal']:
        with st.expander("📋 Formulário de Abertura de Novo Problema", expanded=True):
            with st.form("form_novo_problema"):
                st.subheader("1. Identificação")
                f_titulo = st.text_input("Título do problema")
                f_desc = st.text_area("Descrição")
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    f_cat = st.selectbox("Categoria", ["Software", "Hardware", "Rede", "Segurança"])
                    f_serv = st.text_input("Serviço/Sistema afetado")
                with col_f2:
                    f_subcat = st.text_input("Subcategoria")
                    f_amb = st.selectbox("Ambiente", ["Produção", "Homologação", "Desenvolvimento"])
                with col_f3:
                    f_origem = st.selectbox("Origem", ["Monitoramento", "Chamados", "Auditoria", "Proativo"])

                st.subheader("2. Classificação")
                col_f4, col_f5, col_f6, col_f7 = st.columns(4)
                with col_f4:
                    f_imp = st.selectbox("Impacto", ["Baixo", "Médio", "Alto", "Crítico"])
                with col_f5:
                    f_urg = st.selectbox("Urgência", ["Baixa", "Média", "Alta"])
                with col_f6:
                    f_prio = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"])
                with col_f7:
                    f_recorrente = st.selectbox("Problema recorrente?", ["Não", "Sim"])

                st.subheader("3. Investigação")
                col_f8, col_f9 = st.columns(2)
                with col_f8:
                    f_resp = st.text_input("Analista responsável")
                    f_sintomas = st.text_area("Sintomas")
                with col_f9:
                    f_grupo = st.text_input("Grupo responsável")
                    f_inc_rel = st.number_input("Incidentes relacionados (Qtd)", min_value=1, value=1)
                
                f_evid = st.file_uploader("Evidências / Logs / Anexos", accept_multiple_files=True)
                f_hipotese = st.text_area("Hipótese da causa")

                submit_prob = st.form_submit_button("Salvar Problema")
                if submit_prob and f_titulo:
                    novo_registro = {
                        "ID": f"PRB-00{len(st.session_state['problemas_df']) + 127}",
                        "Título": f_titulo,
                        "Categoria": f_cat,
                        "Serviço/Sistema": f_serv,
                        "Impacto": f_imp,
                        "Prioridade": f_prio,
                        "Status": "Novos",
                        "Responsável": f_resp,
                        "Grupo": f_grupo,
                        "Incidentes relacionados": f_inc_rel,
                        "Causa raiz": "Não identificada",
                        "SLA": "08:00",
                        "Data de abertura": datetime.now().strftime("%d/%m/%Y"),
                        "Descrição": f_desc,
                        "Subcategoria": f_subcat,
                        "Ambiente": f_amb,
                        "Origem": f_origem,
                        "Urgência": f_urg,
                        "Criticidade": f_prio,
                        "Problema recorrente": f_recorrente,
                        "Sintomas": f_sintomas,
                        "Hipótese": f_hipotese,
                        "Plano de ação": "Pendente",
                        "Ação corretiva": "Pendente",
                        "Ação preventiva": "Pendente",
                        "Mudança necessária": "Nenhuma",
                        "Prazo": (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state['problemas_df'] = pd.concat([st.session_state['problemas_df'], pd.DataFrame([novo_registro])], ignore_index=True)
                    st.success("Problema cadastrado com sucesso!")
                    st.session_state['show_new_problem_modal'] = False
                    st.rerun()

    st.markdown("### 📋 Lista de Problemas")

    # 2. TABELA PRINCIPAL DE PROBLEMAS
    df_exibicao = st.session_state['problemas_df'][[
        "ID", "Título", "Categoria", "Serviço/Sistema", "Impacto", 
        "Prioridade", "Status", "Responsável", "Incidentes relacionados", 
        "Causa raiz", "SLA", "Data de abertura"
    ]].copy()

    for index, row in df_exibicao.iterrows():
        cols = st.columns([1, 2.5, 1, 1, 1, 1, 1.2, 1, 1, 1, 1, 1, 1])
        with cols[0]: st.write(row["ID"])
        with cols[1]: st.write(row["Título"])
        with cols[2]: st.write(row["Categoria"])
        with cols[3]: st.write(row["Serviço/Sistema"])
        with cols[4]: st.write(row["Impacto"])
        with cols[5]: st.write(row["Prioridade"])
        with cols[6]: st.write(row["Status"])
        with cols[7]: st.write(row["Responsável"])
        with cols[8]: st.write(str(row["Incidentes relacionados"]))
        with cols[9]: st.write(row["Causa raiz"])
        with cols[10]: st.write(row["SLA"])
        with cols[11]: st.write(row["Data de abertura"])
        with cols[12]:
            if st.button("Abrir", key=f"btn_abrir_prob_{row['ID']}"):
                st.session_state['selected_problem'] = row["ID"]
                st.rerun()
        st.markdown("<hr style='margin:5px 0;opacity:0.2;'>", unsafe_allow_html=True)

    st.markdown("---")

    # 6. DETALHE DO PROBLEMA (SELECIONADO)
    prob_atual_id = st.session_state['selected_problem']
    prob_dados = st.session_state['problemas_df'][st.session_state['problemas_df']['ID'] == prob_atual_id]

    if not prob_dados.empty:
        p_row = prob_dados.iloc[0]
        st.markdown(f"## Detalhes do Problema: {p_row['ID']} — {p_row['Título']}")
        
        aba_resumo, aba_inc, aba_inv, aba_causa, aba_plano, aba_mudancas, aba_hist, aba_conhec = st.tabs([
            "Resumo", "Incidentes", "Investigação", "Causa Raiz", "Plano de Ação", "Mudanças", "Histórico", "Conhecimento"
        ])

        with aba_resumo:
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.info(f"**Categoria:** {p_row['Categoria']} / {p_row['Subcategoria']}")
                st.info(f"**Serviço:** {p_row['Serviço/Sistema']}")
            with col_r2:
                st.warning(f"**Impacto:** {p_row['Impacto']} | **Prioridade:** {p_row['Prioridade']}")
                st.warning(f"**Status:** {p_row['Status']}")
            with col_r3:
                st.success(f"**Responsável:** {p_row['Responsável']} ({p_row['Grupo']})")
                st.success(f"**Incidentes Vinculados:** {p_row['Incidentes relacionados']}")
            
            st.markdown("### Descrição Completa")
            st.write(p_row['Descrição'])

        with aba_inc:
            st.markdown("### 🔗 Relação entre Chamados e Problemas")
            st.markdown(f"**1 Problema → {p_row['Incidentes relacionados']} Incidentes Relacionados**")
            st.markdown("Quando a causa raiz for corrigida, você conseguirá acompanhar quantos chamados deixaram de ocorrer.")
            
            chamados_ficticios = pd.DataFrame({
                "ID Chamado": ["CH-10234", "CH-10228", "CH-10217", "CH-10198", "CH-10175"],
                "Usuário": ["Mariana Souza", "Roberto Dias", "Fernanda Lima", "João Pedro", "Camila Rocha"],
                "Abertura": ["19/08/2026 09:12", "19/08/2026 08:45", "19/08/2026 08:30", "18/08/2026 17:20", "18/08/2026 16:10"],
                "Status do Chamado": ["Em atendimento", "Fechado", "Fechado", "Fechado", "Fechado"]
            })
            st.dataframe(chamados_ficticios, use_container_width=True)

        with aba_inv:
            st.markdown("### 🔍 Investigação e Apoio de IA")
            
            with st.container(border=True):
                st.markdown("#### ✨ Apoio de IA — Análise Inteligente de Causa Raiz")
                st.write("A IA analisa o histórico de incidentes relacionados para sugerir diagnósticos e padrões.")
                
                if st.button("✨ Analisar Problema com IA", key="btn_ia_analise_prob"):
                    with st.spinner("Analisando padrões e logs correlacionados..."):
                        st.markdown("""
                        > **Resultado da Análise IA:**
                        > * **Possível causa raiz:** Falha recorrente no serviço de autenticação SAP (Timeout no token OAuth).
                        > * **Confiança:** `87%`
                        > * **Incidentes relacionados:** `18` chamados mapeados.
                        > * **Padrão identificado:** Pico de ocorrências concentrado entre 08h e 10h (horário de pico de login).
                        > * **Recomendação:** Verificar o pool de conexões do middleware de autenticação e os logs do servidor de diretório.
                        """)
                        col_ia1, col_ia2 = st.columns(2)
                        with col_ia1:
                            if st.button("✅ [Aceitar análise]"):
                                st.success("Análise incorporada ao registro do problema com sucesso!")
                        with col_ia2:
                            if st.button("🔄 [Reanalisar]"):
                                st.info("Solicitando nova varredura profunda de logs...")

            st.markdown("#### Dados Atuais da Investigação")
            st.text_area("Sintomas relatados", value=p_row['Sintomas'], key="txt_sintomas_p")
            st.text_area("Hipótese levantada", value=p_row['Hipótese'], key="txt_hipotese_p")

        with aba_causa:
            st.markdown("### 🎯 Causa Raiz Oficial")
            st.text_input("Método de análise (Ex: 5 Porquês / Ishikawa)", value="Diagrama de Ishikawa", key="met_analise_p")
            st.text_area("Causa Raiz Definitiva", value=p_row['Causa raiz'], key="causa_raiz_def_p")
            st.text_area("Evidência da causa", value="Logs do gateway indicam esgotamento de threads no pool de autenticação.", key="evid_causa_p")

        with aba_plano:
            st.markdown("### 🛠️ Plano de Ação e Tratamento")
            st.text_area("Plano de Ação", value=p_row['Plano de ação'], key="plano_acao_p")
            col_pa1, col_pa2 = st.columns(2)
            with col_pa1:
                st.text_input("Ação corretiva", value=p_row['Ação corretiva'], key="acao_corr_p")
                st.text_input("Responsável pela ação", value=p_row['Responsável'], key="resp_acao_p")
            with col_pa2:
                st.text_input("Ação preventiva", value=p_row['Ação preventiva'], key="acao_prev_p")
                st.text_input("Prazo limite", value=p_row['Prazo'], key="prazo_lim_p")

        with aba_mudancas:
            st.markdown("### 🔄 Gestão de Mudanças (RFC)")
            st.info(f"Mudança vinculada para correção definitiva: **{p_row['Mudança necessária']}**")
            if st.button("Criar Nova RFC Relacionada", key="btn_nova_rfc_p"):
                st.success("Redirecionando para o módulo de Mudanças (RFC)...")

        with aba_hist:
            st.markdown("### 📜 Histórico de Auditoria e Alterações")
            historico_df = pd.DataFrame({
                "Data/Hora": ["19/08/2026 10:00", "19/08/2026 08:30"],
                "Usuário": ["Carlos (N2)", "Sistema LaryMB AI"],
                "Ação": ["Status alterado para 'Em investigação'", "Problema criado automaticamente via monitoramento"]
            })
            st.dataframe(historico_df, use_container_width=True)

        with aba_conhec:
            st.markdown("### 📚 Base de Conhecimento Relacionada (KEDB)")
            st.success("Artigo sugerido: **KB-00892 - Solução de contorno para falhas de autenticação SAP 504**")
            st.button("Vincular Artigo à Base de Conhecimento", key="btn_vinc_kb_p")

else:
    st.title(f"🤖 LaryMB AI Service — {aba_activa}")
    st.write(f"Você está acessando a aba: **{aba_activa}**")
    st.info("Módulo em fase de expansão. Navegue pelas abas principais como Dashboard, Chamados ou Problemas.")
