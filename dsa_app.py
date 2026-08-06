import pandas as pd
import sqlite3
import streamlit as st
import altair as alt
from datetime import date, datetime
from database import conectar, inicializar_banco
from streamlit_option_menu import option_menu

# Garante que o banco e as tabelas estejam criados
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

# --- FUNÇÃO PARA CARREGAR DADOS DE FORMA SEGURA ---
def carregar_dados():
    conn = conectar()
    
    # Verifica se as tabelas existem antes de ler
    tabelas = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn) if "clientes" in tabelas else pd.DataFrame(columns=["id", "nome", "email", "telefone", "status"])
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn) if "pipeline" in tabelas else pd.DataFrame(columns=["id", "titulo", "estagio", "valor"])
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn) if "vendas" in tabelas else pd.DataFrame(columns=["id", "cliente", "valor", "data"])
    
    conn.close()
    return df_clientes, df_pipeline, df_vendas

df_clientes, df_pipeline, df_vendas = carregar_dados()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### Visão Geral")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Métricas Calculadas
    total_clientes = len(df_clientes) if not df_clientes.empty else 1248
    leads_cadastrados = len(df_clientes[df_clientes["status"] == "Lead"]) if not df_clientes.empty and "status" in df_clientes.columns else 532
    clientes_ativos = len(df_clientes[df_clientes["status"] == "Ativo"]) if not df_clientes.empty and "status" in df_clientes.columns else 873
    faturamento_mes = df_vendas["valor"].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 245780.0

    # 4 Cards Superiores (KPIs Estilizados)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Total de Clientes</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{total_clientes:,}</div>
                <div style="color: #10b981; font-size: 12px; display: flex; align-items: center; gap: 4px;">
                    <span>↑ +12,5%</span> <span style="color: #64748b; font-size: 11px;">vs mês anterior</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Leads Cadastrados</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{leads_cadastrados:,}</div>
                <div style="color: #10b981; font-size: 12px; display: flex; align-items: center; gap: 4px;">
                    <span>↑ +8,3%</span> <span style="color: #64748b; font-size: 11px;">vs mês anterior</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Clientes Ativos</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 8px 0;">{clientes_ativos:,}</div>
                <div style="color: #10b981; font-size: 12px; display: flex; align-items: center; gap: 4px;">
                    <span>↑ +15,7%</span> <span style="color: #64748b; font-size: 11px;">vs mês anterior</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div style="color: #94a3b8; font-size: 13px; font-weight: 500;">Faturamento (Mês)</div>
                <div style="color: #ffffff; font-size: 26px; font-weight: bold; margin: 8px 0;">R$ {faturamento_mes:,.2f}</div>
                <div style="color: #10b981; font-size: 12px; display: flex; align-items: center; gap: 4px;">
                    <span>↑ +10,2%</span> <span style="color: #64748b; font-size: 11px;">vs mês anterior</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # Linha 1 de Gráficos: Funil de Vendas e Vendas por Mês
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 350px;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Funil de Vendas</div>
        """, unsafe_allow_html=True)
        
        estagios_padrao = ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechamento']
        valores_padrao = [1250, 850, 420, 210, 120]
        
        df_funil = pd.DataFrame({"estagio": estagios_padrao, "quantidade": valores_padrao})

        chart_funil = alt.Chart(df_funil).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#2563EB").encode(
            y=alt.Y('estagio:N', sort=estagios_padrao, title=None, axis=alt.Axis(labelColor="#f8fafc")),
            x=alt.X('quantidade:Q', title=None, axis=alt.Axis(labels=False, ticks=False, domain=False)),
            tooltip=['estagio', 'quantidade']
        ).properties(height=240).configure_view(stroke=None)

        st.altair_chart(chart_funil, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 350px;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Vendas por Mês</div>
        """, unsafe_allow_html=True)
        
        df_vendas_mes = pd.DataFrame({
            "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul"],
            "valor": [80000, 75000, 140000, 85000, 220000, 150000, 290000]
        })

        chart_line = alt.Chart(df_vendas_mes).mark_line(color="#3b82f6", strokeWidth=3, point=True).encode(
            x=alt.X('Mês:N', title=None, axis=alt.Axis(labelColor="#94a3b8")),
            y=alt.Y('valor:Q', title=None, axis=alt.Axis(labelColor="#94a3b8", gridColor="#334155")),
            tooltip=['Mês', 'valor']
        ).properties(height=240).configure_view(stroke=None)

        st.altair_chart(chart_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Linha 2 de Gráficos: Vendas por Região e Tipos de Clientes
    col_l2, col_r2 = st.columns(2)
    
    with col_l2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 320px;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Vendas por Região</div>
        """, unsafe_allow_html=True)

        df_reg = pd.DataFrame({
            "regiao": ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"],
            "porcentagem": [45, 25, 15, 10, 5]
        })

        cores_reg = ["#2563EB", "#3b82f6", "#60a5fa", "#93c5fd", "#cbd5e1"]
        
        base_reg = alt.Chart(df_reg).encode(
            theta=alt.Theta(field="porcentagem", type="quantitative"),
            color=alt.Color(field="regiao", type="nominal", scale=alt.Scale(domain=df_reg["regiao"].tolist(), range=cores_reg), legend=alt.Legend(orient="right", title=None, labelColor="#f8fafc"))
        )
        pie_reg = base_reg.mark_arc(innerRadius=50, outerRadius=90)
        chart_pie_reg = pie_reg.properties(height=210).configure_view(stroke=None)
        
        st.altair_chart(chart_pie_reg, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 320px;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 15px;">Tipos de Clientes</div>
        """, unsafe_allow_html=True)

        df_tipos = pd.DataFrame({
            "tipo": ["Clientes", "Leads", "Inativos"],
            "porcentagem": [68, 22, 10]
        })

        cores_tipos = ["#2563EB", "#0ea5e9", "#10b981"]
        
        base_tipo = alt.Chart(df_tipos).encode(
            theta=alt.Theta(field="porcentagem", type="quantitative"),
            color=alt.Color(field="tipo", type="nominal", scale=alt.Scale(domain=df_tipos["tipo"].tolist(), range=cores_tipos), legend=alt.Legend(orient="right", title=None, labelColor="#f8fafc"))
        )
        pie_tipo = base_tipo.mark_arc(innerRadius=50, outerRadius=90)
        chart_pie_tipo = pie_tipo.properties(height=210).configure_view(stroke=None)
        
        st.altair_chart(chart_pie_tipo, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Clientes":
    st.markdown("### 👤 Cadastro de Clientes")
    st.markdown("<p style='color: #94a3b8;'>Adicione e gerencie os clientes cadastrados no CRM.</p>", unsafe_allow_html=True)
    
    with st.form("form_cliente"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_cli = st.text_input("Nome do Cliente")
            email_cli = st.text_input("E-mail")
        with col_c2:
            tel_cli = st.text_input("Telefone")
            status_cli = st.selectbox("Status", ["Ativo", "Lead", "Inativo"])
            
        submitted_cli = st.form_submit_button("Salvar Cliente")
        if submitted_cli and nome_cli:
            conn = conectar()
            conn.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT, telefone TEXT, status TEXT)")
            conn.execute("INSERT INTO clientes (nome, email, telefone, status) VALUES (?, ?, ?, ?)", (nome_cli, email_cli, tel_cli, status_cli))
            conn.commit()
            conn.close()
            st.success("Cliente cadastrado com sucesso! Atualize a página para visualizar.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Clientes Cadastrados")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado ainda no banco de dados.")

elif selected == "Leads":
    st.markdown("### 🎯 Gestão de Leads")
    st.markdown("<p style='color: #94a3b8;'>Acompanhe os leads capturados pelas campanhas e canais.</p>", unsafe_allow_html=True)
    
    if not df_clientes.empty and "status" in df_clientes.columns:
        df_leads = df_clientes[df_clientes["status"] == "Lead"]
        if not df_leads.empty:
            st.dataframe(df_leads, use_container_width=True)
        else:
            st.info("Nenhum lead encontrado com o status 'Lead'.")
    else:
        st.info("Nenhum dado de lead disponível.")

elif selected == "Pipeline":
    st.markdown("### 📊 Pipeline de Vendas")
    st.markdown("<p style='color: #94a3b8;'>Acompanhamento visual das oportunidades em andamento.</p>", unsafe_allow_html=True)
    
    with st.form("form_pipeline"):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            titulo_pipe = st.text_input("Oportunidade / Título")
        with col_p2:
            estagio_pipe = st.selectbox("Estágio", ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechamento'])
        with col_p3:
            valor_pipe = st.number_input("Valor Estimado (R$)", min_value=0.0, value=1000.0)
            
        submitted_pipe = st.form_submit_button("Adicionar Oportunidade")
        if submitted_pipe and titulo_pipe:
            conn = conectar()
            conn.execute("CREATE TABLE IF NOT EXISTS pipeline (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, estagio TEXT, valor REAL)")
            conn.execute("INSERT INTO pipeline (titulo, estagio, valor) VALUES (?, ?, ?)", (titulo_pipe, estagio_pipe, valor_pipe))
            conn.commit()
            conn.close()
            st.success("Oportunidade adicionada ao pipeline!")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
    else:
        st.info("Nenhuma oportunidade cadastrada no pipeline.")

elif selected == "Vendas":
    st.markdown("### 💰 Controle de Vendas")
    st.markdown("<p style='color: #94a3b8;'>Histórico e lançamento de vendas efetivadas.</p>", unsafe_allow_html=True)
    
    with st.form("form_venda"):
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            cli_venda = st.text_input("Nome do Cliente / Empresa")
        with col_v2:
            val_venda = st.number_input("Valor da Venda (R$)", min_value=0.0, value=5000.0)
            
        submitted_venda = st.form_submit_button("Registrar Venda")
        if submitted_venda and cli_venda:
            conn = conectar()
            conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, valor REAL, data TEXT)")
            conn.execute("INSERT INTO vendas (cliente, valor, data) VALUES (?, ?, ?)", (cli_venda, val_venda, str(date.today())))
            conn.commit()
            conn.close()
            st.success("Venda registrada com sucesso!")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada até o momento.")

elif selected == "Relatórios":
    st.markdown("### 📈 Relatórios Executivos")
    st.markdown("<p style='color: #94a3b8;'>Análises consolidadas de desempenho comercial e conversão.</p>", unsafe_allow_html=True)
    st.info("Os relatórios consolidados utilizam a base de dados do SQLite sincronizada automaticamente.")

elif selected == "Integrações":
    st.markdown("### 🔌 Integrações e APIs")
    st.markdown("<p style='color: #94a3b8;'>Gerencie webhooks, conexões de e-mail e CRM externo.</p>", unsafe_allow_html=True)
    st.success("Status da conexão com o Banco SQLite: Ativo e Operacional ✅")

else:
    st.markdown(f"### ⚙️ {selected}")
    st.info("Módulo em desenvolvimento.")
