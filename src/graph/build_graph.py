from langgraph.graph import StateGraph, END

from src.graph.state import GraphState
from src.agents.supervisor import supervisor_node
from src.agents.retriever_agent import retriever_node
from src.agents.safety import safety_node
from src.agents.writer import writer_node
from src.agents.self_check import self_check_node
from src.agents.automation import automation_node


def route_after_supervisor(state: GraphState):
    route = state.get("route", "refuse")

    if route == "qna":
        return "retriever"

    if route == "automation":
        return "automation"

    return "refuse"


def build_graph():
    graph = StateGraph(GraphState)

    # Nós
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("safety", safety_node)
    graph.add_node("writer", writer_node)
    graph.add_node("self_check", self_check_node)
    graph.add_node("automation", automation_node)

    # Nó inicial
    graph.set_entry_point("supervisor")

    # Roteamento depois do supervisor
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "retriever": "retriever",
            "automation": "automation",
            "refuse": END,
        },
    )

    # Fluxo Q&A
    graph.add_edge("retriever", "safety")
    graph.add_edge("safety", "writer")
    graph.add_edge("writer", "self_check")
    graph.add_edge("self_check", END)

    # Fluxo automação
    graph.add_edge("automation", END)

    return graph.compile()