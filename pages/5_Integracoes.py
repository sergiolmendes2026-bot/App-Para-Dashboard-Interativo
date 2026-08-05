import streamlit as st

st.set_page_config(page_title="Integrações - CRM", page_icon="🔌", layout="wide")

st.title("🔌 Integrações")
st.write("Conecte o CRM às ferramentas essenciais para empresas de serviços:")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🟢 WhatsApp")
        st.write("Integre mensagens e facilite o contato direto com os clientes cadastrados.")
        status_wa = st.toggle("Ativar Integração com WhatsApp", value=False)
        if status_wa:
            st.success("WhatsApp conectado com sucesso!")
            st.text_input("Número / Instância da API do WhatsApp")

with col2:
    with st.container(border=True):
        st.subheader("📧 Gmail")
        st.write("Sincronize e-mails enviados e recebidos diretamente no histórico do cliente.")
        status_gm = st.toggle("Ativar Integração com Gmail", value=False)
        if status_gm:
            st.success("Gmail conectado com sucesso!")
            st.text_input("E-mail para Sincronização")

st.divider()
st.info("💡 As integrações permitem automatizar o registro de interações e o fluxo comercial do seu CRM.")
