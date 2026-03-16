from src.rag.retriever import get_retriever


def retriever_node(state):
    question = state.get("question", "").strip()

    if not question:
        return {"retrieved_docs": []}

    retriever = get_retriever(k=4)
    docs = retriever.invoke(question)

    retrieved_docs = []

    for doc in docs:
        retrieved_docs.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
        )

    return {"retrieved_docs": retrieved_docs}