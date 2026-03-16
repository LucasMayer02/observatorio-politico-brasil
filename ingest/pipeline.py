import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tqdm import tqdm

from ingest.collect import collect
from ingest.clean import process_all_raw_documents
from ingest.countries import add_countries_metadata
from ingest.categorize import categorize_documents
from ingest.chunk import chunk_all_documents
from ingest.embed import embed_all_chunks

from src.config import PROCESSED_DATA_DIR


pipeline_status = {
    "state": "idle",
    "processed_docs": 0,
    "processed_chunks": 0,
    "last_update": None
}


# =========================================================
# UTILIDADES
# =========================================================

def load_processed_files():

    processed_dir = Path(PROCESSED_DATA_DIR)

    if not processed_dir.exists():
        return []

    return list(processed_dir.glob("*.json"))


def count_docs_missing(field):

    count = 0

    for file in load_processed_files():

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data.get(field):
            count += 1

    return count


# =========================================================
# PIPELINE
# =========================================================

def run_pipeline():

    print("\n==============================")
    print("Pipeline incremental iniciado")
    print("==============================\n")

    try:

        # -------------------------------------------------
        # 1️⃣ COLETA
        # -------------------------------------------------

        pipeline_status["state"] = "collecting"

        tqdm.write("Running collect")

        collect()


        # -------------------------------------------------
        # 2️⃣ LIMPEZA (apenas se necessário)
        # -------------------------------------------------

        missing_clean = count_docs_missing("content_clean")

        if missing_clean > 0:

            pipeline_status["state"] = "cleaning"

            tqdm.write(f"Cleaning {missing_clean} documents")

            process_all_raw_documents()


        # -------------------------------------------------
        # 3️⃣ DETECTAR PAÍSES
        # -------------------------------------------------

        missing_countries = count_docs_missing("countries")

        if missing_countries > 0:

            pipeline_status["state"] = "detecting_countries"

            tqdm.write(f"Detecting countries for {missing_countries} docs")

            add_countries_metadata()


        # -------------------------------------------------
        # 4️⃣ CLASSIFICAR CATEGORIA
        # -------------------------------------------------

        missing_category = count_docs_missing("category")

        if missing_category > 0:

            pipeline_status["state"] = "categorizing"

            tqdm.write(f"Categorizing {missing_category} docs")

            categorize_documents()


        # -------------------------------------------------
        # 5️⃣ CHUNKING
        # -------------------------------------------------

        pipeline_status["state"] = "chunking"

        tqdm.write("Running chunk_all_documents")

        chunk_all_documents()


        # -------------------------------------------------
        # 6️⃣ EMBEDDINGS
        # -------------------------------------------------

        pipeline_status["state"] = "embedding"

        tqdm.write("Running embed_all_chunks")

        embed_all_chunks()


        pipeline_status["state"] = "idle"
        pipeline_status["last_update"] = datetime.now().isoformat()

        print("\nPipeline finalizado\n")

        return True

    except Exception as e:

        pipeline_status["state"] = "error"

        print("\nErro no pipeline:")
        print(e)

        return False


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    run_pipeline()