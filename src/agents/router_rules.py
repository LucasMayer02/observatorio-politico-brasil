import re

NEWS_KEYWORDS = [
    "war",
    "conflict",
    "geopolitics",
    "sanctions",
    "diplomacy",
    "military",
    "election",
    "government",
    "policy"
]

AUTOMATION_KEYWORDS = [
    "briefing",
    "report",
    "summary",
    "analysis report",
    "generate briefing",
    "write report"
]


def rule_router(question: str):

    q = question.lower()

    for word in AUTOMATION_KEYWORDS:
        if word in q:
            return "automation"

    for word in NEWS_KEYWORDS:
        if word in q:
            return "news_analysis"

    # nenhuma regra encontrada
    return None