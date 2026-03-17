import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config import PROCESSED_DATA_DIR


CHUNK_DIR_NAME = "chunks"
VECTORSTORE_DIR_NAME = "vectorstore"

EMBEDDING_MODEL = "BAAI/bge-small-en"


# =========================================================
# CARREGAR CHUNKS
# =========================================================

def load_chunks(chunk_dir: Path):

    docs = []

    for file_path in chunk_dir.glob("*.json"):

        try:

            with open(file_path, "r", encoding="utf-8") as f:
                chunk = json.load(f)

            text = chunk.get("text", "").strip()

            if not text:
                continue

            metadata = {
                "chunk_id": chunk.get("chunk_id"),
                "doc_id": chunk.get("doc_id"),
                "title": chunk.get("title"),
                "source": chunk.get("source"),
                "url": chunk.get("url"),
                "published_at": chunk.get("published_at"),
                "topic": chunk.get("topic"),
            }

            docs.append(Document(page_content=text, metadata=metadata))

        except Exception as e:

            print(f"[ERRO] Falha ao carregar {file_path.name}: {e}")

    return docs


# =========================================================
# GERAR EMBEDDINGS
# =========================================================

def build_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    return embeddings


# =========================================================
# CRIAR VECTOR STORE
# =========================================================

def build_vectorstore(documents, vectorstore_dir: Path):

    embeddings = build_embeddings()

    vectorstore = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=str(vectorstore_dir)
    )

    vectorstore.persist()

    return vectorstore


# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def embed_all_chunks():

    base_dir = Path(PROCESSED_DATA_DIR).parent

    chunk_dir = base_dir / CHUNK_DIR_NAME
    vectorstore_dir = base_dir / VECTORSTORE_DIR_NAME

    if not chunk_dir.exists():

        print("Diretório de chunks não encontrado.")
        return

    print("Carregando chunks...")

    documents = load_chunks(chunk_dir)

    if not documents:

        print("Nenhum chunk encontrado.")
        return

    print(f"{len(documents)} chunks carregados.")

    print("Gerando embeddings...")

    build_vectorstore(documents, vectorstore_dir)

    print("\nVector store criado com sucesso.")
    print(f"Localização: {vectorstore_dir}")


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    embed_all_chunks()