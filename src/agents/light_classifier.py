from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

LABELS = [
    "news_analysis",
    "automation",
    "refusal"
]


def classify_question(question: str, labels = LABELS):

    result = classifier(question, labels)

    return result["labels"][0]