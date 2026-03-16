import os
import sys

# permitir importar src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from pathlib import Path

from langchain_core.documents import Document

from src.config import PROCESSED_DATA_DIR
from src.rag.vectorstore import get_vectorstore


def load_chunks():
    chunks_path = Path(PROCESSED_DATA_DIR) / "chunks.json"

    if not chunks_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {chunks_path}")

    with open(chunks_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_documents(chunk_records):
    documents = []

    for chunk in chunk_records:
        doc = Document(
            page_content=chunk["text"],
            metadata={
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "chunk_index": chunk["chunk_index"],
                "source": chunk["source"],
                "title": chunk["title"],
                "url": chunk["url"],
                "published_at": chunk["published_at"],
                "topic": chunk["topic"],
            },
        )

        documents.append(doc)

    return documents


def index_chunks():
    chunk_records = load_chunks()
    documents = build_documents(chunk_records)

    vectorstore = get_vectorstore()

    vectorstore.add_documents(documents)

    print(f"Total indexado: {len(documents)}")


if __name__ == "__main__":
    index_chunks()