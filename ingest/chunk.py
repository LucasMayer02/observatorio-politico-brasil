import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import PROCESSED_DATA_DIR


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

CHUNK_DIR_NAME = "chunks"


# =========================================================
# CARREGAR DOCUMENTOS PROCESSADOS
# =========================================================

def load_processed_documents(processed_dir: Path):

    docs = []

    for file_path in processed_dir.glob("*.json"):

        with open(file_path, "r", encoding="utf-8") as f:

            try:
                data = json.load(f)

                if isinstance(data, dict):
                    docs.append(data)

            except Exception as e:
                print(f"[ERRO] Falha ao ler {file_path.name}: {e}")

    return docs


# =========================================================
# GERAR CHUNKS
# =========================================================

def build_chunk_records(doc: dict, splitter):

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

                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "url": doc.get("url", ""),

                "published_at": doc.get("published_at", ""),
                "topic": doc.get("topic", ""),

                # metadados úteis para RAG
                "citability": doc.get("citability", {}),
            }
        )

    return records


# =========================================================
# SALVAR CHUNKS
# =========================================================

def save_chunks(chunk_records, chunk_dir: Path):

    saved = 0

    for chunk in chunk_records:

        file_path = chunk_dir / f"{chunk['chunk_id']}.json"

        # evita reprocessar
        if file_path.exists():
            continue

        with open(file_path, "w", encoding="utf-8") as f:

            json.dump(chunk, f, ensure_ascii=False, indent=2)

        saved += 1

    return saved


# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def chunk_all_documents():

    processed_dir = Path(PROCESSED_DATA_DIR)

    if not processed_dir.exists():
        print("Diretório de documentos processados não encontrado.")
        return

    chunk_dir = processed_dir.parent / CHUNK_DIR_NAME
    chunk_dir.mkdir(parents=True, exist_ok=True)

    docs = load_processed_documents(processed_dir)

    if not docs:
        print("Nenhum documento processado encontrado.")
        return

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ],
    )

    total_chunks = 0

    for doc in docs:

        chunk_records = build_chunk_records(doc, splitter)

        saved = save_chunks(chunk_records, chunk_dir)

        total_chunks += saved

        print(f"[OK] {doc['doc_id']} → {saved} chunks")

    print(f"\nTotal de chunks criados: {total_chunks}")
    print(f"Diretório de saída: {chunk_dir}")


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    chunk_all_documents()