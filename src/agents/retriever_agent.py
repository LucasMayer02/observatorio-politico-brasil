import re
import unicodedata

from spacy.lang.pt.stop_words import STOP_WORDS

from src.rag.retriever import get_retriever


# Stopwords em set para busca O(1)
STOPWORDS = set(STOP_WORDS)


def normalize(text: str):
    """Remove acentos e normaliza texto"""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def tokenize(text: str):
    text = normalize(text)

    terms = re.findall(r"\b[a-z0-9-]+\b", text)

    return [
        term for term in terms
        if term not in STOPWORDS and len(term) > 2
    ]


def score_doc(question_terms, content: str, title: str):
    text = normalize(f"{title} {content}")

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