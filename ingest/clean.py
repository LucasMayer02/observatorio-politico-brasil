import os
import sys
import json
import re
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR


# =========================================================
# NORMALIZAÇÃO DE TEXTO
# =========================================================

def normalize_whitespace(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# =========================================================
# REMOÇÃO DE RUÍDO
# =========================================================

def remove_common_noise(text: str) -> str:

    if not text:
        return ""

    noise_patterns = [
        r">>\s*Siga o canal.*",
        r"\*Matéria ampliada às .*",
        r"Leia também:.*",
        r"Compartilhe esta notícia.*",
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()


# =========================================================
# PIPELINE DE LIMPEZA
# =========================================================

def clean_text(text: str) -> str:

    if not text:
        return ""

    text = normalize_whitespace(text)
    text = remove_common_noise(text)
    text = normalize_whitespace(text)

    return text


# =========================================================
# CONSTRUÇÃO DO DOCUMENTO PROCESSADO
# =========================================================

def build_processed_document(raw_doc: dict) -> dict:

    content_raw = raw_doc.get("content_raw", "")
    content_clean = clean_text(content_raw)

    summary = raw_doc.get("summary", "")
    summary = clean_text(summary)

    return {

        "doc_id": raw_doc.get("doc_id", ""),

        "source": raw_doc.get("source", ""),
        "source_type": raw_doc.get("source_type", "news_site"),

        "topic": raw_doc.get("topic", "politics"),

        "title": raw_doc.get("title", ""),

        "url": raw_doc.get("url", ""),

        "published_at": raw_doc.get("published_at", ""),
        "collected_at": raw_doc.get("collected_at", ""),

        "author": raw_doc.get("author", ""),

        "summary": summary,

        "content_clean": content_clean,

        "language": raw_doc.get("language", "en"),

        "tags": raw_doc.get("tags", []),

        "citability": {
            "title": raw_doc.get("title", ""),
            "url": raw_doc.get("url", ""),
            "published_at": raw_doc.get("published_at", ""),
            "source": raw_doc.get("source", ""),
        },

        "metadata": raw_doc.get("metadata", {})
    }


# =========================================================
# PROCESSAMENTO DE ARQUIVO
# =========================================================

def process_file(raw_file: Path, output_dir: Path):

    with open(raw_file, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    processed_doc = build_processed_document(raw_doc)

    output_path = output_dir / raw_file.name

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_doc, f, ensure_ascii=False, indent=2)

    print(f"[OK] Processado: {raw_file.name}")


# =========================================================
# PROCESSAMENTO EM LOTE
# =========================================================

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

        output_path = output_dir / raw_file.name

        # evita reprocessar arquivos
        if output_path.exists():
            continue

        try:

            process_file(raw_file, output_dir)
            processed_count += 1

        except Exception as e:

            print(f"[ERRO] Falha ao processar {raw_file.name}: {e}")

    print(f"\nTotal processado: {processed_count}")


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    process_all_raw_documents()