import json
from pathlib import Path
from tqdm import tqdm

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import PROCESSED_DATA_DIR


# =========================================================
# CONFIGURAÇÃO
# =========================================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

labels = [
    "conflict",
    "diplomacy",
    "economy",
    "sanctions",
    "politics",
    "environment"
]


# =========================================================
# MODELO
# =========================================================

model = SentenceTransformer(MODEL_NAME)

label_embeddings = model.encode(
    labels,
    normalize_embeddings=True
)


# =========================================================
# CLASSIFICAÇÃO
# =========================================================

def classify(text):

    embedding = model.encode(
        [text],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        embedding,
        label_embeddings
    )[0]

    best_idx = np.argmax(similarities)

    return labels[best_idx]


# =========================================================
# PIPELINE
# =========================================================

def categorize_documents():

    processed_dir = Path(PROCESSED_DATA_DIR)

    files = list(processed_dir.glob("*.json"))

    if not files:
        print("Nenhum documento encontrado.")
        return

    for file in tqdm(files):

        try:

            with open(file, "r", encoding="utf-8") as f:
                article = json.load(f)

            # pular se já categorizado
            if article.get("category"):
                continue

            text = f"{article.get('title','')} {article.get('summary','')}"

            category = classify(text)

            article["category"] = category

            with open(file, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)

        except Exception as e:

            print(f"Erro em {file.name}: {e}")

    print("Classificação concluída.")


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    categorize_documents()