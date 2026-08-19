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

# Inicializar estado da sessão para navegação interna de chamados
if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None

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
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 18px; color: #94a3b8; cursor: pointer;">☰</span>
            <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">{aba_activa}</h2>
        </div>
        <p style="margin: 2px 0 0 30px; font-size: 11px; color: #64748b;">Gerenciamento completo de solicitações, incidentes e suporte de TI</p>
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

    # --- DASHBOARD PRINCIPAL ---
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
    col_l2_1, col_l2_2, col_l2_3 = st.columns([1, 1.6, 1])

    with col_l2_1:
        st.markdown('<div class="dashboard-card"><p class="card-title">Chamados Abertos por Prioridade</p>', unsafe_allow_html=True)
        df_prioridade = pd.DataFrame({'Prioridade': ['Crítica', 'Alta', 'Média', 'Baixa'], 'Quantidade': [28, 36, 42, 22]})
        fig_donut = px.pie(df_prioridade, names='Prioridade', values='Quantidade', hole=0.65, color='Prioridade', color_discrete_map={'Crítica': '#dc2626', 'Alta': '#ea580c', 'Média': '#facc15', 'Baixa': '#16a34a'})
        fig_donut.update_traces(textinfo='percent', textfont_size=11)
        fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=230, margin=dict(t=10, b=10, l=10, r=10), showlegend=True, legend=dict(orientation="v", y=0.5, x=1.0, font=dict(size=10)))
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
        st.dataframe(df_recentes, use_container_width=True, hide_index=True, height=220)
        st.markdown('<p class="card-footer-link">Ver todos os chamados →</p></div>', unsafe_allow_html=True)

    with col_l2_3:
        st.markdown('<div class="dashboard-card"><p class="card-title">Incidentes por Sistema SaaS</p>', unsafe_allow_html=True)
        df_saas = pd.DataFrame({'Sistema': ['Microsoft 365', 'Salesforce', 'SAP Business One', 'Totvs Protheus', 'Google Workspace'], 'Incidentes': [24, 18, 15, 10, 8]})
        fig_bar = px.bar(df_saas, x='Incidentes', y='Sistema', orientation='h', text='Incidentes', color_discrete_sequence=['#0ea5e9'])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=220, margin=dict(t=5, b=5, l=5, r=5), xaxis=dict(showgrid=False, visible=False), yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="white")))
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('<p class="card-footer-link">Ver todos os sistemas →</p></div>', unsafe_allow_html=True)

