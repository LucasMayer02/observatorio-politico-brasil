from langchain_ollama import ChatOllama

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

K = 3
PADDING_SIZE = 500

def writer_node(state):
    retrieved_docs = state.get("retrieved_docs", [])

    if not retrieved_docs:
        return {
            "answer": "Não encontrei evidências suficientes no corpus atual.",
            "citations": [],
        }

    top_docs = retrieved_docs[:K]
    citations = []

    evidence_blocks = []

    for idx, doc in enumerate(top_docs, start=1):
        metadata = doc.get("metadata", {})
        content = doc.get("content", "").strip()

        snippet = content[:PADDING_SIZE].strip()

        evidence_blocks.append(
            f"[{idx}] Título: {metadata.get('title', '')}\n"
            f"Fonte: {metadata.get('source', '')}\n"
            f"Data: {metadata.get('published_at', '')}\n"
            f"URL: {metadata.get('url', '')}\n"
            f"Trecho: {snippet}\n"
        )

        citations.append(
            {
                "id": idx,
                "title": metadata.get("title", ""),
                "url": metadata.get("url", ""),
                "published_at": metadata.get("published_at", ""),
                "source": metadata.get("source", ""),
                "snippet": snippet,
            }
        )

    question = state.get("question", "")

    prompt = f"""
Você é um assistente que responde perguntas sobre notícias políticas com base apenas nas evidências fornecidas.

Pergunta:
{question}

Evidências:
{chr(10).join(evidence_blocks)}

Instruções:
- Responder em português.
- Usar somente as evidências fornecidas.
- Fazer uma síntese curta e clara em 2 a 4 frases.
- Não inventar fatos.
- Responder apenas ao que foi perguntado.
- Se a pergunta for sobre estado de saúde, priorizar somente informações clínicas:
  diagnóstico, internação, sintomas, tratamento, quadro clínico e evolução.
- Não misturar contexto jurídico, prisional ou político com contexto clínico,
  a menos que isso seja essencial para responder à pergunta.
- Se as evidências forem insuficientes, responder exatamente:
  "Não encontrei evidências suficientes no corpus atual."
"""

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    response = llm.invoke(prompt)

    answer = response.content.strip()

    return {
        "answer": answer,
        "citations": citations,
    }