import streamlit as st
import sqlite3
from datetime import date
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas existem
inicializar_banco()

st.set_page_config(page_title="Vendas - CRM", page_icon="💰", layout="wide")

st.title("💰 Registro de Vendas")
st.write("Registre e acompanhe as vendas efetivadas do seu negócio.")

# Buscar clientes para associar à venda
conn = conectar()
cursor = conn.cursor()
cursor.execute("SELECT id, nome, empresa FROM clientes")
clientes = cursor.fetchall()
conn.close()

if not clientes:
    st.warning("Cadastre pelo menos um cliente na primeira página antes de registrar vendas.")
else:
    clientes_dict = {f"{c[1]} ({c[2]})" if c[2] else c[1]: c[0] for c in clientes}
    
    with st.form("form_venda"):
        st.subheader("Nova Venda Concluída")
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_selecionado = st.selectbox("Selecione o Cliente", options=list(clientes_dict.keys()))
            valor_venda = st.number_input("Valor da Venda (R$)", min_value=0.0, format="%.2f")
            
        with col2:
            data_venda = st.date_input("Data da Venda", date.today())
            produto_servico = st.text_input("Produto ou Serviço Vendido *")
            
        submitted = st.form_submit_button("Registrar Venda")
        
        if submitted:
            if not produto_servico.strip():
                st.error("O campo produto/serviço é obrigatório!")
            elif valor_venda <= 0:
                st.error("O valor da venda deve ser maior que zero!")
            else:
                id_cliente = clientes_dict[cliente_selecionado]
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO vendas (id_cliente, valor, data_venda, produto_servico)
                    VALUES (?, ?, ?, ?)
                """, (id_cliente, valor_venda, str(data_venda), produto_servico))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()

    st.divider()
    
    # Exibir Vendas Registradas
    st.subheader("Histórico de Vendas Realizadas")
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.data_venda, c.nome, v.produto_servico, v.valor 
        FROM vendas v
        JOIN clientes c ON v.id_cliente = c.id
        ORDER BY v.data_venda DESC
    """)
    vendas = cursor.fetchall()
    conn.close()
    
    if vendas:
        for venda in vendas:
            data_v, nome_cli, produto, valor = venda
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([2, 3, 2])
                with col_a:
                    st.markdown(f"**{data_v}**")
                    st.caption(f"Cliente: {nome_cli}")
                with col_b:
                    st.markdown(f"**Produto/Serviço:** {produto}")
                with col_c:
                    st.markdown(f"**R$ {valor:,.2f}**")
    else:
        st.info("Nenhuma venda registrada até o momento.")
