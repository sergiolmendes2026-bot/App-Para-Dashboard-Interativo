import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="LaryMB AI Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. ESTILIZAÇÃO CSS AVANÇADA (UI DESIGN DARK MODE)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Fundo Principal da Aplicação */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Remover margins superiores nativas do Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Esconder o Header/Footer nativo do Streamlit */
    header, footer {
        visibility: hidden;
    }

    /* Estilização da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1322;
        border-right: 1px solid #1e293b;
        padding-top: 10px;
    }

    .sidebar-section {
        font-size: 10px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin: 16px 0 6px 4px;
    }

    /* Estilização do Radio Button na Sidebar */
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

    /* Estilo Personalizado dos Cards Nativos / HTML */
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

    /* Customização de Input */
    .stTextInput>div>div>input {
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
    # Header da Sidebar (Logo)
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
    
    # Campo de Busca na Sidebar
    st.text_input("Buscar no menu...", placeholder="🔍  Buscar no menu...     Ctrl K", label_visibility="collapsed")
    
    # Lista de Menu
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

    menu_selecionado = st.radio(
        "Navegação",
        opcoes_menu,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Card: Status da Plataforma
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
    
    # Rodapé do Usuário na Sidebar
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

# Limpa o texto da aba selecionada
aba_activa = menu_selecionado.strip().split(" ", 1)[-1]

# ---------------------------------------------------------
# 4. HEADER DA APLICAÇÃO (BARRA SUPERIOR)
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 18px; color: #94a3b8; cursor: pointer;">☰</span>
            <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">Dashboard</h2>
        </div>
        <p style="margin: 2px 0 0 30px; font-size: 11px; color: #64748b;">Visão geral dos principais indicadores de TI & Operações</p>
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
# 5. CONTEÚDO PRINCIPAL (RENDERIZADO EXATAMENTE IGUAL)
# ---------------------------------------------------------
if "Dashboard" in aba_activa:

    # --- LINHA 1: CARDS DE MÉTRICAS (6 CARDS TOP) ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon" style="background-color: #1e3a8a; color: #3b82f6;">📋</div>
                <div>
                    <p style="margin: 0; font-size: 10px; color: #9ca3af;">Chamados Abertos</p>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">128</h3>
                    <p style="margin: 0; font-size: 10px; color: #3b82f6;">↑ 12 hoje</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon" style="background-color: #064e3b; color: #10b981;">✅</div>
                <div>
                    <p style="margin: 0; font-size: 10px; color: #9ca3af;">Chamados Resolvidos</p>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">342</h3>
                    <p style="margin: 0; font-size: 10px; color: #10b981;">↑ 28 hoje</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon" style="background-color: #78350f; color: #f59e0b;">🕒</div>
                <div>
                    <p style="margin: 0; font-size: 10px; color: #9ca3af;">Em Andamento</p>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">45</h3>
                    <p style="margin: 0; font-size: 10px; color: #f59e0b;">↑ 5 hoje</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon" style="background-color: #7f1d1d; color: #ef4444;">⚠️</div>
                <div>
                    <p style="margin: 0; font-size: 10px; color: #9ca3af;">SLA Fora do Prazo</p>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">12</h3>
                    <p style="margin: 0; font-size: 10px; color: #ef4444;">↓ 3 hoje</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon" style="background-color: #4c1d95; color: #a855f7;">⏱️</div>
                <div>
                    <p style="margin: 0; font-size: 10px; color: #9ca3af;">MTTR (h)</p>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">3,2</h3>
                    <p style="margin: 0; font-size: 10px; color: #a855f7;">↓ 0,6h</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon" style="background-color: #0e7490; color: #06b6d4;">🖥️</div>
                <div>
                    <p style="margin: 0; font-size: 10px; color: #9ca3af;">Sistemas Online</p>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #fff;">95%</h3>
                    <p style="margin: 0; font-size: 10px; color: #06b6d4;">↑ 2%</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LINHA 2: GRÁFICOS E TABELA CENTRAL (3 CARDS) ---
    col_l2_1, col_l2_2, col_l2_3 = st.columns([1, 1.6, 1])

    # Card 1: Chamados Abertos por Prioridade (Donut)
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
            font_color='#ffffff', height=230, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True, legend=dict(orientation="v", y=0.5, x=1.0, font=dict(size=10))
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('<p style="font-size: 11px; color: #9ca3af; text-align: right; margin: 0;">Total <b style="color: white;">128</b></p></div>', unsafe_allow_html=True)

    # Card 2: Chamados Recentes (Tabela)
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
        st.dataframe(df_recentes, use_container_width=True, hide_index=True, height=220)
        st.markdown('<p class="card-footer-link">Ver todos os chamados →</p></div>', unsafe_allow_html=True)

    # Card 3: Incidentes por Sistema SaaS (Barra Horizontal)
    with col_l2_3:
        st.markdown('<div class="dashboard-card"><p class="card-title">Incidentes por Sistema SaaS</p>', unsafe_allow_html=True)
        df_saas = pd.DataFrame({
            'Sistema': ['Microsoft 365', 'Salesforce', 'SAP Business One', 'Totvs Protheus', 'Google Workspace'],
            'Incidentes': [24, 18, 15, 10, 8]
        })
        fig_bar = px.bar(df_saas, x='Incidentes', y='Sistema', orientation='h', text='Incidentes', color_discrete_sequence=['#0ea5e9'])
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', height=220, margin=dict(t=5, b=5, l=5, r=5),
            xaxis=dict(showgrid=False, visible=False), yaxis=dict(autorange="reversed", font=dict(size=10))
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('<p class="card-footer-link">Ver todos os sistemas →</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LINHA 3: SLA, CATEGORIAS, EQUIPES, STATUS SAAS (4 CARDS) ---
    col_l3_1, col_l3_2, col_l3_3, col_l3_4 = st.columns(4)

    # Card SLA Cumprimento
    with col_l3_1:
        st.markdown('<div class="dashboard-card"><p class="card-title">SLA - Cumprimento</p>', unsafe_allow_html=True)
        fig_sla = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 87,
            number = {'suffix': "%", 'font': {'color': 'white', 'size': 26}},
            title = {'text': "Dentro do prazo", 'font': {'size': 10, 'color': '#9ca3af'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "white"},
                'bar': {'color': '#10b981'},
                'bgcolor': "#1f2937",
                'steps': [{'range': [0, 80], 'color': '#ef4444'}, {'range': [80, 100], 'color': '#facc15'}],
            }
        ))
        fig_sla.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=170, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sla, use_container_width=True)
        st.markdown('<p style="font-size: 10px; color: #9ca3af;">🟢 Dentro do prazo: 312 (87%)<br>🔴 Fora do prazo: 38 (11%)<br>⏸️ Pausado: 8 (2%)</p></div>', unsafe_allow_html=True)

    # Card Atendimentos por Categoria
    with col_l3_2:
        st.markdown("""
            <div class="dashboard-card">
                <p class="card-title">Atendimentos por Categoria</p>
                <p style="font-size: 11px; margin: 4px 0;">🔵 <b>Acesso / Permissões:</b> 56 (26%)</p>
                <p style="font-size: 11px; margin: 4px 0;">🔵 <b>Falhas / Erros:</b> 48 (22%)</p>
                <p style="font-size: 11px; margin: 4px 0;">🟢 <b>Solicitações:</b> 46 (21%)</p>
                <p style="font-size: 11px; margin: 4px 0;">🟣 <b>Hardware:</b> 24 (11%)</p>
                <p style="font-size: 11px; margin: 4px 0;">🌸 <b>Software:</b> 20 (9%)</p>
                <p style="font-size: 11px; margin: 4px 0;">🟡 <b>Outros:</b> 18 (8%)</p>
                <p class="card-footer-link" style="margin-top: 15px;">Ver todas as categorias →</p>
            </div>
        """, unsafe_allow_html=True)

    # Card Atendimentos por Equipe
    with col_l3_3:
        st.markdown('<div class="dashboard-card"><p class="card-title">Atendimentos por Equipe</p>', unsafe_allow_html=True)
        df_equipe = pd.DataFrame({
            'Equipe': ['N1 - Suporte', 'N2 - Especialista', 'Infraestrutura', 'Sistemas'],
            'Abertos': [72, 32, 14, 10],
            'SLA (%)': ['91%', '85%', '88%', '90%']
        })
        st.dataframe(df_equipe, use_container_width=True, hide_index=True, height=150)
        st.markdown('<p class="card-footer-link">Ver todas as equipes →</p></div>', unsafe_allow_html=True)

    # Card Status dos Sistemas SaaS
    with col_l3_4:
        st.markdown('<div class="dashboard-card"><p class="card-title">Status dos Sistemas SaaS</p>', unsafe_allow_html=True)
        df_status_saas = pd.DataFrame({
            'Status': ['Operacional', 'Atenção', 'Indisponível'],
            'Qtd': [76, 18, 6]
        })
        fig_saas_status = px.pie(
            df_status_saas, names='Status', values='Qtd', hole=0.6,
            color='Status',
            color_discrete_map={'Operacional': '#16a34a', 'Atenção': '#facc15', 'Indisponível': '#dc2626'}
        )
        fig_saas_status.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', height=160, margin=dict(t=5, b=5, l=5, r=5),
            showlegend=True, legend=dict(font=dict(size=9))
        )
        st.plotly_chart(fig_saas_status, use_container_width=True)
        st.markdown('<p class="card-footer-link">Ver todos os sistemas →</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LINHA 4: BASE DE CONHECIMENTO E IA & AUTOMAÇÃO (2 CARDS INFERIORES) ---
    col_l4_1, col_l4_2 = st.columns([1.2, 1.8])

    # Card Base de Conhecimento
    with col_l4_1:
        st.markdown("""
            <div class="dashboard-card">
                <p class="card-title">Base de Conhecimento - Artigos Populares</p>
                <div style="font-size: 11px; background: #0f172a; padding: 8px; border-radius: 6px; margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>📄 Como redefinir senha no AD</span>
                    <span style="color: #94a3b8;">👁️ 124 | Acessos</span>
                </div>
                <div style="font-size: 11px; background: #0f172a; padding: 8px; border-radius: 6px; margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>📄 Erro ao conectar no Outlook</span>
                    <span style="color: #94a3b8;">👁️ 98 | Microsoft 365</span>
                </div>
                <div style="font-size: 11px; background: #0f172a; padding: 8px; border-radius: 6px; display: flex; justify-content: space-between;">
                    <span>📄 VPN não conecta</span>
                    <span style="color: #94a3b8;">👁️ 85 | Rede</span>
                </div>
                <p class="card-footer-link" style="margin-top: 15px;">Ver todos os artigos →</p>
            </div>
        """, unsafe_allow_html=True)

    # Card IA & Automação (Insights)
    with col_l4_2:
        st.markdown("""
            <div class="dashboard-card">
                <p class="card-title" style="color: #a78bfa;">🤖 IA & Automação (Insights)</p>
                <p style="font-size: 11px; color: #94a3af; margin-bottom: 12px;">A IA identificou padrões nos chamados e sugere ações automáticas para acelerar a resolução.</p>
                <div style="display: flex; gap: 10px;">
                    <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; flex: 1; border: 1px solid #1e293b;">
                        <h4 style="margin: 0; font-size: 18px; color: #fff;">128</h4>
                        <p style="margin: 0; font-size: 10px; color: #94a3af;">Chamados categorizados automaticamente</p>
                        <p style="margin: 2px 0 0 0; font-size: 9px; color: #10b981;">↑ 18% este mês</p>
                    </div>
                    <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; flex: 1; border: 1px solid #1e293b;">
                        <h4 style="margin: 0; font-size: 18px; color: #fff;">45</h4>
                        <p style="margin: 0; font-size: 10px; color: #94a3af;">Soluções sugeridas pela IA</p>
                        <p style="margin: 2px 0 0 0; font-size: 9px; color: #10b981;">↑ 21% este mês</p>
                    </div>
                    <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; flex: 1; border: 1px solid #1e293b;">
                        <h4 style="margin: 0; font-size: 18px; color: #fff;">32%</h4>
                        <p style="margin: 0; font-size: 10px; color: #94a3af;">Dos tickets resolvidos com apoio da IA</p>
                        <p style="margin: 2px 0 0 0; font-size: 9px; color: #10b981;">↑ 12% este mês</p>
                    </div>
                </div>
                <p class="card-footer-link" style="margin-top: 15px;">Ver painel de IA →</p>
            </div>
        """, unsafe_allow_html=True)

else:
    # Caso o usuário navegue para outra aba na Sidebar
    st.title(f"🛠️ Módulo: {aba_activa}")
    st.info(f"Você está navegando na seção de **{aba_activa}**. O conteúdo completo deste módulo pode ser integrado aqui.")
