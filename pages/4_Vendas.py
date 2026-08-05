import streamlit as st
import sqlite3
import pandas as pd
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas existem
inicializar_banco()

st.set_page_config(page_title="Registro de Vendas - CRM", page_icon="💰", layout="wide")

st.title("💰 Registro de Vendas")
st.write("Registre e acompanhe as vendas efetivadas do seu negócio.")

# Buscar clientes cadastrados para associar à venda
conn = conectar()
cursor = conn.cursor()
cursor.execute("SELECT id, nome, empresa FROM clientes")
clientes = cursor.fetchall()
conn.close()

if not clientes:
    st.warning("Nenhum cliente cadastrado ainda. Cadastre um cliente na página inicial antes de registrar vendas.")
else:
    # Mapear clientes para seleção amigável
    clientes_dict = {f"{c[1]} ({c[2]})" if c[2] else c[1]: c[0] for c in clientes}
    
    with st.form("form_venda"):
        st.subheader("Nova Venda Concluída")
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_selecionado = st.selectbox("Selecione o Cliente", options=list(clientes_dict.keys()))
            valor_venda = st.number_input("Valor da Venda (R$)", min_value=0.0, format="%.2f")
            
        with col2:
            data_venda = st.date_input("Data da Venda")
            produto_servico = st.text_input("Produto ou Serviço Vendido *")
            
        submitted = st.form_submit_button("Registrar Venda")
        
        if submitted:
            if not produto_servico.strip():
                st.error("O campo do produto ou serviço vendido é obrigatório!")
            else:
                id_cliente = clientes_dict[cliente_selecionado]
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO vendas (cliente_id, produto_servico, valor, data_venda)
                    VALUES (?, ?, ?, ?)
                """, (id_cliente, produto_servico, valor_venda, str(data_venda)))
                conn.commit()
                conn.close()
                st.success("Venda registrada com sucesso!")
                st.rerun()

    st.divider()
    
    # Exibir Histórico de Vendas com segurança usando Pandas
    st.subheader("Histórico de Vendas Realizadas")
    
    conn = conectar()
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()
    
    if not df_vendas.empty and not df_clientes.empty:
        col_id_cli = "cliente_id" if "cliente_id" in df_vendas.columns else "id_cliente"
        
        if col_id_cli in df_vendas.columns:
            df_merged = df_vendas.merge(df_clientes, left_on=col_id_cli, right_on="id", suffixes=("_venda", "_cli"))
            
            # Ordena por data de forma decrescente se a coluna existir
            col_data = "data_venda" if "data_venda" in df_merged.columns else df_merged.columns[0]
            df_merged = df_merged.sort_values(by=col_data, ascending=False)
            
            for _, row in df_merged.iterrows():
                data = row.get("data_venda", "")
                nome_cli = row.get("nome", "Cliente")
                produto = row.get("produto_servico", row.get("titulo", "Produto/Serviço"))
                valor = row.get("valor", 0.0)
                
                with st.container(border=True):
                    col_a, col_b, col_c = st.columns([3, 2, 2])
                    with col_a:
                        st.markdown(f"**{produto}**")
                        st.caption(f"Cliente: {nome_cli}")
                    with col_b:
                        st.markdown(f"Data: `{data}`")
                    with col_c:
                        st.markdown(f"**R$ {valor:,.2f}**")
        else:
            st.dataframe(df_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada até o momento.")
