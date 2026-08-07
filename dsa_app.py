import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu

# --- INICIALIZAÇÃO E MIGRAÇÃO AUTOMÁTICA DO BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    
    # Cria as tabelas se não existirem
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT, 
            empresa TEXT, 
            email TEXT, 
            telefone TEXT, 
            regiao TEXT, 
            status TEXT, 
            origem TEXT,
            motivo_perda TEXT,
            data TEXT, 
            data_fechamento TEXT,
            responsavel TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            titulo TEXT, 
            estagio TEXT, 
            valor REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            cliente TEXT, 
            valor REAL, 
            data TEXT,
            responsavel TEXT
        )
    """)
    
    # Garante que colunas novas existam mesmo em bases antigas
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(clientes)")
    colunas_existentes = [col[1] for col in cursor.fetchall()]
    
    novas_colunas = {
        "origem": "TEXT",
        "motivo_perda": "TEXT",
        "data_fechamento": "TEXT",
        "responsavel": "TEXT"
    }
    
    for coluna, tipo in novas_colunas.items():
        if coluna not in colunas_existentes:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}")
            
    conn.commit()
    conn.close()

inicializar_banco()

st.set_page_config(
    page_title="CRM Comercial Profissional", page_icon="📊", layout="wide"
)

# --- BARRA LATERAL COM MENU E ÍCONES ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0 20px 0;">
            <div style="background-color: #2563EB; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">📊</div>
            <div>
                <div style="font-weight: bold; font-size: 16px; color: #ffffff;">CRM</div>
                <div style="font-size: 11px; color: #94a3b8; letter-spacing: 1px;">COMERCIAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Clientes",
            "Leads",
            "Pipeline",
            "Vendas",
            "Relatórios",
            "Integrações",
            "Configurações",
        ],
        icons=[
            "speedometer2", 
            "people-fill",    
            "person-plus-fill", 
            "kanban",         
            "trophy-fill",    
            "file-earmark-bar-graph", 
            "plug",           
            "gear-fill"       
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#60a5fa", "font-size": "15px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0px",
                "color": "#94a3b8",
                "--hover-color": "#1e293b",
            },
            "nav-link-selected": {
                "background-color": "#2563EB",
                "color": "#FFFFFF",
                "font-weight": "600",
            },
        },
    )

# --- FUNÇÃO PARA CONEXÃO E CARREGAMENTO COM CACHE EM TEMPO REAL ---
def conectar():
    return sqlite3.connect("crm.db")

@st.cache_data(ttl=1)
def carregar_dados():
    conn = conectar()
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame(columns=["id", "nome", "empresa", "email", "telefone", "regiao", "status", "origem", "motivo_perda", "data", "data_fechamento", "responsavel"])
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame(columns=["id", "titulo", "estagio", "valor"])
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame(columns=["id", "cliente", "valor", "data", "responsavel"])
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# Normalização de regiões
if not df_clientes.empty and "regiao" in df_clientes.columns:
    df_clientes["regiao"] = df_clientes["regiao"].astype(str).str.replace("Região ", "", regex=False).str.strip()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # 1. CÁLCULOS DE MÉTRICAS AVANÇADAS
    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    receita_prevista = valor_pipeline 
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and "valor" in df_vendas.columns and len(df_vendas) > 0 else 0.0
    
    vendas_fechadas_count = len(df_clientes[df_clientes["status"] == "✅ Venda Fechada"]) if not df_clientes.empty and "status" in df_clientes.columns else 0
    taxa_conversao = (vendas_fechadas_count / total_leads * 100) if total_leads > 0 else 0.0

    tempo_medio_fechamento = 0
    if not df_clientes.empty and "data" in df_clientes.columns and "data_fechamento" in df_clientes.columns:
        df_fechados = df_clientes[(df_clientes["status"] == "✅ Venda Fechada") & (df_clientes["data_fechamento"].notnull()) & (df_clientes["data_fechamento"] != "")]
        if not df_fechados.empty:
            d_ini = pd.to_datetime(df_fechados["data"], errors='coerce')
            d_fim = pd.to_datetime(df_fechados["data_fechamento"], errors='coerce')
            diffs = (d_fim - d_ini).dt.days
            tempo_medio_fechamento = int(diffs.mean()) if not diffs.empty else 0

    # --- LINHA 1 DE KPIS ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Leads", f"{total_leads}")
    k2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    k3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    k4.metric("Receita Prevista", f"R$ {receita_prevista:,.2f}")

    # --- LINHA 2 DE KPIS ---
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    k6.metric("Taxa de Conversão", f"{taxa_conversao:.1f}%")
    k7.metric("Tempo Médio Fechamento", f"{tempo_medio_fechamento} dias")
    follow_pendentes_count = len(df_clientes[df_clientes["status"] == "📅 Follow-up Agendado"]) if not df_clientes.empty and "status" in df_clientes.columns else 0
    k8.metric("Follow-ups Pendentes", f"{follow_pendentes_count}")

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # --- GRÁFICOS: LINHA 1 ---
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Leads por Status</div>
        """, unsafe_allow_html=True)
        if not df_clientes.empty and "status" in df_clientes.columns:
            status_df = df_clientes['status'].value_counts().reset_index()
            status_df.columns = ['Status', 'Quantidade']
            fig_status = px.bar(status_df, x='Quantidade', y='Status', orientation='h', color_discrete_sequence=['#2563EB'])
            fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(l=10, r=10, t=10, b=10), font=dict(color="white"))
            st.plotly_chart(fig_status, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Sem dados de status.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Funil de Conversão (Pipeline)</div>
        """, unsafe_allow_html=True)
        etapas = ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechamento']
        if not df_pipeline.empty and "estagio" in df_pipeline.columns:
            contagem_estagios = df_pipeline['estagio'].value_counts()
            valores_funil = [int(contagem_estagios.get(est, 0)) for est in etapas]
        else:
            valores_funil = [0, 0, 0, 0, 0]

        fig_funil = go.Figure(go.Funnel(
            y=etapas, x=valores_funil, textposition="inside", textinfo="value",
            marker=dict(color=["#2563EB", "#3b82f6", "#60a5fa", "#38bdf8", "#7dd3fc"])
        ))
        fig_funil.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(l=10, r=10, t=10, b=10), font=dict(color="white"))
        st.plotly_chart(fig_funil, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- GRÁFICOS: LINHA 2 ---
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Vendas por Responsável</div>
        """, unsafe_allow_html=True)
        if not df_vendas.empty and "responsavel" in df_vendas.columns:
            resp_df = df_vendas.groupby('responsavel')['valor'].sum().reset_index()
            fig_resp = px.bar(resp_df, x='responsavel', y='valor', color_discrete_sequence=['#10b981'])
            fig_resp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(l=10, r=10, t=10, b=10), font=dict(color="white"))
            st.plotly_chart(fig_resp, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Nenhuma venda registrada com responsável.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g4:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Origem dos Leads & Conversão</div>
        """, unsafe_allow_html=True)
        if not df_clientes.empty and "origem" in df_clientes.columns and df_clientes["origem"].notnull().any():
            origem_df = df_clientes['origem'].value_counts().reset_index()
            origem_df.columns = ['Origem', 'Total']
            fig_origem = px.pie(origem_df, names='Origem', values='Total', hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_origem.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(l=10, r=10, t=10, b=10), font=dict(color="white"))
            st.plotly_chart(fig_origem, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Preencha a origem no cadastro de clientes para ver este gráfico.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- GRÁFICOS: LINHA 3 ---
    col_g5, col_g6 = st.columns(2)

    with col_g5:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Motivos de Perda (Vendas Perdidas)</div>
        """, unsafe_allow_html=True)
        if not df_clientes.empty and "motivo_perda" in df_clientes.columns:
            perdidos = df_clientes[df_clientes["status"] == "❌ Venda Perdida"]
            if not perdidos.empty and perdidos["motivo_perda"].notnull().any():
                motivos = perdidos['motivo_perda'].value_counts().reset_index()
                motivos.columns = ['Motivo', 'Qtd']
                fig_motivo = px.pie(motivos, names='Motivo', values='Qtd', hole=0.4, color_discrete_sequence=['#ef4444', '#f59e0b', '#dc2626'])
                fig_motivo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=230, margin=dict(l=10, r=10, t=10, b=10), font=dict(color="white"))
                st.plotly_chart(fig_motivo, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Nenhum lead com motivo de perda registrado.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g6:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Clientes Inativos / Sem Interesse</div>
        """, unsafe_allow_html=True)
        if not df_clientes.empty and "status" in df_clientes.columns:
            inativos = df_clientes[df_clientes["status"].isin(["🚫 Sem Interesse", "⏳ Em Espera"])]
            if not inativos.empty:
                st.dataframe(inativos[['nome', 'empresa', 'telefone', 'status']], use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum cliente inativo ou sem interesse registrado.")
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro Completo de Clientes e Leads")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Adicione novos contatos e categorize com todos os status e origens.</p>", unsafe_allow_html=True)
    
    with st.form("form_cliente_completo", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_contato = st.text_input("Nome do Contato *")
            nome_empresa = st.text_input("Nome da Empresa")
            email_cli = st.text_input("E-mail")
            telefone_cli = st.text_input("Telefone / WhatsApp")
            regiao_cli = st.selectbox("Região", ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"])
        with col_c2:
            origem_cli = st.selectbox("Origem do Lead", ["Indicação", "Instagram", "Google Ads", "WhatsApp", "Prospecção Ativa", "Site"])
            
            status_opcoes = [
                "🆕 Novo Lead", "📞 Primeiro Contato", "💬 Em Atendimento",
                "📋 Proposta Enviada", "⏳ Aguardando Resposta", "🤝 Negociação",
                "✅ Venda Fechada", "❌ Venda Perdida", "🔄 Pós-Venda",
                "❤️ Cliente Fidelizado", "📅 Follow-up Agendado",
                "🚫 Sem Interesse", "⏳ Em Espera", "🔄 Reativado"
            ]
            status_cli = st.selectbox("Status do Cliente", status_opcoes)
            
            motivo_cli = st.text_input("Motivo de Perda (Preencha se o status for Venda Perdida)")
            responsavel_cli = st.text_input("Responsável Comercial", value="Equipe Comercial")
            data_cad = st.text_input("Data de Cadastro", value=str(date.today()))
            data_fech = st.text_input("Data de Fechamento (Se aplicável)", value="")
            
        submitted_cli = st.form_submit_button("Salvar Cliente no CRM")
        if submitted_cli:
            if nome_contato:
                conn = conectar()
                conn.execute("""
                    INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, origem, motivo_perda, data, data_fechamento, responsavel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome_contato, nome_empresa, email_cli, telefone_cli, regiao_cli, status_cli, origem_cli, motivo_cli, data_cad, data_fech, responsavel_cli))
                conn.commit()
                conn.close()
                st.success("Cliente cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha ao menos o Nome do Contato.")

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Base de Dados Geral (CRM)")
    if not df_clientes.empty:
        colunas_mostrar = [c for c in ['nome', 'empresa', 'telefone', 'origem', 'status', 'responsavel', 'data'] if c in df_clientes.columns]
        st.dataframe(df_clientes[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Filtro exclusivo focado em prospecção e novos contatos.</p>", unsafe_allow_html=True)
    
    df_leads_only = df_clientes[df_clientes["status"].str.contains("Lead|Contato|Atendimento", case=False, na=False)] if not df_clientes.empty and "status" in df_clientes.columns else pd.DataFrame()
    if not df_leads_only.empty:
        colunas_mostrar = [c for c in ["nome", "empresa", "email", "telefone", "origem", "status", "data"] if c in df_leads_only.columns]
        st.dataframe(df_leads_only[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead em aberto no momento.")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Acompanhamento de negócios por etapas do funil.</p>", unsafe_allow_html=True)

    with st.form("form_pipeline", clear_on_submit=True):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_titulo = st.text_input("Título do Negócio *")
        with col_p2:
            p_estagio = st.selectbox("Estágio", ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"])
        with col_p3:
            p_valor = st.number_input("Valor Estimado (R$)", min_value=0.0, step=100.0)
            
        btn_pipe = st.form_submit_button("Adicionar Negócio ao Pipeline")
        if btn_pipe:
            if p_titulo:
                conn = conectar()
                conn.execute("INSERT INTO pipeline (titulo, estagio, valor) VALUES (?, ?, ?)", (p_titulo, p_estagio, p_valor))
                conn.commit()
                conn.close()
                st.success("Negócio adicionado!")
                st.rerun()
            else:
                st.error("Informe o título do negócio.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    estagios = ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"]
    cols = st.columns(len(estagios))
    
    for i, estagio in enumerate(estagios):
        with cols[i]:
            st.markdown(f"<div style='background-color: #1e293b; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; color: #60a5fa;'>{estagio}</div>", unsafe_allow_html=True)
            subset = df_pipeline[df_pipeline["estagio"] == estagio] if not df_pipeline.empty and "estagio" in df_pipeline.columns else pd.DataFrame()
            if not subset.empty:
                for _, row in subset.iterrows():
                    st.markdown(f"""
                        <div style="background-color: #0f172a; padding: 10px; border-radius: 6px; margin-top: 10px; border: 1px solid #334155;">
                            <div style="font-size: 13px; font-weight: bold; color: #ffffff;">{row['titulo']}</div>
                            <div style="font-size: 12px; color: #10b981; margin-top: 4px;">R$ {row['valor']:,.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div style='color: #64748b; font-size: 12px; text-align: center; margin-top: 10px;'>Vazio</div>", unsafe_allow_html=True)

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas Fechadas")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Registre faturamentos e atribua responsáveis.</p>", unsafe_allow_html=True)

    with st.form("form_venda", clear_on_submit=True):
        col_v1, col_v2, col_v3, col_v4 = st.columns(4)
        with col_v1:
            v_cliente = st.text_input("Nome do Cliente *")
        with col_v2:
            v_valor = st.number_input("Valor da Venda (R$)", min_value=0.0, step=100.0)
        with col_v3:
            v_resp = st.text_input("Responsável", value="Comercial")
        with col_v4:
            v_data = st.text_input("Data da Venda", value=str(date.today()))
            
        btn_venda = st.form_submit_button("Registrar Venda")
        if btn_venda:
            if v_cliente and v_valor > 0:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel) VALUES (?, ?, ?, ?)", (v_cliente, v_valor, v_data, v_resp))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o cliente e um valor válido.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📜 Histórico de Vendas")
    if not df_vendas.empty:
        colunas_mostrar_v = [c for c in ["cliente", "valor", "responsavel", "data"] if c in df_vendas.columns]
        st.dataframe(df_vendas[colunas_mostrar_v], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada ainda.")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Baixe relatórios consolidados do seu CRM em formato CSV.</p>", unsafe_allow_html=True)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 10px;">Relatório de Clientes</div>
        """, unsafe_allow_html=True)
        if not df_clientes.empty:
            csv_clientes = df_clientes.to_csv(index=False).encode('utf-8')
            st.download_button("Baixar CSV de Clientes", data=csv_clientes, file_name="clientes_crm.csv", mime="text/csv")
        else:
            st.info("Sem dados.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 10px;">Relatório de Vendas</div>
        """, unsafe_allow_html=True)
        if not df_vendas.empty:
            csv_vendas = df_vendas.to_csv(index=False).encode('utf-8')
            st.download_button("Baixar CSV de Vendas", data=csv_vendas, file_name="vendas_crm.csv", mime="text/csv")
        else:
            st.info("Sem dados.")
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Conecte seu CRM com ferramentas externas.</p>", unsafe_allow_html=True)
    st.toggle("Ativar Integração WhatsApp", value=True)
    st.text_input("Chave de API", value="crm_live_sec_99812736", type="password")

else:
    st.markdown("### ⚙️ Configurações do Sistema")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Gerencie as preferências da sua conta.</p>", unsafe_allow_html=True)
    st.text_input("Nome da Organização", value="Comercial Alpha LTDA")
    st.text_input("E-mail do Administrador", value="admin@crm.com")
    if st.button("Salvar Configurações"):
        st.success("Salvo com sucesso!")
