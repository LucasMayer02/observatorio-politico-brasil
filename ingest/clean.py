import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import re
from pathlib import Path

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def remove_common_noise(text: str) -> str:
    noise_patterns = [
        r">>\s*Siga o canal da Agência Brasil no WhatsApp",
        r"\*Matéria em ampliada às .*",
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()


def clean_text(text: str) -> str:
    text = normalize_whitespace(text)
    text = remove_common_noise(text)
    text = normalize_whitespace(text)
    return text


def build_processed_document(raw_doc: dict) -> dict:
    content_clean = clean_text(raw_doc.get("content_raw", ""))

    return {
        "doc_id": raw_doc.get("doc_id", ""),
        "source": raw_doc.get("source", ""),
        "topic": raw_doc.get("topic", "politica"),
        "title": raw_doc.get("title", ""),
        "url": raw_doc.get("url", ""),
        "published_at": raw_doc.get("published_at", ""),
        "author": raw_doc.get("author", ""),
        "summary": "",
        "content_clean": content_clean,
        "language": raw_doc.get("language", "pt-BR"),
        "tags": raw_doc.get("tags", []),
        "citability": {
            "title": raw_doc.get("title", ""),
            "url": raw_doc.get("url", ""),
            "published_at": raw_doc.get("published_at", ""),
            "source": raw_doc.get("source", ""),
        },
    }


def process_file(raw_file: Path, output_dir: Path):
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    processed_doc = build_processed_document(raw_doc)

    output_path = output_dir / raw_file.name
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_doc, f, ensure_ascii=False, indent=2)

    print(f"[OK] Processado: {raw_file.name}")


def process_all_raw_documents():
    raw_dir = Path(RAW_DATA_DIR)
    output_dir = Path(PROCESSED_DATA_DIR)

    output_dir.mkdir(parents=True, exist_ok=True)

    raw_files = list(raw_dir.glob("*.json"))

    if not raw_files:
        print("Nenhum arquivo raw encontrado.")
        return

    processed_count = 0

    for raw_file in raw_files:
        try:
            process_file(raw_file, output_dir)
            processed_count += 1
        except Exception as e:
            print(f"[ERRO] Falha ao processar {raw_file.name}: {e}")

    print(f"\nTotal processado: {processed_count}")


if __name__ == "__main__":
    process_all_raw_documents()