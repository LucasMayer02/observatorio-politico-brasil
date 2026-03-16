from langchain_ollama import OllamaEmbeddings

from src.config import OLLAMA_BASE_URL, EMBEDDING_MODEL


def get_embedding_model():
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )