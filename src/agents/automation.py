from langchain_ollama import ChatOllama

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.rag.retriever import get_retriever


def automation_node(state):
    question = state.get("question", "").strip()

    if not question:
        return {
            "automation_result": {
                "status": "error",
                "message": "Pergunta vazia para automação."
            }
        }

    retriever = get_retriever(k=5)
    docs = retriever.invoke(question)

    if not docs:
        return {
            "automation_result": {
                "status": "no_evidence",
                "message": "Não encontrei evidências suficientes no corpus atual.",
                "briefing": "",
                "sources": []
            }
        }

    evidence_blocks = []
    sources = []

    for idx, doc in enumerate(docs, start=1):
        metadata = doc.metadata
        snippet = doc.page_content[:500].strip()

        evidence_blocks.append(
            f"[{idx}] Título: {metadata.get('title', '')}\n"
            f"Fonte: {metadata.get('source', '')}\n"
            f"Data: {metadata.get('published_at', '')}\n"
            f"URL: {metadata.get('url', '')}\n"
            f"Trecho: {snippet}\n"
        )

        sources.append(
            {
                "id": idx,
                "title": metadata.get("title", ""),
                "url": metadata.get("url", ""),
                "published_at": metadata.get("published_at", ""),
                "source": metadata.get("source", ""),
                "snippet": snippet,
            }
        )

    prompt = f"""
Você é um assistente que gera briefings curtos sobre notícias políticas com base apenas nas evidências fornecidas.

Pedido:
{question}

Evidências:
{chr(10).join(evidence_blocks)}

Instruções:
- Responder em português.
- Usar somente as evidências fornecidas.
- Produzir um briefing curto e claro.
- Organizar a resposta em:
  1. Resumo executivo
  2. Principais eventos
  3. Fontes utilizadas
- Não inventar fatos.
- Se as evidências forem insuficientes, responder exatamente:
  "Não encontrei evidências suficientes no corpus atual."
"""

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    response = llm.invoke(prompt)
    briefing = response.content.strip()

    return {
        "automation_result": {
            "status": "ok" if briefing else "error",
            "message": "",
            "briefing": briefing,
            "sources": sources,
        }
    }