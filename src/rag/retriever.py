from src.rag.vectorstore import get_vectorstore


def get_retriever(k: int = 4):
    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": 8,
        },
    )

    return retriever