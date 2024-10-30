import streamlit as st

jzap = st.Page("whats/jzap.py", title="Envio de Mensagem", icon=":material/send:")

pg = st.navigation(
    {
        "Whatsapp": [jzap],
    }
)

pg.run()