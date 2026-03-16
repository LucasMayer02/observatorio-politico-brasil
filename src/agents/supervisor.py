from src.agents.router_rules import rule_router
from src.agents.light_classifier import classify_question

from ..graph.state import GraphState


def supervisor_node(state: GraphState) -> GraphState:

    question = state["question"]

    # 1️⃣ regras rápidas
    route = rule_router(question)

    if route:
        return {"route": route}

    # 2️⃣ fallback para classificador
    route = classify_question(question)

    return {"route": route}

if __name__ == "__main__":

    query = input("Pergunta: ")

    state: GraphState = {
        "question": query
    }

    result = supervisor_node(state)

    print("Route:", result["route"])
