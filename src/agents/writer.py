def writer_node(state):
    retrieved_docs = state.get("retrieved_docs", [])

    if not retrieved_docs:
        return {
            "answer": "Não encontrei evidências suficientes no corpus atual.",
            "citations": [],
        }

    top_docs = retrieved_docs[:3]

    evidence_lines = []
    citations = []

    for idx, doc in enumerate(top_docs, start=1):
        metadata = doc.get("metadata", {})
        content = doc.get("content", "").strip()

        snippet = content[:300].strip()

        evidence_lines.append(
            f"[{idx}] {metadata.get('title', 'Sem título')} — "
            f"{metadata.get('published_at', 'Sem data')} — "
            f"{snippet}"
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

    answer = (
        "Com base nas notícias recuperadas, encontrei evidências relacionadas à pergunta. "
        "Os principais trechos recuperados estão listados abaixo."
    )

    answer += "\n\nEvidências:\n" + "\n".join(evidence_lines)

    return {
        "answer": answer,
        "citations": citations,
    }