elif aba_activa == "Chamados":

    # =========================================================
    # 6. MÓDULO DE CHAMADOS ITSM (COMPLETO)
    # =========================================================

    # Se um chamado foi selecionado para detalhamento
    if st.session_state.selected_ticket:
        t_id = st.session_state.selected_ticket
        
        if st.button("← Voltar para a lista de chamados"):
            st.session_state.selected_ticket = None
            st.rerun()

        st.markdown(f"""
            <div style="background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 10px; margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #ffffff;">🎫 {t_id} — Erro ao acessar o ERP SAP</h3>
                    <span style="background-color: #7f1d1d; color: #f87171; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;">🔴 Alta Prioridade</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Abas de detalhe do Chamado
        tab_det, tab_hist, tab_ia, tab_anexos, tab_auditoria = st.tabs(["📋 Informações & Descrição", "⏱️ Histórico & Timeline", "🤖 AI Assistant & RAG", "📎 Anexos (2)", "🔐 Auditoria"])

        with tab_det:
            col_d1, col_d2 = st.columns([1.5, 1])
            with col_d1:
                st.markdown("#### Informações do Solicitante e Atendimento")
                st.markdown("""
                - **Solicitante:** Ana Souza
                - **Empresa / Departamento:** Empresa XYZ / Financeiro
                - **Sistema:** SAP Business One
                - **Tipo / Categoria:** Incidente / Acesso & Permissões
                - **Status Atual:** Em atendimento
                - **Responsável:** Carlos Mendes (N1)
                """)
                st.markdown("#### Descrição do Problema")
                st.info("Usuária informa que não consegue acessar o sistema ERP desde as 08:30 da manhã. Apresenta erro de timeout e credenciais rejeitadas após atualização de senha.")
            
            with col_d2:
                st.markdown("#### ⏱️ Controle de SLA")
                st.metric("Tempo Restante", "01h 42m", "- 2h 18m decorridas", delta_color="normal")
                st.markdown("""
                - **Início:** 31/05/2026 08:30
                - **Prazo limite:** 31/05/2026 12:30
                - **Status SLA:** 🟢 Dentro do prazo
                """)
                st.markdown("---")
                st.markdown("#### 🔀 Escalonamento")
                st.selectbox("Escalar para nível:", ["Manter em N1", "N2 — Especialistas", "N3 — Arquitetura", "Infraestrutura"])
                if st.button("Executar Escalonamento"):
                    st.success("Chamado escalado com sucesso para N2!")

        with tab_hist:
            st.markdown("#### ⏱️ Linha do Tempo (Timeline do Chamado)")
            st.markdown("""
            - 🟢 **08:30** — 🎫 **Chamado aberto** por Ana Souza.
            - 🤖 **08:32** — 🤖 **IA analisou o chamado:** Categoria identificada como *Acesso*, Prioridade sugerida: *Alta*.
            - 👤 **08:34** — 👤 **Atribuído** para Carlos Mendes (N1).
            - 🔧 **08:45** — 🔧 **Em atendimento:** Analista iniciou investigação remota.
            - 💬 **09:10** — 💬 **Atualização:** Solicitado teste de autenticação em modo anônimo.
            - ⏳ **09:25** — ⏳ **Status alterado:** Aguardando resposta do usuário.
            """)

        with tab_ia:
            st.markdown("""
                <div style="background-color: #0f172a; border: 1px solid #1e293b; padding: 15px; border-radius: 10px;">
                    <h4 style="color: #a78bfa; margin-top: 0;">🤖 AI Assistant & RAG Insights</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">O chamado apresenta características de problema de autenticação no SAP devido a expiração de token no AD.</p>
                    <hr style="border-color: #1e293b;">
                    <p style="font-size: 13px; color: #e2e8f0; font-weight: bold;">📚 Base de Conhecimento RAG Encontrada:</p>
                    <p style="font-size: 12px; color: #38bdf8;">Artigo: "Problemas de autenticação e reset de token no SAP" (Relevância: 94%)</p>
                    <p style="font-size: 12px; color: #cbd5e1;"><b>💡 Solução sugerida pela IA:</b> Verificar o status da conta no Active Directory, forçar sincronização de credenciais e limpar cache do client SAP.</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_ia1, col_ia2, col_ia3 = st.columns(3)
            with col_ia1:
                if st.button("✨ Aplicar Solução Sugerida"):
                    st.success("Solução aplicada e enviada ao usuário!")
            with col_ia2:
                if st.button("📖 Ver Artigo na KB"):
                    st.info("Abrindo base de conhecimento...")
            with col_ia3:
                if st.button("📤 Enviar Resposta Pronta"):
                    st.success("Resposta enviada por e-mail para Ana Souza!")

        with tab_anexos:
            st.markdown("#### 📎 Arquivos Anexados")
            st.markdown("- 📄 `erro_login_sap.png` (Enviado por Ana Souza às 08:30)")
            st.markdown("- 📄 `log_autenticacao.txt` (Enviado por Carlos Mendes às 08:46)")
            st.file_uploader("Adicionar novo anexo ao chamado", type=['png', 'jpg', 'pdf', 'txt', 'docx'])

        with tab_auditoria:
            st.markdown("#### 🔐 Registro de Governança e Auditoria")
            df_audit = pd.DataFrame({
                'Data/Hora': ['31/05/2026 08:34', '31/05/2026 08:32', '31/05/2026 08:30'],
                'Usuário': ['Carlos Mendes', 'IA LaryMB', 'Ana Souza'],
                'Campo Alterado': ['Responsável / Status', 'Prioridade / Categoria', 'Criação do Ticket'],
                'Valor Anterior': ['Não atribuído', 'Média', '-'],
                'Novo Valor': ['Carlos Mendes / Em atendimento', 'Alta / Acesso', 'Aberto']
            })
            st.dataframe(df_audit, use_container_width=True, hide_index=True)

    else:
        # --- TELA PRINCIPAL DE LISTAGEM DE CHAMADOS ---
        
        # 1. Topo: Ações e Botões
        col_top1, col_top2 = st.columns([2, 2])
        with col_top1:
            st.text_input("Buscar chamado", placeholder="🔎 Buscar por ID, título ou solicitante...", label_visibility="collapsed")
        with col_top2:
            bc1, bc2, bc3, bc4 = st.columns(4)
            with bc1:
                if st.button("➕ Novo"):
                    st.toast("Abrindo painel de novo chamado...")
            with bc2:
                st.button("🎛️ Filtros")
            with bc3:
                st.button("📥 Exportar")
            with bc4:
                if st.button("🔄 Atualizar"):
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Cards de Indicadores
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

        # 3. Filtros Avançados Expansíveis
        with st.expander("🎛️ Filtros Avançados de Chamados (Status, Prioridade, Tipo, Categoria, Sistema)"):
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                st.selectbox("Status", ["Todos", "Novo", "Em triagem", "Em atendimento", "Aguardando usuário", "Resolvido", "Fechado"])
            with fc2:
                st.selectbox("Prioridade", ["Todas", "Baixa", "Média", "Alta", "Crítica"])
            with fc3:
                st.selectbox("Tipo", ["Todos", "Incidente", "Solicitação", "Problema", "Dúvida"])
            with fc4:
                st.selectbox("Sistema", ["Todos", "Microsoft 365", "Salesforce", "SAP", "Google Workspace"])

        st.markdown("<br>", unsafe_allow_html=True)

        # 4. Tabela Principal de Chamados com Ação de Clique
        st.markdown("#### Lista de Chamados Ativos")
        
        chamados_data = [
            {"ID": "#CH-10234", "Título": "Erro ao acessar o ERP", "Solicitante": "Ana Souza", "Tipo": "Incidente", "Prioridade": "🔴 Alta", "Sistema": "SAP", "Responsável": "Carlos", "SLA": "01:42", "Status": "Em atendimento"},
            {"ID": "#CH-10233", "Título": "Falha na integração com API", "Solicitante": "Carlos Mendes", "Tipo": "Incidente", "Prioridade": "🚨 Crítica", "Sistema": "API", "Responsável": "João", "SLA": "00:35", "Status": "Em atendimento"},
            {"ID": "#CH-10232", "Título": "Impressora sem resposta", "Solicitante": "João Ferreira", "Tipo": "Solicitação", "Prioridade": "🟡 Média", "Sistema": "Hardware", "Responsável": "Maria", "SLA": "05:20", "Status": "Novo"},
            {"ID": "#CH-10231", "Título": "Solicitação de acesso VPN", "Solicitante": "Mariana Lima", "Tipo": "Solicitação", "Prioridade": "🟢 Baixa", "Sistema": "Rede", "Responsável": "Pedro", "SLA": "12:00", "Status": "Novo"},
            {"ID": "#CH-10230", "Título": "Tela azul no Windows 11", "Solicitante": "Pedro Oliveira", "Tipo": "Incidente", "Prioridade": "🔴 Alta", "Sistema": "M365", "Responsável": "Carlos", "SLA": "00:15", "Status": "Em atendimento"}
        ]
        
        df_chamados = pd.DataFrame(chamados_data)

        # Renderização interativa por linhas com botões de acesso ao detalhe
        for idx, row in df_chamados.iterrows():
            cols = st.columns([1, 2.5, 1, 1, 1, 1, 1, 1, 1, 1])
            cols[0].markdown(f"**{row['ID']}**")
            cols[1].markdown(f"{row['Título']}")
            cols[2].markdown(f"{row['Solicitante']}")
            cols[3].markdown(f"{row['Tipo']}")
            cols[4].markdown(f"{row['Prioridade']}")
            cols[5].markdown(f"{row['Sistema']}")
            cols[6].markdown(f"{row['Responsável']}")
            cols[7].markdown(f"{row['SLA']}")
            cols[8].markdown(f"{row['Status']}")
            if cols[9].button("👁️ Abrir", key=f"btn_{row['ID']}"):
                st.session_state.selected_ticket = row['ID']
                st.rerun()
            st.markdown("<hr style='margin: 4px 0; border-color: #1e293b;'>", unsafe_allow_html=True)

else:
    # Outros módulos gerais da sidebar
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
