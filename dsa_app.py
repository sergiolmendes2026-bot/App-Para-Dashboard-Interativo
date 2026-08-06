import pandas as pd
import sqlite3
import streamlit as st
import altair as alt
from datetime import date
from database import conectar, inicializar_banco
from streamlit_option_menu import option_menu

# Garante que o banco e as tabelas estejam criados
inicializar_banco()

st.set_page_config(
    page_title="Dashboard CRM de Vendas", page_icon="📊", layout="wide"
)

# --- BARRA LATERAL COM MENU E ÍCONES ---
with st.sidebar:
    st.markdown("### 🚀 dsa app")
    selected = option_menu(
        menu_title=None,
        options=[
            "Clientes",
            "Vendas",
            "Pipeline",
            "Interações",
            "Integrações",
            "Dashboard",
        ],
        icons=[
            "people-fill",     # Clientes
            "trophy-fill",     # Vendas
            "kanban",          # Pipeline
            "headset",         # Interações
            "plug",            # Integrações
            "speedometer2",    # Dashboard
        ],
        menu_icon="cast",
        default_index=5,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#2563EB", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0px",
                "--hover-color": "#262730",
            },
            "nav-link-selected": {
                "background-color": "#2563EB",
                "color": "#FFFFFF",
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
    st.title("📊 Dashboard Executivo - CRM Corporativo")
    st.write("Análise avançada de indicadores comerciais, faturamento e distribuição de clientes.")

    total_clientes = len(df_clientes)
    total_vendas_valor = df_vendas["valor"].sum() if not df_vendas.empty and "valor" in df_vendas.columns else 0.0
    total_oportunidades = len(df_pipeline)
    pipeline_valor = df_pipeline["valor"].sum() if not df_pipeline.empty and "valor" in df_pipeline.columns else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Clientes", total_clientes)
    with col2:
        st.metric("Faturamento Total", f"R$ {total_vendas_valor:,.2f}")
    with col3:
        st.metric("Oportunidades no Pipeline", total_oportunidades)
    with col4:
        st.metric("Valor em Pipeline", f"R$ {pipeline_valor:,.2f}")

    st.divider()

    # Linha 1 de Gráficos: Linha de Faturamento e Pizza por Região com Cores Personalizadas e Porcentagem
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Linha de Faturamento por Mês")
        if not df_vendas.empty and "valor" in df_vendas.columns:
            df_vendas_line = df_vendas.copy()
            if "data_venda" not in df_vendas_line.columns:
                df_vendas_line["Mês"] = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"][:len(df_vendas_line)] if len(df_vendas_line) <= 6 else "Atual"
                df_vendas_grouped = df_vendas_line.groupby("Mês")["valor"].sum().reset_index()
                
                chart_line = alt.Chart(df_vendas_grouped).mark_line(color="#2563EB", strokeWidth=3, point=True).encode(
                    x=alt.X('Mês:N', title=None),
                    y=alt.Y('valor:Q', title="Faturamento (R$)"),
                    tooltip=['Mês', 'valor']
                ).properties(height=280)
                st.altair_chart(chart_line, use_container_width=True)
            else:
                st.info("Dados de faturamento temporal carregados.")
        else:
            st.info("Insira vendas para visualizar a linha de faturamento.")

    with col_right:
        st.subheader("🍕 Distribuição de Clientes por Região (%)")
        if not df_clientes.empty and "regiao" in df_clientes.columns:
            df_regiao = df_clientes[df_clientes["regiao"] != ""].groupby("regiao").size().reset_index(name="quantidade")
            if not df_regiao.empty:
                total_reg = df_regiao["quantidade"].sum()
                df_regiao["porcentagem"] = df_regiao["quantidade"] / total_reg
                df_regiao["rotulo"] = df_regiao["porcentagem"].apply(lambda p: f"{p*100:.1f}%")

                # Mapeamento fixo de cores corporativas para as 5 regiões do Brasil
                regioes_lista = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
                cores_lista = ["#2563EB", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"]

                base = alt.Chart(df_regiao).encode(
                    theta=alt.Theta(field="quantidade", type="quantitative"),
                    color=alt.Color(
                        field="regiao", 
                        type="nominal", 
                        scale=alt.Scale(domain=regioes_lista, range=cores_lista), 
                        legend=alt.Legend(title="Regiões")
                    )
                )

                pie = base.mark_arc(innerRadius=65, outerRadius=110)
                text = base.mark_text(radius=85, size=13, fontWeight="bold", color="white").encode(
                    text=alt.Text(field="rotulo", type="nominal")
                )

                chart_pie = (pie + text).properties(height=280)
                st.altair_chart(chart_pie, use_container_width=True)
            else:
                st.info("Cadastre a região dos clientes para visualizar o gráfico.")
        else:
            st.info("Nenhum dado de região disponível.")

    st.divider()

    # Linha 2 de Gráficos: Funil de Vendas e Vendas por Produto
    col_l2, col_r2 = st.columns(2)
    
    with col_l2:
        st.subheader("🔻 Funil de Vendas (Pipeline)")
        if not df_pipeline.empty and "estagio" in df_pipeline.columns:
            df_pipe_grouped = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
            
            chart_funil = alt.Chart(df_pipe_grouped).mark_bar(color="#16A34A", cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                y=alt.Y('estagio:N', sort=['Prospecção', 'Qualificação', 'Proposta', 'Fechamento'], title=None),
                x=alt.X('valor:Q', title="Valor (R$)"),
                tooltip=['estagio', 'valor']
            ).properties(height=280)
            
            st.altair_chart(chart_funil, use_container_width=True)
        else:
            st.info("Nenhuma oportunidade no pipeline registrada.")

    with col_r2:
        st.subheader("💰 Vendas por Produto / Serviço")
        if not df_vendas.empty and "produto_servico" in df_vendas.columns:
            df_vendas_grouped = df_vendas.groupby("produto_servico")["valor"].sum().reset_index()
            
            chart_vendas = alt.Chart(df_vendas_grouped).mark_bar(color="#F59E0B", cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                y=alt.Y('produto_servico:N', sort='-x', title=None),
                x=alt.X('valor:Q', title="Valor (R$)"),
                tooltip=['produto_servico', 'valor']
            ).properties(height=280)
            
            st.altair_chart(chart_vendas, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada.")

elif selected == "Clientes":
    st.title("👤 Cadastro de Clientes e Leads")
    st.write("Adicione novos clientes para alimentar o seu CRM e a sua operação comercial.")

    with st.form("form_cad_cliente", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            nome = st.text_input("Nome do Contato *")
            empresa = st.text_input("Nome da Empresa")
            email = st.text_input("E-mail")
            
        with col_b:
            telefone = st.text_input("Telefone / WhatsApp")
            regiao = st.selectbox("Região", ["Selecione...", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
            status_cliente = st.selectbox("Status do Cliente", ["Ativo", "Lead", "Inativo", "Fechado"])
            data_cadastro = st.date_input("Data de Cadastro", value=date.today())
            
        btn_salvar_cliente = st.form_submit_button("Salvar Cliente")
        
        if btn_salvar_cliente:
            if nome:
                regiao_valida = regiao if regiao != "Selecione..." else ""
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, data_cadastro)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (nome, empresa, email, telefone, regiao_valida, status_cliente, str(data_cadastro)))
                    conn.commit()
                    conn.close()
                    st.success(f"Cliente '{nome}' cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    try:
                        conn = conectar()
                        cursor = conn.cursor()
                        cursor.execute("ALTER TABLE clientes ADD COLUMN status TEXT;")
                        cursor.execute("""
                            INSERT INTO clientes (nome, empresa, email, telefone, regiao, status, data_cadastro)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (nome, empresa, email, telefone, regiao_valida, status_cliente, str(data_cadastro)))
                        conn.commit()
                        conn.close()
                        st.success(f"Cliente '{nome}' cadastrado com sucesso!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro ao salvar no banco de dados: {err}")
            else:
                st.warning("O campo 'Nome do Contato *' é obrigatório.")

    st.divider()
    st.subheader("📋 Tabela de Clientes (Estilo CRM)")
    
    if not df_clientes.empty:
        tabela_crm = pd.DataFrame()
        tabela_crm["Avatar"] = df_clientes["nome"].apply(lambda x: "".join([n[0].upper() for n in str(x).split()[:2]]))
        tabela_crm["Nome"] = df_clientes["nome"]
        tabela_crm["Empresa"] = df_clientes["empresa"] if "empresa" in df_clientes.columns else "-"
        tabela_crm["Região"] = df_clientes["regiao"] if "regiao" in df_clientes.columns else "-"
        tabela_crm["Status"] = df_clientes["status"] if "status" in df_clientes.columns else "Ativo"
            
        if not df_interacoes.empty and "cliente" in df_interacoes.columns:
            ultimas = df_interacoes.groupby("cliente")["tipo"].last().reset_index()
            ultimas.columns = ["Nome", "Última Interação"]
            tabela_crm = tabela_crm.merge(ultimas, on="Nome", how="left")
            tabela_crm["Última Interação"] = tabela_crm["Última Interação"].fillna("Nenhuma")
        else:
            tabela_crm["Última Interação"] = "Nenhuma"
            
        if not df_vendas.empty and "cliente" in df_vendas.columns and "valor" in df_vendas.columns:
            vendas_soma = df_vendas.groupby("cliente")["valor"].sum().reset_index()
            vendas_soma.columns = ["Nome", "Valor Total"]
            tabela_crm = tabela_crm.merge(vendas_soma, on="Nome", how="left")
            tabela_crm["Valor Total"] = tabela_crm["Valor Total"].fillna(0.0).apply(lambda v: f"R$ {v:,.2f}")
        else:
            tabela_crm["Valor Total"] = "R$ 0,00"

        st.dataframe(tabela_crm, use_container_width=True, hide_index=True)
        
        if "telefone" in df_clientes.columns and not df_clientes["telefone"].isnull().all():
            st.markdown("### 💬 Ações Rápidas - WhatsApp")
            cliente_selecionado = st.selectbox("Selecione o cliente para enviar mensagem:", df_clientes["nome"].tolist())
            fone_cliente = df_clientes.loc[df_clientes["nome"] == cliente_selecionado, "telefone"].values[0]
            
            if fone_cliente:
                fone_limpo = "".join(filter(str.isdigit, str(fone_cliente)))
                msg_padrao = f"Olá {cliente_selecionado}, tudo bem? Entramos em contato pelo CRM da nossa empresa."
                link_wa = f"https://wa.me/55{fone_limpo}?text={msg_padrao.replace(' ', '%20')}"
                st.markdown(f'''
                    <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                        <button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; display: inline-flex; align-items: center; justify-content: center; gap: 12px; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <svg width="22" height="22" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: block; vertical-align: middle; flex-shrink: 0;">
                                <path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.558 6.558 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.348.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.342-.116-.008-.249-.008-.383-.008a.749.749 0 0 0-.543.25c-.187.198-.716.7-.716 1.707 0 1.008 1.034 1.981 1.177 2.115.143.133 2.031 3.102 4.922 4.349.688.297 1.226.474 1.646.607.692.22 1.32.189 1.817.115.556-.083 1.17-.478 1.338-.94.168-.46.168-.855.117-.94-.05-.085-.183-.138-.38-.235z" fill="white"/>
                            </svg>
                            Falar no WhatsApp
                        </button>
                    </a>
                ''', unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif selected == "Pipeline":
    st.title("📊 Pipeline de Vendas")
    st.write("Acompanhamento do funil de oportunidades comerciais.")

    with st.form("form_pipeline", clear_on_submit=True):
        st.subheader("Adicionar Oportunidade ao Pipeline")
        col1, col2 = st.columns(2)
        with col1:
            clientes_nomes = df_clientes["nome"].tolist() if not df_clientes.empty else []
            cliente_op = st.selectbox("Cliente *", clientes_nomes if clientes_nomes else ["Cadastre um cliente primeiro"])
            titulo_op = st.text_input("Título da Oportunidade *")
        with col2:
            estagio_op = st.selectbox("Estágio do Funil", ["Prospecção", "Qualificação", "Proposta", "Fechamento"])
            valor_op = st.number_input("Valor Estimado (R$)", min_value=0.0, step=100.0)

        btn_salvar_pipe = st.form_submit_button("Salvar Oportunidade")
        
        if btn_salvar_pipe:
            if titulo_op and clientes_nomes:
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO pipeline (cliente, titulo, estagio, valor)
                        VALUES (?, ?, ?, ?)
                    """, (cliente_op, titulo_op, estagio_op, valor_op))
                    conn.commit()
                    conn.close()
                    st.success("Oportunidade adicionada ao pipeline com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar oportunidade: {e}")
            else:
                st.warning("Preencha o título e certifique-se de ter clientes cadastrados.")

    st.divider()
    st.subheader("Oportunidades Atuais")
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
    else:
        st.info("Nenhuma oportunidade no pipeline registrada.")

elif selected == "Interações":
    st.title("💬 Histórico de Interações")
    st.write("Acompanhe e registre os contatos realizados com os clientes.")

    with st.form("form_interacao", clear_on_submit=True):
        st.subheader("Registrar Nova Interação")
        clientes_nomes = df_clientes["nome"].tolist() if not df_clientes.empty else []
        cliente_int = st.selectbox("Cliente *", clientes_nomes if clientes_nomes else ["Cadastre um cliente primeiro"])
        tipo_contato = st.selectbox("Tipo de Contato", ["WhatsApp", "Ligação", "E-mail", "Reunião"])
        descricao_int = st.text_area("Descrição da Conversa / Observações")

        btn_salvar_int = st.form_submit_button("Salvar Interação")

        if btn_salvar_int:
            if clientes_nomes:
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO interacoes (cliente, tipo, descricao)
                        VALUES (?, ?, ?)
                    """, (cliente_int, tipo_contato, descricao_int))
                    conn.commit()
                    conn.close()
                    st.success("Interação registrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar interação: {e}")
            else:
                st.warning("Cadastre um cliente antes de registrar interações.")

    st.divider()
    st.subheader("Interações Registradas")
    if not df_interacoes.empty:
        st.dataframe(df_interacoes, use_container_width=True)
    else:
        st.info("Nenhuma interação registrada.")

elif selected == "Vendas":
    st.title("💰 Gestão de Vendas")
    st.write("Controle completo de faturamento e vendas efetivadas.")

    with st.form("form_venda", clear_on_submit=True):
        st.subheader("Registrar Nova Venda")
        col1, col2 = st.columns(2)
        with col1:
            clientes_nomes = df_clientes["nome"].tolist() if not df_clientes.empty else []
            cliente_venda = st.selectbox("Cliente *", clientes_nomes if clientes_nomes else ["Cadastre um cliente primeiro"])
            produto_venda = st.text_input("Produto / Serviço *")
        with col2:
            valor_venda = st.number_input("Valor da Venda (R$)", min_value=0.0, step=100.0)
            status_venda = st.selectbox("Status", ["Concluída", "Pendente", "Cancelada"])

        btn_salvar_venda = st.form_submit_button("Salvar Venda")

        if btn_salvar_venda:
            if produto_venda and clientes_nomes:
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO vendas (cliente, produto_servico, valor, status)
                        VALUES (?, ?, ?, ?)
                    """, (cliente_venda, produto_venda, valor_venda, status_venda))
                    conn.commit()
                    conn.close()
                    st.success("Venda registrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar venda: {e}")
            else:
                st.warning("Preencha o produto/serviço e certifique-se de ter clientes cadastrados.")

    st.divider()
    st.subheader("Histórico de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda cadastrada.")

elif selected == "Integrações":
    st.title("🔌 Configuração de Integrações")
    st.write("Gerencie as conexões com APIs e ferramentas externas.")
    st.info("Módulo preparado para futuras integrações (WhatsApp API, Webhooks, Gateway de Pagamento).")
