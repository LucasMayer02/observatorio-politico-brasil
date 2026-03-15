import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.graph.build_graph import build_graph

st.set_page_config(
    page_title="Observatório Político Brasil",
    layout="wide"
)

st.title("Observatório Político Brasil")
st.write("Sistema agêntico para consulta e briefing de notícias políticas do Brasil.")

# construir grafo
graph = build_graph()

aba1, aba2 = st.tabs(["Perguntas", "Briefing"])

# -----------------------
# Aba de perguntas
# -----------------------

with aba1:
    st.subheader("Perguntas sobre notícias políticas")

    pergunta = st.text_input(
        "Digite sua pergunta",
        placeholder="Ex: O que saiu hoje sobre o Senado?"
    )

    if st.button("Responder"):

        if pergunta:
            result = graph.invoke({"question": pergunta})

            st.write("### Resultado do sistema")
            st.json(result)

        else:
            st.warning("Digite uma pergunta.")

# -----------------------
# Aba de automação
# -----------------------

with aba2:
    st.subheader("Gerar briefing político")

    tema = st.text_input(
        "Tema do briefing",
        placeholder="Ex: Congresso"
    )

    periodo = st.selectbox(
        "Período",
        ["3 dias", "7 dias", "30 dias"]
    )

    if st.button("Gerar briefing"):

        pergunta = f"Gerar briefing sobre {tema} nos últimos {periodo}"

        result = graph.invoke({"question": pergunta})

        st.write("### Resultado do sistema")
        st.json(result)