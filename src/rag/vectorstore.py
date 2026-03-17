from langchain_chroma import Chroma

from src.config import CHROMA_DIR
from src.rag.embedder import get_embedding_model


COLLECTION_NAME = "political_news"


def get_vectorstore():
    embeddings = get_embedding_model()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

    return vectorstore