from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.graph.state import GraphState
from src.config import PROCESSED_DATA_DIR


VECTORSTORE_DIR_NAME = "vectorstore"
EMBEDDING_MODEL = "BAAI/bge-small-en"


# =========================================================
# CARREGAR EMBEDDINGS
# =========================================================

def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# =========================================================
# CARREGAR VECTOR STORE
# =========================================================

def load_vectorstore():

    base_dir = Path(PROCESSED_DATA_DIR).parent
    vectorstore_dir = base_dir / VECTORSTORE_DIR_NAME

    if not vectorstore_dir.exists():
        raise FileNotFoundError(
            f"Vector store não encontrado em {vectorstore_dir}"
        )

    embeddings = load_embeddings()

    vectorstore = Chroma(
        persist_directory=str(vectorstore_dir),
        embedding_function=embeddings
    )

    return vectorstore


# =========================================================
# CRIAR RETRIEVER
# =========================================================

def get_retriever(k: int = 5):

    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    return retriever


# =========================================================
# RETRIEVER AGENT
# =========================================================

def retriever_agent(state: GraphState, k: int = 5) -> GraphState:

    question = state["question"]

    retriever = get_retriever(k)

    docs = retriever.invoke(question)

    results = []

    for doc in docs:
        results.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })

    state["retrieved_docs"] = results

    return state