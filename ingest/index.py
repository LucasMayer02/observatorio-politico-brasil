import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import PROCESSED_DATA_DIR


VECTORSTORE_DIR_NAME = "vectorstore"
EMBEDDING_MODEL = "BAAI/bge-small-en"


# =========================================================
# CARREGAR EMBEDDINGS
# =========================================================

def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# =========================================================
# CARREGAR VECTOR STORE
# =========================================================

def load_vectorstore():

    base_dir = Path(PROCESSED_DATA_DIR).parent
    vectorstore_dir = base_dir / VECTORSTORE_DIR_NAME

    if not vectorstore_dir.exists():

        raise FileNotFoundError(
            f"Vector store não encontrado em {vectorstore_dir}"
        )

    embeddings = load_embeddings()

    vectorstore = Chroma(
        persist_directory=str(vectorstore_dir),
        embedding_function=embeddings
    )

    return vectorstore


# =========================================================
# CRIAR RETRIEVER
# =========================================================

def get_retriever(k: int = 5):

    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    return retriever


# =========================================================
# BUSCA SIMPLES (DEBUG)
# =========================================================

def search(query: str, k: int = 5):

    retriever = get_retriever(k)

    docs = retriever.invoke(query)

    results = []

    for doc in docs:

        results.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })

    return results


# =========================================================
# TESTE DO ÍNDICE
# =========================================================

if __name__ == "__main__":

    query = "Ukraine Russia war"

    print(f"\nBuscando: {query}\n")

    results = search(query)

    for i, r in enumerate(results):

        print("=" * 60)
        print(f"Resultado {i+1}")
        print(r["metadata"])
        print()
        print(r["text"][:400])