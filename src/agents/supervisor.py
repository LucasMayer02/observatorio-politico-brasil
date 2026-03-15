def supervisor_node(state):
    question = state.get("question", "").strip().lower()

    if not question:
        return {
            "route": "refuse",
            "refusal_reason": "Pergunta vazia ou inválida."
        }

    automation_keywords = [
        "briefing",
        "resumo",
        "relatório",
        "timeline",
        "linha do tempo"
    ]

    if any(keyword in question for keyword in automation_keywords):
        return {"route": "automation"}

    return {"route": "qna"}