import streamlit as st
import sqlite3
import pandas as pd
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas existem
inicializar_banco()

st.set_page_config(page_title="Histórico de Interações - CRM", page_icon="💬", layout="wide")

st.title("💬 Histórico de Interações")
st.write("Registre ligações, reuniões, e-mails ou anotações importantes com os clientes.")

# Buscar clientes cadastrados para associar à interação
conn = conectar()
cursor = conn.cursor()
cursor.execute("SELECT id, nome, empresa FROM clientes")
clientes = cursor.fetchall()
conn.close()

if not clientes:
    st.warning("Nenhum cliente cadastrado ainda. Cadastre um cliente na página anterior antes de registrar interações.")
else:
    # Mapear clientes para seleção amigável
    clientes_dict = {f"{c[1]} ({c[2]})" if c[2] else c[1]: c[0] for c in clientes}
    
    with st.form("form_interacao"):
        st.subheader("Nova Interação")
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_selecionado = st.selectbox("Selecione o Cliente", options=list(clientes_dict.keys()))
            tipo_contato = st.selectbox("Tipo de Contato", ["Ligação", "Reunião", "E-mail", "WhatsApp", "Outro"])
            
        with col2:
            data_interacao = st.date_input("Data da Interação")
            
        descricao = st.text_area("Descrição / Notas da Conversa *")
            
        submitted = st.form_submit_button("Salvar Interação")
        
        if submitted:
            if not descricao.strip():
                st.error("A descrição da interação é obrigatória!")
            else:
                id_cliente = clientes_dict[cliente_selecionado]
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO interacoes (cliente_id, tipo, descricao, data_interacao)
                    VALUES (?, ?, ?, ?)
                """, (id_cliente, tipo_contato, descricao, str(data_interacao)))
                conn.commit()
                conn.close()
                st.success("Interação registrada com sucesso!")
                st.rerun()

    st.divider()
    
    # Exibir Últimas Interações com segurança usando Pandas
    st.subheader("Últimas Interações Registradas")
    
    conn = conectar()
    df_interacoes = pd.read_sql("SELECT * FROM interacoes", conn)
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()
    
    if not df_interacoes.empty and not df_clientes.empty:
        col_id_cli = "cliente_id" if "cliente_id" in df_interacoes.columns else "id_cliente"
        
        if col_id_cli in df_interacoes.columns:
            df_merged = df_interacoes.merge(df_clientes, left_on=col_id_cli, right_on="id", suffixes=("_inter", "_cli"))
            
            # Ordena por data de forma decrescente se a coluna existir
            col_data = "data_interacao" if "data_interacao" in df_merged.columns else df_merged.columns[0]
            df_merged = df_merged.sort_values(by=col_data, ascending=False)
            
            for _, row in df_merged.iterrows():
                tipo = row.get("tipo", "Contato")
                data = row.get("data_interacao", "")
                nome_cli = row.get("nome", "Cliente")
                desc = row.get("descricao", "")
                
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{tipo}** — *{data}*")
                        st.caption(f"Cliente: {nome_cli}")
                        st.write(desc)
        else:
            st.dataframe(df_interacoes, use_container_width=True)
    else:
        st.info("Nenhuma interação registrada até o momento.")
