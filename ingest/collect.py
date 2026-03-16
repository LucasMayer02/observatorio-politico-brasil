import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional

import feedparser
import httpx
import pandas as pd
import trafilatura
from tqdm import tqdm
from dateutil import parser as dateparser


# =========================================================
# CONFIGURAÇÃO
# =========================================================

RAW_DATA_DIR = "data/raw"

SITE_SOURCE = {
    "https://www.bbc.com/": "BBC",
    "https://www.nytimes.com/": "The New York Times",
}

RSS_FEEDS = {
    "https://www.bbc.com/": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.nytimes.com/": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
}


# =========================================================
# UTILITÁRIOS
# =========================================================

def build_doc_id(source: str, published_at: str, title: str):

    title_slug = (
        title.lower()
        .replace(" ", "-")
        .replace("/", "")
        .replace(":", "")
    )

    date_part = published_at[:10] if published_at else "no-date"

    return f"{source.lower().replace(' ', '-')}_{date_part}_{title_slug[:80]}"


def fetch_html(url: str):

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:

        response = client.get(url)
        response.raise_for_status()

        return response.text


def extract_main_text(html: str, url: str):

    content = trafilatura.extract(
        html,
        include_links=False,
        include_images=False,
        url=url,
    )

    return content or ""


# =========================================================
# EXTRAÇÃO RSS
# =========================================================

def fetch_rss_entries(feed_url: str):

    feed = feedparser.parse(feed_url)

    return feed.entries


def extract_published(entry):

    if hasattr(entry, "published_parsed") and entry.published_parsed:

        return datetime(*entry.published_parsed[:6]).isoformat()

    if hasattr(entry, "published"):

        try:
            return dateparser.parse(entry.published).isoformat()
        except:
            return ""

    return ""


# =========================================================
# CONSTRUÇÃO DO DOCUMENTO
# =========================================================

def build_document(entry, source_name, content_raw):

    title = getattr(entry, "title", "").strip()
    url = getattr(entry, "link", "").strip()

    published_at = extract_published(entry)

    collected_at = datetime.now(timezone.utc).isoformat()

    doc_id = build_doc_id(source_name, published_at, title)

    summary = getattr(entry, "summary", "")

    return {
        "doc_id": doc_id,
        "source": source_name,
        "source_type": "news_site",
        "topic": "politics",
        "title": title,
        "url": url,
        "published_at": published_at,
        "collected_at": collected_at,
        "author": "",
        "summary": summary,
        "content_raw": content_raw,
        "language": "en",
        "tags": [],
        "metadata": {
            "collector": "rss+html",
            "status": "success" if content_raw else "empty_content",
        },
    }


# =========================================================
# SALVAR DOCUMENTO
# =========================================================

def save_document(doc: dict):

    output_dir = Path(RAW_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{doc['doc_id']}.json"

    with open(path, "w", encoding="utf-8") as f:

        json.dump(doc, f, ensure_ascii=False, indent=2)


# =========================================================
# COLETA PRINCIPAL
# =========================================================

def collect_from_feed(site: str, limit: Optional[int] = None):

    rss_url = RSS_FEEDS[site]

    source_name = SITE_SOURCE[site]

    entries = fetch_rss_entries(rss_url)

    if limit:
        entries = entries[:limit]

    collected = 0

    for entry in tqdm(entries):

        try:

            url = getattr(entry, "link", "").strip()

            if not url:
                continue

            html = fetch_html(url)

            content_raw = extract_main_text(html, url)

            doc = build_document(entry, source_name, content_raw)

            save_document(doc)

            collected += 1

        except Exception as e:

            print(f"[ERRO] {e}")

    return collected


# =========================================================
# PIPELINE DE COLETA
# =========================================================

def collect():

    total = 0

    for site in RSS_FEEDS:

        print(f"\nColetando {SITE_SOURCE[site]}...")

        n = collect_from_feed(site)

        total += n

    print(f"\nTotal coletado: {total}")

    return total


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    collect()