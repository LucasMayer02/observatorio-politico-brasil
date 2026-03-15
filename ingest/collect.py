import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import feedparser
import httpx
import trafilatura

from src.config import RAW_DATA_DIR


AGENCIA_BRASIL_RSS = "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text


def build_doc_id(source: str, published_at: str, title: str) -> str:
    date_part = published_at[:10] if published_at else "sem-data"
    source_slug = slugify(source)
    title_slug = slugify(title)[:80]
    return f"{source_slug}_{date_part}_{title_slug}"


def fetch_rss_entries(feed_url: str):
    feed = feedparser.parse(feed_url)
    return feed.entries


def extract_published_at(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6]).isoformat()
    if hasattr(entry, "published"):
        return entry.published
    return ""


def fetch_html(url: str) -> str:
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def extract_main_text(html: str, url: str = "") -> str:
    downloaded = trafilatura.extract(
        html,
        include_links=False,
        include_images=False,
        url=url,
    )
    return downloaded or ""


def build_raw_document(entry, html: str, content_raw: str) -> dict:
    title = getattr(entry, "title", "").strip()
    url = getattr(entry, "link", "").strip()
    published_at = extract_published_at(entry)
    collected_at = datetime.now().isoformat()

    doc_id = build_doc_id("Agencia Brasil", published_at, title)

    summary = ""
    if hasattr(entry, "summary"):
        summary = entry.summary

    return {
        "doc_id": doc_id,
        "source": "Agencia Brasil",
        "source_type": "news_site",
        "topic": "politica",
        "title": title,
        "url": url,
        "published_at": published_at,
        "collected_at": collected_at,
        "author": "",
        "summary": summary,
        "content_raw": content_raw,
        "language": "pt-BR",
        "tags": [],
        "metadata": {
            "collector": "rss+html",
            "base_url": "https://agenciabrasil.ebc.com.br",
            "status": "success" if content_raw else "empty_content",
        },
    }


def save_raw_document(doc: dict):
    output_dir = Path(RAW_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{doc['doc_id']}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)


def collect_agencia_brasil(limit: int = 5):
    entries = fetch_rss_entries(AGENCIA_BRASIL_RSS)

    collected = 0

    for entry in entries[:limit]:
        try:
            url = getattr(entry, "link", "").strip()
            if not url:
                continue

            html = fetch_html(url)
            content_raw = extract_main_text(html, url=url)

            doc = build_raw_document(entry, html, content_raw)
            save_raw_document(doc)

            collected += 1
            print(f"[OK] Coletado: {doc['title']}")

        except Exception as e:
            print(f"[ERRO] Falha ao coletar entrada: {e}")

    print(f"\nTotal coletado: {collected}")


if __name__ == "__main__":
    collect_agencia_brasil(limit=5)