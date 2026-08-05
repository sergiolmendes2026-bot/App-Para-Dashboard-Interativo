import streamlit as st
import sqlite3
import pandas as pd
from database import conectar, inicializar_banco

# Garante que o banco e as tabelas existem
inicializar_banco()

st.set_page_config(page_title="Pipeline de Vendas - CRM", page_icon="📈", layout="wide")

st.title("📈 Pipeline / Funil de Vendas")
st.write("Acompanhe o status das suas oportunidades comerciais.")

# Buscar clientes cadastrados para associar ao pipeline
conn = conectar()
cursor = conn.cursor()
cursor.execute("SELECT id, nome, empresa FROM clientes")
clientes = cursor.fetchall()
conn.close()

if not clientes:
    st.warning("Nenhum cliente cadastrado ainda. Cadastre um cliente na página anterior antes de criar oportunidades no pipeline.")
else:
    # Mapear clientes para seleção amigável
    clientes_dict = {f"{c[1]} ({c[2]})" if c[2] else c[1]: c[0] for c in clientes}
    
    with st.form("form_pipeline"):
        st.subheader("Adicionar Nova Oportunidade")
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_selecionado = st.selectbox("Selecione o Cliente", options=list(clientes_dict.keys()))
            titulo_oportunidade = st.text_input("Título / Descrição da Oportunidade *")
            
        with col2:
            estagio = st.selectbox("Estágio do Funil", ["Prospecção", "Contato Feito", "Proposta Enviada", "Fechado Ganho", "Fechado Perdido"])
            valor = st.number_input("Valor Estimado (R$)", min_value=0.0, format="%.2f")
            
        submitted = st.form_submit_button("Adicionar ao Pipeline")
        
        if submitted:
            if not titulo_oportunidade.strip():
                st.error("O título da oportunidade é obrigatório!")
            else:
                id_cliente = clientes_dict[cliente_selecionado]
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pipeline (cliente_id, titulo, estagio, valor)
                    VALUES (?, ?, ?, ?)
                """, (id_cliente, titulo_oportunidade, estagio, valor))
                conn.commit()
                conn.close()
                st.success("Oportunidade adicionada com sucesso ao Pipeline!")
                st.rerun()

    st.divider()
    
    # Exibir Oportunidades Existentes usando Pandas para evitar erros de colunas específicas do SQL
    st.subheader("Oportunidades Ativas")
    
    conn = conectar()
    df_pipeline = pd.read_sql("SELECT * FROM pipeline", conn)
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()
    
    if not df_pipeline.empty and not df_clientes.empty:
        # Tenta identificar qual coluna de ID de cliente existe na tabela pipeline
        col_id_cli = "cliente_id" if "cliente_id" in df_pipeline.columns else "id_cliente"
        
        if col_id_cli in df_pipeline.columns:
            df_merged = df_pipeline.merge(df_clientes, left_on=col_id_cli, right_on="id", suffixes=("_pipe", "_cli"))
            
            for _, row in df_merged.iterrows():
                titulo = row.get("titulo", row.get("descricao", "Oportunidade"))
                nome_cli = row.get("nome", "Cliente")
                estagio = row.get("estagio", "Prospecção")
                valor = row.get("valor", 0.0)
                
                with st.container(border=True):
                    col_a, col_b, col_c = st.columns([3, 2, 2])
                    with col_a:
                        st.markdown(f"**{titulo}**")
                        st.caption(f"Cliente: {nome_cli}")
                    with col_b:
                        st.markdown(f"Estágio: `{estagio}`")
                    with col_c:
                        st.markdown(f"**R$ {valor:,.2f}**")
        else:
            st.dataframe(df_pipeline, use_container_width=True)
    else:
        st.info("Nenhuma oportunidade registrada no pipeline até o momento.")
