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

graph = build_graph()

aba1, aba2 = st.tabs(["Perguntas", "Briefing"])


def render_result(result: dict):
    answer = result.get("answer", "")
    citations = result.get("citations", [])
    self_check_passed = result.get("self_check_passed", False)
    refusal_reason = result.get("refusal_reason")

    st.subheader("Resposta")
    if answer:
        st.write(answer)
    else:
        st.info("Nenhuma resposta gerada.")

    st.subheader("Validação")
    if self_check_passed:
        st.success("Self-check aprovado")
    else:
        st.error("Self-check reprovado")

    if refusal_reason:
        st.warning(f"Motivo: {refusal_reason}")

    st.subheader("Citações")
    if citations:
        for citation in citations:
            st.markdown(
                f"**[{citation['id']}] {citation['title']}**  \n"
                f"Fonte: {citation['source']}  \n"
                f"Data: {citation['published_at']}  \n"
                f"URL: {citation['url']}  \n"
                f"Trecho: {citation['snippet']}"
            )
            st.markdown("---")
    else:
        st.info("Nenhuma citação disponível.")

    with st.expander("Ver estado bruto do grafo"):
        st.json(result)


with aba1:
    st.subheader("Perguntas sobre notícias políticas")

    pergunta = st.text_input(
        "Digite sua pergunta",
        placeholder="Ex: O que saiu hoje sobre o Senado?"
    )

    if st.button("Responder"):
        if pergunta:
            result = graph.invoke({"question": pergunta})
            render_result(result)
        else:
            st.warning("Digite uma pergunta.")


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
        render_result(result)