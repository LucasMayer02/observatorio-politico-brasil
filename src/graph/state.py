from typing import TypedDict, List, Dict, Any


class GraphState(TypedDict, total=False):
    # pergunta do usuário
    question: str

    # rota escolhida pelo supervisor
    route: str

    # documentos recuperados pelo retriever
    retrieved_docs: List[Dict[str, Any]]

    # resposta gerada
    answer: str

    # citações usadas
    citations: List[Dict[str, Any]]

    # resultado do self-check
    self_check_passed: bool

    # contador de tentativas
    retry_count: int

    # resultado da automação (briefing)
    automation_result: Dict[str, Any]

    # motivo de recusa
    refusal_reason: str