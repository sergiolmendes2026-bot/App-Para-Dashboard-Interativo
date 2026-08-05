import streamlit as st
import sqlite3
from datetime import date
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas existem
inicializar_banco()

st.set_page_config(page_title="Interações - CRM", page_icon="💬", layout="wide")

st.title("💬 Histórico de Interações")
st.write("Registre ligações, reuniões, e-mails ou anotações importantes com os clientes.")

# Buscar clientes para associar à interação
conn = conectar()
cursor = conn.cursor()
cursor.execute("SELECT id, nome, empresa FROM clientes")
clientes = cursor.fetchall()
conn.close()

if not clientes:
    st.warning("Cadastre pelo menos um cliente na primeira página antes de registrar interações.")
else:
    clientes_dict = {f"{c[1]} ({c[2]})" if c[2] else c[1]: c[0] for c in clientes}
    
    with st.form("form_interacao"):
        st.subheader("Nova Interação")
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_selecionado = st.selectbox("Selecione o Cliente", options=list(clientes_dict.keys()))
            tipo = st.selectbox("Tipo de Contato", ["Ligação", "Reunião", "E-mail", "WhatsApp", "Outro"])
            
        with col2:
            data_interacao = st.date_input("Data da Interação", date.today())
            
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
                    INSERT INTO interacoes (id_cliente, tipo, descricao, data_interacao)
                    VALUES (?, ?, ?, ?)
                """, (id_cliente, tipo, descricao, str(data_interacao)))
                conn.commit()
                conn.close()
                st.success("Interação registrada com sucesso!")
                st.rerun()

    st.divider()
    
    # Exibir Histórico Recente
    st.subheader("Últimas Interações Registradas")
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.data_interacao, c.nome, i.tipo, i.descricao 
        FROM interacoes i
        JOIN clientes c ON i.id_cliente = c.id
        ORDER BY i.data_interacao DESC
    """)
    interacoes = cursor.fetchall()
    conn.close()
    
    if interacoes:
        for inter in interacoes:
            data_i, nome_cli, tipo, desc = inter
            with st.container(border=True):
                col_a, col_b = st.columns([1, 4])
                with col_a:
                    st.markdown(f"**{data_i}**")
                    st.caption(f"Tipo: `{tipo}`")
                with col_b:
                    st.markdown(f"**Cliente:** {nome_cli}")
                    st.write(desc)
    else:
        st.info("Nenhuma interação registrada até o momento.")
