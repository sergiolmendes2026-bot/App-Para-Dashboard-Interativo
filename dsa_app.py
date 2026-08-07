import pandas as pd
import sqlite3
import streamlit as st
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu

# --- GARANTE QUE O BANCO E AS TABELAS ESTEJAM CRIADOS ---
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
            data TEXT, 
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
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_banco()

st.set_page_config(
    page_title="CRM Comercial", page_icon="📊", layout="wide"
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
    
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame(columns=["id", "nome", "empresa", "email", "telefone", "regiao", "status", "data", "responsavel"])
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame(columns=["id", "titulo", "estagio", "valor"])
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame(columns=["id", "cliente", "valor", "data"])
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# Normalização de regiões para evitar divergências de texto
if not df_clientes.empty and "regiao" in df_clientes.columns:
    df_clientes["regiao"] = df_clientes["regiao"].astype(str).str.replace("Região ", "", regex=False).str.strip()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### Visão Geral")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    total_clientes = len(df_clientes) if not df_clientes.empty else 0
    leads_cadastrados = len(df_clientes[df_clientes["status"] == "Lead"]) if not df_clientes.empty and "status" in df_clientes.columns else 0
    clientes_ativos = len(df_clientes[df_clientes["status"] == "Ativo"]) if not df_clientes.empty and "status" in df_clientes.columns else 0
    faturamento_mes = df_vendas["valor"].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0

    # 4 Cards Superiores (KPIs Estilizados)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Total de Clientes</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{total_clientes:,}</div>
                <div style="color: #10b981; font-size: 12px;">↑ Dinâmico <span style="color: #64748b;">vs base</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Leads Cadastrados</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{leads_cadastrados:,}</div>
                <div style="color: #10b981; font-size: 12px;">↑ Dinâmico <span style="color: #64748b;">vs base</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Clientes Ativos</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{clientes_ativos:,}</div>
                <div style="color: #10b981; font-size: 12px;">↑ Dinâmico <span style="color: #64748b;">vs base</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Faturamento (Mês)</div>
                <div style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 8px 0;">R$ {faturamento_mes:,.2f}</div>
                <div style="color: #10b981; font-size: 12px;">↑ Dinâmico <span style="color: #64748b;">vs base</span></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # --- 1. FUNIL DE VENDAS (Usando componente nativo go.Funnel para precisão total) ---
    etapas = ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechamento']
    if not df_pipeline.empty and "estagio" in df_pipeline.columns:
        contagem_estagios = df_pipeline['estagio'].value_counts()
        valores_funil = [int(contagem_estagios.get(est, 0)) for est in etapas]
    else:
        valores_funil = [0, 0, 0, 0, 0]

    fig_funil = go.Figure(go.Funnel(
        y=etapas,
        x=valores_funil,
        textposition="inside",
        textinfo="value",
        marker=dict(color=["#2563EB", "#3b82f6", "#60a5fa", "#38bdf8", "#7dd3fc"]),
        connector=dict(line=dict(color="#334155", width=1))
    ))

    fig_funil.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        font=dict(color="white")
    )

    # --- 2. VENDAS POR MÊS ---
    meses_base = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
    
    if not df_vendas.empty and "data" in df_vendas.columns and "valor" in df_vendas.columns:
        df_vendas['data_dt'] = pd.to_datetime(df_vendas['data'], errors='coerce')
        df_vendas['mes_str'] = df_vendas['data_dt'].dt.strftime('%b')
        vendas_mes = df_vendas.groupby('mes_str')['valor'].sum().reset_index()
        df_padrao = pd.DataFrame({"mes_str": meses_base})
        vendas_mes = pd.merge(df_padrao, vendas_mes, on="mes_str", how="left").fillna(0)
        x_vals = vendas_mes['mes_str'].tolist()
        y_vals = vendas_mes['valor'].tolist()
    else:
        x_vals = meses_base
        y_vals = [0, 0, 0, 0, 0, 0]

    fig_line = go.Figure(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines+markers',
        line=dict(color='#38bdf8', width=3),
        marker=dict(color='#38bdf8', size=8)
    ))

    fig_line.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        xaxis=dict(
            tickfont=dict(color="#94a3b8", size=12),
            showgrid=False,
            zeroline=False,
            categoryorder="array",
            categoryarray=meses_base
        ),
        yaxis=dict(
            tickfont=dict(color="#94a3b8", size=12),
            gridcolor="#334155",
            zeroline=False,
            tickformat="s"
        )
    )

    # --- 3. VENDAS POR REGIÃO (Garantindo que todas as 5 regiões apareçam sempre) ---
    regioes_fixas = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    if not df_clientes.empty and "regiao" in df_clientes.columns:
        contagem_regiao = df_clientes['regiao'].value_counts()
        values_regiao = [int(contagem_regiao.get(reg, 0)) for reg in regioes_fixas]
    else:
        values_regiao = [0, 0, 0, 0, 0]

    cores_regiao = ["#2563EB", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

    fig_regiao = go.Figure(go.Pie(
        labels=regioes_fixas,
        values=values_regiao,
        hole=0.6,
        textinfo='none',
        marker=dict(colors=cores_regiao)
    ))
    fig_regiao.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=200,
        showlegend=True,
        legend=dict(
            font=dict(color="#f8fafc", size=11),
            orientation="v",
            x=1.0,
            y=0.5
        )
    )

    # --- 4. TIPOS DE CLIENTES ---
    if not df_clientes.empty and "status" in df_clientes.columns and df_clientes["status"].dropna().any():
        status_contagem = df_clientes['status'].value_counts()
        labels_tipo = status_contagem.index.tolist()
        values_tipo = status_contagem.values.tolist()
    else:
        labels_tipo = ["Ativo", "Lead", "Inativo"]
        values_tipo = [0, 0, 0]

    cores_tipo = ["#2563EB", "#0ea5e9", "#10b981", "#334155"]

    fig_tipo = go.Figure(go.Pie(
        labels=labels_tipo,
        values=values_tipo,
        hole=0.6,
        textinfo='none',
        marker=dict(colors=cores_tipo[:len(labels_tipo)])
    ))
    fig_tipo.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=200,
        showlegend=True,
        legend=dict(
            font=dict(color="#f8fafc", size=11),
            orientation="v",
            x=1.0,
            y=0.5
        )
    )

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Funil de Vendas</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_funil, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Vendas por Mês</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Vendas por Região</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_regiao, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Tipos de Clientes</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_tipo, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro de Clientes e Leads")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Adicione novos clientes para alimentar o seu CRM e a sua operação comercial.</p>", unsafe_allow_html=True)
    
    with st.form("form_cliente_completo", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_contato = st.text_input("Nome do Contato *")
            nome_empresa = st.text_input("Nome da Empresa")
            email_cli = st.text_input("E-mail")
        with col_c2:
            telefone_cli = st.text_input("Telefone / WhatsApp")
            regiao_cli = st.selectbox("Região", ["Selecione...", "Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"])
            status_cli = st.selectbox("Status do Cliente", ["Ativo", "Lead", "Em Negociação", "Inativo", "Perdido", "VIP"])
            data_cad = st.text_input("Data de Cadastro", value=str(date.today()))
            
        submitted_cli = st.form_submit_button("Salvar Cliente")
        if submitted_cli:
            if nome_contato:
                conn = conectar()
                conn.execute("""
                    INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, data, responsavel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome_contato, nome_empresa, email_cli, telefone_cli, regiao_cli, status_cli, data_cad, "Equipe Comercial"))
                conn.commit()
                conn.close()
                st.success("Cliente cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha ao menos o Nome do Contato.")

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Tabela de Clientes e Contatos (CRM)")
    
    if not df_clientes.empty:
        df_exibicao = pd.DataFrame()
        df_exibicao["Cliente"] = df_clientes.apply(
            lambda row: f"{row['nome']} - {row.get('empresa', 'CRM')}"
            if pd.notnull(row.get('empresa')) and row.get('empresa') != ""
            else row["nome"],
            axis=1,
        )
        df_exibicao["Tipo"] = df_clientes["regiao"] if "regiao" in df_clientes.columns else "Sudeste"
        df_exibicao["Data"] = df_clientes["data"] if "data" in df_clientes.columns else str(date.today())
        df_exibicao["Responsável"] = df_clientes["responsavel"] if "responsavel" in df_clientes.columns else "Equipe Comercial"
        df_exibicao["Status"] = df_clientes["status"] if "status" in df_clientes.columns else "Ativo"
        df_exibicao["Ações"] = "Gerenciar / WhatsApp"
        
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado no banco de dados.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Gerenciamento focado em prospecção e qualificação de novos contatos.</p>", unsafe_allow_html=True)
    
    with st.form("form_novo_lead", clear_on_submit=True):
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            lead_nome = st.text_input("Nome do Lead *")
            lead_empresa = st.text_input("Empresa do Lead")
        with col_l2:
            lead_email = st.text_input("E-mail do Lead")
            lead_tel = st.text_input("WhatsApp / Telefone")
        
        btn_lead = st.form_submit_button("Cadastrar Lead")
        if btn_lead:
            if lead_nome:
                conn = conectar()
                conn.execute("""
                    INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, data, responsavel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (lead_nome, lead_empresa, lead_email, lead_tel, "Sudeste", "Lead", str(date.today()), "Prospecção"))
                conn.commit()
                conn.close()
                st.success("Lead cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Informe pelo menos o nome do lead.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔍 Lista de Leads Atuais")
    df_leads_only = df_clientes[df_clientes["status"] == "Lead"] if not df_clientes.empty and "status" in df_clientes.columns else pd.DataFrame()
    if not df_leads_only.empty:
        st.dataframe(df_leads_only[["nome", "empresa", "email", "telefone", "data"]], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead cadastrado no momento.")

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
            
        btn_pipe = st.form_submit_button("Adicionar Negócio")
        if btn_pipe:
            if p_titulo:
                conn = conectar()
                conn.execute("INSERT INTO pipeline (titulo, estagio, valor) VALUES (?, ?, ?)", (p_titulo, p_estagio, p_valor))
                conn.commit()
                conn.close()
                st.success("Negócio adicionado ao pipeline!")
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
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Registre e acompanhe as conversões e faturamento.</p>", unsafe_allow_html=True)

    with st.form("form_venda", clear_on_submit=True):
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            v_cliente = st.text_input("Nome do Cliente *")
        with col_v2:
            v_valor = st.number_input("Valor da Venda (R$)", min_value=0.0, step=100.0)
        with col_v3:
            v_data = st.text_input("Data da Venda", value=str(date.today()))
            
        btn_venda = st.form_submit_button("Registrar Venda")
        if btn_venda:
            if v_cliente and v_valor > 0:
                conn = conectar()
                conn.execute("INSERT INTO vendas (cliente, valor, data) VALUES (?, ?, ?)", (v_cliente, v_valor, v_data))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o cliente e um valor válido.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📜 Histórico de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas[["cliente", "valor", "data"]], use_container_width=True, hide_index=True)
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
                <div style="color: #94a3b8; font-size: 13px; margin-bottom: 15px;">Exportar todos os clientes e leads cadastrados.</div>
        """, unsafe_allow_html=True)
        if not df_clientes.empty:
            csv_clientes = df_clientes.to_csv(index=False).encode('utf-8')
            st.download_button("Baixar CSV de Clientes", data=csv_clientes, file_name="clientes_crm.csv", mime="text/csv")
        else:
            st.info("Sem dados para exportar.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 10px;">Relatório de Vendas</div>
                <div style="color: #94a3b8; font-size: 13px; margin-bottom: 15px;">Exportar histórico de faturamento e vendas.</div>
        """, unsafe_allow_html=True)
        if not df_vendas.empty:
            csv_vendas = df_vendas.to_csv(index=False).encode('utf-8')
            st.download_button("Baixar CSV de Vendas", data=csv_vendas, file_name="vendas_crm.csv", mime="text/csv")
        else:
            st.info("Sem dados para exportar.")
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e Conexões")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Conecte seu CRM com ferramentas externas de atendimento e automação.</p>", unsafe_allow_html=True)

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 10px;">💬 WhatsApp API</div>
                <div style="color: #94a3b8; font-size: 13px; margin-bottom: 15px;">Envie mensagens automáticas e dispare campanhas.</div>
        """, unsafe_allow_html=True)
        st.toggle("Ativar Integração WhatsApp", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_i2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 10px;">🌐 Webhooks / API Key</div>
                <div style="color: #94a3b8; font-size: 13px; margin-bottom: 15px;">Integre leads de landing pages diretamente.</div>
        """, unsafe_allow_html=True)
        st.text_input("Chave de API", value="crm_live_sec_99812736", type="password")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("### ⚙️ Configurações do Sistema")
    st.markdown("<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>Gerencie as preferências da sua conta e banco de dados.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Preferências Gerais</div>
        """, unsafe_allow_html=True)
        st.text_input("Nome da Organização", value="Comercial Alpha LTDA")
        st.text_input("E-mail do Administrador", value="admin@crm.com")
        st.selectbox("Moeda Padrão", ["Real (R$)", "Dólar ($)", "Euro (€)"])
        if st.button("Salvar Configurações"):
            st.success("Configurações salvas com sucesso!")
        st.markdown("</div>", unsafe_allow_html=True)
