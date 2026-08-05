import streamlit as st
import datetime
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas existem
inicializar_banco()

st.set_page_config(page_title="Cadastro de Clientes - CRM", page_icon="👤", layout="wide")

st.title("👤 Cadastro de Clientes e Leads")
st.write("Adicione novos clientes para alimentar o seu CRM e a sua operação comercial.")

with st.form("form_cliente"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Contato *")
        empresa = st.text_input("Nome da Empresa")
        email = st.text_input("E-mail")
        
    with col2:
        telefone = st.text_input("Telefone / WhatsApp")
        regiao = st.selectbox("Região", ["Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"])
        data_cadastro = st.date_input("Data de Cadastro", datetime.date.today())
        
    submitted = st.form_submit_button("Salvar Cliente")
    
    if submitted:
        if nome.strip() == "":
            st.error("O campo 'Nome do Contato' é obrigatório!")
        else:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nome, empresa, email, telefone, regiao, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, empresa, email, telefone, regiao, str(data_cadastro)))
            conn.commit()
            conn.close()
            st.success(f"Cliente '{nome}' cadastrado com sucesso!")

# Exibir clientes cadastrados recentemente
st.markdown("---")
st.subheader("📋 Clientes Cadastrados Recentemente")

conn = conectar()
try:
    df_clientes = st.dataframe(
        conn.execute("SELECT id, nome, empresa, email, telefone, regiao, data_cadastro FROM clientes ORDER BY id DESC").fetchall(),
        use_container_width=True,
        column_config={
            "id": "ID",
            "nome": "Nome",
            "empresa": "Empresa",
            "email": "E-mail",
            "telefone": "Telefone",
            "regiao": "Região",
            "data_cadastro": "Data Cadastro"
        }
    )
except Exception as e:
    st.info("Ainda não há clientes cadastrados.")
conn.close()
