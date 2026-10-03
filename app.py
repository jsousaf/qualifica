from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Projetos" / ".env")

from agente import rodar_agente

st.set_page_config(page_title="Qualificador de Leads", page_icon="🏢")
st.title("Qualificador de Leads B2B")
st.write("Informe um CNPJ para consultar e qualificar a empresa.")

with st.form("qualificar_empresa"):
    cnpj = st.text_input("CNPJ", placeholder="00.000.000/0000-00")
    enviar = st.form_submit_button("Qualificar empresa")

if enviar:
    if not cnpj.strip():
        st.warning("Informe um CNPJ para continuar.")
    else:
        try:
            with st.spinner("Consultando a empresa e preparando a análise..."):
                resposta = rodar_agente(
                    f"Qualifique a empresa com CNPJ {cnpj.strip()}. "
                    "Resuma os dados encontrados e informe a nota de fit de 0 a 10."
                )
            st.markdown(resposta)
        except Exception as erro:
            st.error(f"Não foi possível concluir a consulta: {erro}")