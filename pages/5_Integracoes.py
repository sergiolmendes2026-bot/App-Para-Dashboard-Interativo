import streamlit as st

st.set_page_config(page_title="Integrações - CRM", page_icon="🔌", layout="wide")

st.title("🔌 Integrações")
st.write("Conecte o CRM às ferramentas essenciais para empresas de serviços:")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🟢 WhatsApp")
        st.write("Integre mensagens e facilite o contato direto com os clientes cadastrados.")
        
        # Salva o estado no session_state para uso global
        status_wa = st.toggle("Ativar Integração com WhatsApp", value=st.session_state.get("whatsapp_ativo", False))
        st.session_state["whatsapp_ativo"] = status_wa
        
        if status_wa:
            st.success("WhatsApp conectado com sucesso!")
            numero_wa = st.text_input("Número / Instância da API do WhatsApp", value=st.session_state.get("whatsapp_numero", ""))
            st.session_state["whatsapp_numero"] = numero_wa

with col2:
    with st.container(border=True):
        st.subheader("📧 Gmail")
        st.write("Sincronize e-mails enviados e recebidos diretamente no histórico do cliente.")
        
        status_gm = st.toggle("Ativar Integração com Gmail", value=st.session_state.get("gmail_ativo", False))
        st.session_state["gmail_ativo"] = status_gm
        
        if status_gm:
            st.success("Gmail conectado com sucesso!")
            email_gm = st.text_input("E-mail para Sincronização", value=st.session_state.get("gmail_email", ""))
            st.session_state["gmail_email"] = email_gm

st.divider()
st.info("💡 Com a integração ativa, os atalhos de disparo e envio direto aparecerão nos cadastros de clientes e interações.")
