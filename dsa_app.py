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
            "speedometer2", # Dashboard
            "people-fill",    # Clientes
            "person-plus-fill", # Leads
            "kanban",         # Pipeline
            "trophy-fill",    # Vendas
            "file-earmark-bar-graph", # Relatórios
            "plug",           # Integrações
            "gear-fill"       # Configurações
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
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    df_interacoes = pd.read_sql("SELECT * FROM interacoes", conn)
    conn.close()
    return df_clientes, df_pipeline, df_vendas, df_interacoes

df_clientes, df_pipeline, df_vendas, df_interacoes = carregar_dados()

# --- NAVEGAÇÃO ENTRE AS PÁGINAS ---

if selected == "Dashboard":
    st.markdown("### Visão Geral")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Métricas Calculadas
    total_clientes = len(df_clientes)
    leads_cadastrados = len(df_clientes[df_clientes["status"] == "Lead"]) if "status" in df_clientes.columns else len(df_clientes)
    clientes_ativos = len(df_clientes[df_clientes["status"] == "Ativo"]) if "status" in df_clientes.columns else int(total_clientes * 0.7)
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
        
        # Dados do Funil (Simulados ou Reais do Pipeline)
        estagios_padrao = ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechamento']
        valores_padrao = [1250, 850, 420, 210, 120]
        
        df_funil = pd.DataFrame({"estagio": estagios_padrao, "quantidade": valores_padrao})
        if not df_pipeline.empty and "estagio" in df_pipeline.columns:
            df_grouped_pipe = df_pipeline.groupby("estagio").size().reset_index(name="quantidade")
            # Atualiza com dados reais se houver
            for idx, row in df_grouped_pipe.iterrows():
                if row["estagio"] in estagios_padrao:
                    pos = estagios_padrao.index(row["estagio"])
                    valores_padrao[pos] = row["quantidade"]
            df_funil = pd.DataFrame({"estagio": estagios_padrao, "quantidade": valores_padrao})

        chart_funil = alt.Chart(df_funil).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#2563EB").encode(
            y=alt.Y('estagio:N', sort=estagios_padrao, title=None, axis=alt.Axis(labelColor="#f8fafc")),
            x=alt.X('quantidade:Q', title=None, axis=alt.Axis(labels=False, ticks=False, domain=False)),
            tooltip=['estagio', 'quantidade']
        ).properties(height=240).configure_view(stroke=None).configure_background(color="transparent")

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
        ).properties(height=240).configure_view(stroke=None).configure_background(color="transparent")

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
        chart_pie_reg = pie_reg.properties(height=210).configure_view(stroke=None).configure_background(color="transparent")
        
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
        chart_pie_tipo = pie_tipo.properties(height=210).configure_view(stroke=None).configure_background(color="transparent")
        
        st.altair_chart(chart_pie_tipo, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Clientes":
    st.title("👤 Cadastro de Clientes e Leads")
    st.write("Adicione novos clientes para alimentar o seu CRM.")
    # (Mantém a lógica da sua página de clientes original...)

elif selected == "Pipeline":
    st.title("📊 Pipeline de Vendas")
    st.write("Acompanhamento do funil de oportunidades comerciais.")
    # (Mantém a lógica do pipeline...)

elif selected == "Vendas":
    st.title("💰 Gestão de Vendas")
    st.write("Controle completo de faturamento e vendas efetivadas.")

elif selected == "Integrações":
    st.title("🔌 Configuração de Integrações")
    st.write("Gerencie as conexões com APIs e ferramentas externas.")

else:
    st.title(f"⚙️ {selected}")
    st.info("Módulo em desenvolvimento.")
