import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import PROCESSED_DATA_DIR


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_processed_documents(processed_dir: Path):
    docs = []

    for file_path in processed_dir.glob("*.json"):
        # ignorar o arquivo agregado de chunks
        if file_path.name == "chunks.json":
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # garantir que só documentos individuais entrem
            if isinstance(data, dict):
                docs.append(data)
            else:
                print(f"[AVISO] Ignorando arquivo não compatível: {file_path.name}")

    return docs


def build_chunk_records(doc: dict, splitter: RecursiveCharacterTextSplitter):
    content = doc.get("content_clean", "").strip()

    if not content:
        return []

    chunks = splitter.split_text(content)
    records = []

    for idx, chunk_text in enumerate(chunks):
        records.append(
            {
                "chunk_id": f"{doc['doc_id']}_chunk_{idx}",
                "doc_id": doc["doc_id"],
                "chunk_index": idx,
                "text": chunk_text,
                "source": doc.get("source", ""),
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "published_at": doc.get("published_at", ""),
                "topic": doc.get("topic", "politica"),
            }
        )

    return records


def chunk_all_documents():
    processed_dir = Path(PROCESSED_DATA_DIR)

    if not processed_dir.exists():
        print("Diretório de processados não encontrado.")
        return

    docs = load_processed_documents(processed_dir)

    if not docs:
        print("Nenhum documento processado encontrado.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks = []

    for doc in docs:
        chunk_records = build_chunk_records(doc, splitter)
        all_chunks.extend(chunk_records)

        print(f"[OK] {doc['doc_id']} -> {len(chunk_records)} chunks")

    output_path = processed_dir / "chunks.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nTotal de chunks: {len(all_chunks)}")
    print(f"Arquivo salvo em: {output_path}")


if __name__ == "__main__":
    chunk_all_documents()