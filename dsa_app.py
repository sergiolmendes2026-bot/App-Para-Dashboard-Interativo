import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import date
from streamlit_option_menu import option_menu

# --- INICIALIZAÇÃO E MIGRAÇÃO AUTOMÁTICA DO BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("crm.db")
    
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
            valor REAL,
            empresa TEXT,
            contato TEXT,
            telefone TEXT,
            email TEXT,
            responsavel TEXT,
            origem TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            cliente TEXT, 
            valor REAL, 
            data TEXT,
            responsavel TEXT,
            status TEXT
        )
    """)
    
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(clientes)")
    colunas_existentes_clientes = [col[1] for col in cursor.fetchall()]
    novas_colunas_clientes = {"origem": "TEXT", "motivo_perda": "TEXT", "data_fechamento": "TEXT", "responsavel": "TEXT"}
    for coluna, tipo in novas_colunas_clientes.items():
        if coluna not in colunas_existentes_clientes:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}")

    cursor.execute("PRAGMA table_info(pipeline)")
    colunas_existentes_pipeline = [col[1] for col in cursor.fetchall()]
    novas_colunas_pipeline = {"empresa": "TEXT", "contato": "TEXT", "telefone": "TEXT", "email": "TEXT", "responsavel": "TEXT", "origem": "TEXT"}
    for coluna, tipo in novas_colunas_pipeline.items():
        if coluna not in colunas_existentes_pipeline:
            conn.execute(f"ALTER TABLE pipeline ADD COLUMN {coluna} {tipo}")

    cursor.execute("PRAGMA table_info(vendas)")
    colunas_existentes_vendas = [col[1] for col in cursor.fetchall()]
    if "status" not in colunas_existentes_vendas:
        conn.execute("ALTER TABLE vendas ADD COLUMN status TEXT")
            
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
        default_index=5,
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

def conectar():
    return sqlite3.connect("crm.db")

@st.cache_data(ttl=1)
def carregar_dados():
    conn = conectar()
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame()
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame()
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame()
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### 📊 Dashboard de Performance Comercial")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    total_leads = len(df_clientes)
    valor_pipeline = df_pipeline['valor'].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0
    receita_realizada = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and "valor" in df_vendas.columns and len(df_vendas) > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Leads", f"{total_leads}")
    k2.metric("Valor do Pipeline", f"R$ {valor_pipeline:,.2f}")
    k3.metric("Receita Realizada", f"R$ {receita_realizada:,.2f}")
    k4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro Completo de Clientes e Leads")
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
            motivo_cli = st.text_input("Motivo de Perda (Se aplicável)")
            responsavel_cli = st.text_input("Responsável Comercial", value="Equipe Comercial")
            data_cad = st.text_input("Data de Cadastro", value=str(date.today()))
            data_fech = st.text_input("Data de Fechamento", value="")
            
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
    df_leads_only = df_clientes[df_clientes["status"].str.contains("Lead|Contato|Atendimento", case=False, na=False)] if not df_clientes.empty and "status" in df_clientes.columns else pd.DataFrame()
    if not df_leads_only.empty:
        colunas_mostrar = [c for c in ["nome", "empresa", "email", "telefone", "origem", "status", "data"] if c in df_leads_only.columns]
        st.dataframe(df_leads_only[colunas_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead em aberto no momento.")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline Comercial")
    with st.form("form_pipeline", clear_on_submit=True):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_titulo = st.text_input("Título do Negócio *")
            p_empresa = st.text_input("Empresa")
        with col_p2:
            p_estagio = st.selectbox("Estágio", ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"])
            p_contato = st.text_input("Contato")
        with col_p3:
            p_valor = st.number_input("Valor Estimado (R$)", min_value=0.0, step=100.0)
            p_telefone = st.text_input("Telefone")
            
        col_p4, col_p5, col_p6 = st.columns(3)
        with col_p4:
            p_email = st.text_input("E-mail")
        with col_p5:
            p_responsavel = st.text_input("Responsável", value="Comercial")
        with col_p6:
            p_origem = st.selectbox("Origem do Lead", ["Indicação", "LinkedIn", "Google", "Outbound", "Instagram"])
            
        btn_pipe = st.form_submit_button("Adicionar Negócio ao Pipeline")
        if btn_pipe:
            if p_titulo:
                conn = conectar()
                conn.execute("""
                    INSERT INTO pipeline (titulo, estagio, valor, empresa, contato, telefone, email, responsavel, origem) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (p_titulo, p_estagio, p_valor, p_empresa, p_contato, p_telefone, p_email, p_responsavel, p_origem))
                conn.commit()
                conn.close()
                st.success("Negócio adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Informe o título do negócio.")

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas Fechadas")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Registre faturamentos, acompanhe os indicadores e consulte o histórico em tabela.</p>", unsafe_allow_html=True)

    faturamento_total = df_vendas['valor'].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    total_vendas_count = len(df_vendas) if not df_vendas.empty else 0
    ticket_medio = df_vendas['valor'].mean() if not df_vendas.empty and total_vendas_count > 0 else 0.0
    
    melhor_vendedor = "N/A"
    if not df_vendas.empty and "responsavel" in df_vendas.columns and total_vendas_count > 0:
        vendas_por_resp = df_vendas.groupby('responsavel')['valor'].sum()
        if not vendas_por_resp.empty:
            melhor_vendedor = vendas_por_resp.idxmax()

    vk1, vk2, vk3, vk4 = st.columns(4)
    vk1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
    vk2.metric("📦 Total de Vendas", f"{total_vendas_count}")
    vk3.metric("📈 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    vk4.metric("🏆 Melhor Vendedor", f"{melhor_vendedor}")

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    with st.form("form_venda", clear_on_submit=True):
        col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
        with col_v1:
            v_cliente = st.text_input("Cliente *")
        with col_v2:
            v_valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
        with col_v3:
            v_resp = st.text_input("Responsável", value="Comercial")
        with col_v4:
            v_data = st.text_input("Data", value=str(date.today()))
        with col_v5:
            v_status = st.selectbox("Status", ["Pago", "Pendente", "Cancelado"])
            
        btn_venda = st.form_submit_button("Registrar Venda")
        if btn_venda:
            if v_cliente and v_valor > 0:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data, responsavel, status) VALUES (?, ?, ?, ?, ?)", 
                             (v_cliente, v_valor, v_data, v_resp, v_status))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o cliente e um valor válido.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📜 Histórico de Vendas")
    
    pesquisa_cliente = st.text_input("🔍 Pesquisar cliente...", placeholder="Digite o nome do cliente...")

    if not df_vendas.empty:
        df_tabela_vendas = df_vendas[['cliente', 'valor', 'responsavel', 'data', 'status']].copy()
        df_tabela_vendas.columns = ['Cliente', 'Valor', 'Responsável', 'Data', 'Status']
        
        if pesquisa_cliente:
            df_tabela_vendas = df_tabela_vendas[df_tabela_vendas['Cliente'].str.contains(pesquisa_cliente, case=False, na=False)]
            
        df_tabela_vendas['Valor'] = df_tabela_vendas['Valor'].apply(lambda x: f"R$ {x:,.3f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(df_tabela_vendas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada ainda.")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios e Exportação")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Botões como:</p>", unsafe_allow_html=True)
    
    # Prepara os dados para exportação (mesmo se vazio gera planilha vazia ou com cabeçalho)
    df_export = df_vendas if not df_vendas.empty else pd.DataFrame(columns=['cliente', 'valor', 'data', 'responsavel', 'status'])

    # Geração do Excel em memória
    output_excel = io.BytesIO()
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Vendas')
    excel_data = output_excel.getvalue()

    # Geração do arquivo TXT/Relatório estruturado
    pdf_data = df_export.to_string(index=False).encode('utf-8')

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="📥 Exportar Excel",
            data=excel_data,
            file_name="vendas_crm.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_btn2:
        st.download_button(
            label="📥 Exportar PDF",
            data=pdf_data,
            file_name="relatorio_vendas.txt",
            mime="text/plain"
        )

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.toggle("Ativar Integração WhatsApp", value=True)

else:
    st.markdown("### ⚙️ Configurações do Sistema")
    st.text_input("Nome da Organização", value="Comercial Alpha LTDA")
