import re
import unicodedata

from spacy.lang.pt.stop_words import STOP_WORDS


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

def self_check_node(state):
    retrieved_docs = state.get("retrieved_docs", [])
    answer = state.get("answer", "").strip()
    retry_count = state.get("retry_count", 0)
    question = state.get("question", "")

    if not retrieved_docs:
        return {
            "self_check_passed": False,
            "refusal_reason": "Nenhum documento foi recuperado para sustentar a resposta.",
            "retry_count": retry_count,
        }

    if not answer:
        return {
            "self_check_passed": False,
            "refusal_reason": "A resposta gerada está vazia.",
            "retry_count": retry_count,
        }

    if "não encontrei evidências suficientes" in answer.lower():
        return {
            "self_check_passed": False,
            "refusal_reason": "Não há evidências suficientes no corpus atual.",
            "retry_count": retry_count,
        }

    question_terms = tokenize(question)
    evidence_text = " ".join(
        doc.get("content", "").lower()
        for doc in retrieved_docs
    )

    matched_terms = [term for term in question_terms if term in evidence_text]

    # exigir pelo menos 2 termos relevantes ou metade dos termos da pergunta
    minimum_required = max(2, len(question_terms) // 2)

    if len(matched_terms) < minimum_required:
        return {
            "self_check_passed": False,
            "refusal_reason": "Pergunta não suportada pelas evidências recuperadas.",
            "retry_count": retry_count,
        }

    return {
        "self_check_passed": True,
        "retry_count": retry_count,
    }