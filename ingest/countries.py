import json
import re
import unicodedata
from pathlib import Path
from functools import lru_cache

import spacy
import pycountry
from tqdm import tqdm

from src.config import PROCESSED_DATA_DIR
from src.utils.util_dicts import DEMONYMS_TO_ISO2, COUNTRY_TO_CONTINENT


# ----------------------------------
# MODELO NLP
# ----------------------------------

nlp = spacy.load("en_core_web_sm", disable=["tagger","parser"])

# ----------------------------------
# COUNTRY DICTIONARIES
# ----------------------------------

COUNTRY_NAME_TO_ISO2 = {
    c.name.lower(): c.alpha_2
    for c in pycountry.countries
}

COUNTRY_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in COUNTRY_NAME_TO_ISO2.keys()) + r")\b",
    re.IGNORECASE
)


# ----------------------------------
# TEXT NORMALIZATION
# ----------------------------------

def normalize_text(text):

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    return text.lower()


# ----------------------------------
# FAST COUNTRY DETECTION
# ----------------------------------

def extract_countries_fast(text):

    text = normalize_text(text)

    countries = set()

    # 1️⃣ regex country names
    matches = COUNTRY_REGEX.findall(text)

    for m in matches:

        iso2 = COUNTRY_NAME_TO_ISO2.get(m.lower())

        if iso2:
            countries.add(iso2)

    # 2️⃣ demonyms
    tokens = text.split()

    for token in tokens:

        if token in DEMONYMS_TO_ISO2:

            countries.add(DEMONYMS_TO_ISO2[token])

    # 3️⃣ NER fallback
    if not countries:

        doc = nlp(text)

        for ent in doc.ents:

            if ent.label_ == "GPE":

                name = ent.text.lower()

                if name in COUNTRY_NAME_TO_ISO2:

                    countries.add(COUNTRY_NAME_TO_ISO2[name])

    return list(countries)


# ----------------------------------
# PIPELINE STEP
# ----------------------------------

def add_countries_metadata():

    processed_dir = Path(PROCESSED_DATA_DIR)

    files = list(processed_dir.glob("*.json"))

    for file in tqdm(files):

        with open(file, "r", encoding="utf-8") as f:

            article = json.load(f)

        text = f"{article.get('title','')} {article.get('summary','')}"
        
        text = text.replace("'",' ')

        countries = extract_countries_fast(text)

        regions = set()

        for c in countries:

            if c in COUNTRY_TO_CONTINENT:

                regions.add(COUNTRY_TO_CONTINENT[c])

        article["countries"] = countries
        article["regions"] = list(regions)

        with open(file, "w", encoding="utf-8") as f:

            json.dump(article, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":

    add_countries_metadata()