import streamlit as st
import sqlite3
import pandas as pd
from database import conectar, inicializar_banco

inicializar_banco()

st.set_page_config(page_title="Cadastro de Clientes - CRM", page_icon="👥", layout="wide")

st.title("👥 Cadastro de Clientes e Leads")
st.write("Adicione novos clientes para alimentar o seu CRM e a sua operação comercial.")

with st.form("form_cliente", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Contato *")
        empresa = st.text_input("Nome da Empresa")
        email = st.text_input("E-mail")
    with col2:
        telefone = st.text_input("Telefone / WhatsApp")
        regiao = st.selectbox("Região", ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
        data_cadastro = st.text_input("Data de Cadastro", value=pd.Timestamp.today().strftime("%Y-%m-%d"))
        
    submitted = st.form_submit_button("Salvar Cliente")
    
    if submitted:
        if not nome.strip():
            st.error("O campo Nome do Contato é obrigatório!")
        else:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nome, empresa, email, telefone, regiao, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, empresa, email, telefone, regiao, data_cadastro))
            conn.commit()
            conn.close()
            st.success("Cliente salvo com sucesso!")
            st.rerun()

st.divider()
st.subheader("📋 Clientes Cadastrados Recentemente")

conn = conectar()
df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
conn.close()

if not df_clientes.empty:
    whatsapp_ativo = st.session_state.get("whatsapp_ativo", False)
    
    for _, row in df_clientes.iterrows():
        cli_nome = row.get("nome", "Contato")
        cli_empresa = row.get("empresa", "Empresa não informada")
        cli_email = row.get("email", "E-mail não informado")
        cli_tel = row.get("telefone", "")
        cli_regiao = row.get("regiao", "")
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 3, 2])
            
            with c1:
                st.markdown(f"**{cli_nome}**")
                st.caption(f"Empresa: {cli_empresa} | Região: {cli_regiao}")
                
            with c2:
                st.markdown(f"📧 {cli_email}")
                st.markdown(f"📱 {cli_tel if cli_tel else 'Sem telefone'}")
                
            with c3:
                # Botão interativo do WhatsApp caso a integração esteja ativa e exista telefone
                if whatsapp_ativo and cli_tel:
                    tel_limpo = "".join(filter(str.isdigit, str(cli_tel)))
                    link_wa = f"https://wa.me/55{tel_limpo}"
                    
                    st.markdown(f"""
                        <a href="{link_wa}" target="_blank" style="
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            gap: 8px;
                            background-color: #262730;
                            color: #ffffff;
                            padding: 0.5rem 1rem;
                            border-radius: 0.5rem;
                            border: 1px solid rgba(250, 250, 250, 0.2);
                            text-decoration: none;
                            font-weight: 400;
                            width: 100%;
                            box-sizing: border-box;
                        ">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" style="vertical-align: middle;" />
                            Abrir no WhatsApp
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    st.info("WhatsApp inativo ou sem tel")
else:
    st.info("Nenhum cliente cadastrado recentemente.")
