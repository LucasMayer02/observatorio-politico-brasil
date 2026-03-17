import re

from src.rag.retriever import get_retriever


STOPWORDS = {
    "a", "o", "os", "as", "de", "da", "do", "das", "dos",
    "e", "é", "em", "no", "na", "nos", "nas", "um", "uma",
    "que", "quem", "qual", "quais", "foi", "são", "ser",
    "por", "para", "com", "sem", "ao", "aos", "à", "às",
    "como", "sobre", "estado", "saúde"
}


def tokenize(text: str):
    terms = re.findall(r"\b[a-zA-ZÀ-ÿ0-9-]+\b", text.lower())
    return [term for term in terms if term not in STOPWORDS and len(term) > 2]


def score_doc(question_terms, content: str, title: str):
    text = f"{title} {content}".lower()
    return sum(1 for term in question_terms if term in text)


def retriever_node(state):
    question = state.get("question", "").strip()

    if not question:
        return {"retrieved_docs": []}

    retriever = get_retriever(k=6)
    docs = retriever.invoke(question)

    question_terms = tokenize(question)

    ranked = []
    for doc in docs:
        score = score_doc(
            question_terms,
            doc.page_content,
            doc.metadata.get("title", "")
        )
        ranked.append((score, doc))

    ranked.sort(key=lambda x: x[0], reverse=True)

    retrieved_docs = []
    for score, doc in ranked[:4]:
        retrieved_docs.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
        )

    return {"retrieved_docs": retrieved_docs}