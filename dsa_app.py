import pandas as pd
import sqlite3
import streamlit as st
from database import conectar, inicializar_banco
from streamlit_option_menu import option_menu

# Garante que o banco e as tabelas estejam criados
inicializar_banco()

st.set_page_config(
    page_title="Dashboard CRM de Vendas", page_icon="📊", layout="wide"
)

# --- BARRA LATERAL COM MENU MODERNIZADO ---
with st.sidebar:
    st.markdown("### 🚀 dsa app")
    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Cadastro de Clientes",
            "Pipeline de Vendas",
            "Interações",
            "Vendas",
            "Integrações",
        ],
        icons=[
            "speedometer2",
            "people-fill",
            "kanban-fill",
            "chat-dots-fill",
            "cart-fill",
            "plug-fill",
        ],
        menu_icon="cast",
        default_index=1,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#ff4b4b", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0px",
                "--hover-color": "#262730",
            },
            "nav-link-selected": {
                "background-color": "#ff4b4b",
                "color": "white",
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
    st.title("📊 Dashboard Executivo - CRM de Vendas")
    st.write("Visão geral dos indicadores de clientes, pipeline, interações e faturamento.")

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

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("💰 Vendas por Produto / Serviço")
        if not df_vendas.empty and "produto_servico" in df_vendas.columns:
            df_vendas_grouped = df_vendas.groupby("produto_servico")["valor"].sum().reset_index()
            st.dataframe(df_vendas_grouped, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada para exibir.")

    with col_right:
        st.subheader("📈 Oportunidades por Estágio")
        if not df_pipeline.empty and "estagio" in df_pipeline.columns:
            df_pipe_grouped = df_pipeline.groupby("estagio")["valor"].sum().reset_index()
            st.dataframe(df_pipe_grouped, use_container_width=True)
        else:
            st.info("Nenhuma oportunidade no pipeline para exibir.")

    st.divider()
    st.subheader("👥 Clientes Cadastrados Recentemente")
    if not df_clientes.empty:
        colunas_exibir = [col for col in ["nome", "empresa", "email", "telefone", "regiao", "data_cadastro"] if col in df_clientes.columns]
        st.dataframe(df_clientes[colunas_exibir], use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")

elif selected == "Cadastro de Clientes":
    st.title("👥 Cadastro de Clientes")
    st.write("Gerencie e adicione novos registros de clientes ao seu CRM.")

    with st.form("form_cad_cliente", clear_on_submit=True):
        st.subheader("Adicionar Novo Cliente")
        col_a, col_b = st.columns(2)
        with col_a:
            nome = st.text_input("Nome do Cliente *")
            empresa = st.text_input("Empresa")
            email = st.text_input("E-mail")
        with col_b:
            telefone = st.text_input("Telefone / WhatsApp (ex: 11999999999)")
            regiao = st.text_input("Região / Cidade")
            
        btn_salvar_cliente = st.form_submit_button("Salvar Cliente")
        
        if btn_salvar_cliente:
            if nome:
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO clientes (nome, empresa, email, telefone, regiao)
                        VALUES (?, ?, ?, ?, ?)
                    """, (nome, empresa, email, telefone, regiao))
                    conn.commit()
                    conn.close()
                    st.success(f"Cliente '{nome}' cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco de dados: {e}")
            else:
                st.warning("O campo 'Nome do Cliente' é obrigatório.")

    st.divider()
    st.subheader("Base de Clientes Cadastrados")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
        
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
                        <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-weight:bold; display: inline-flex; align-items: center; justify-content: center; gap: 12px; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: block; vertical-align: middle; flex-shrink: 0;">
                                <path d="M17.472 14.382C17.158 14.225 15.632 13.473 15.348 13.369C15.064 13.264 14.857 13.212 14.65 13.522C14.443 13.832 13.847 14.526 13.665 14.741C13.483 14.956 13.301 14.982 12.987 14.825C12.673 14.668 11.658 14.337 10.457 13.265C9.501 12.415 8.861 11.365 8.679 11.051C8.497 10.737 8.658 10.568 8.815 10.412C8.956 10.272 9.128 10.047 9.284 9.859C9.44 9.672 9.492 9.542 9.596 9.332C9.7 9.122 9.648 8.94 9.57 8.785C9.492 8.63 8.87 7.099 8.611 6.484C8.36 5.891 8.106 5.973 7.917 5.963C7.735 5.953 7.528 5.953 7.321 5.953C7.114 5.953 6.774 6.031 6.488 6.341C6.202 6.651 5.395 7.403 5.395 8.927C5.395 10.451 6.502 11.923 6.658 12.133C6.814 12.343 8.825 15.424 11.905 16.751C12.637 17.067 13.204 17.258 13.64 17.403C14.352 17.633 14.993 17.601 15.492 17.527C16.05 17.445 17.221 16.822 17.462 16.14C17.703 15.458 17.703 14.876 17.625 14.741C17.547 14.606 17.339 14.538 17.472 14.382Z" fill="white"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12C2 13.82 2.487 15.53 3.345 17L2 22L7.165 20.645C8.553 21.398 10.222 21.8 12 21.8C17.523 21.8 22 17.323 22 11.8C22 6.277 17.523 1.8 12 1.8V2ZM12 20.1C10.45 20.1 8.96 19.68 7.68 18.91L7.38 18.73L4.2 19.57L5.07 16.46L4.87 16.15C3.99 14.78 3.53 13.18 3.53 11.55C3.53 7.15 7.11 3.57 11.51 3.57C13.66 3.57 15.69 4.41 17.21 5.93C18.73 7.45 19.57 9.48 19.57 11.63C19.57 16.03 15.99 19.61 11.59 19.61L12 20.1Z" fill="white"/>
                            </svg>
                            Enviar Mensagem via WhatsApp
                        </button>
                    </a>
                ''', unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif selected == "Pipeline de Vendas":
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
