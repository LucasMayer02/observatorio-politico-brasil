import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag.retriever import get_retriever


def main():
    retriever = get_retriever(k=3)

    query = "Qual o estado de saúde de Bolsonaro?"

    docs = retriever.invoke(query)

    print("\nRESULTADOS:\n")

    for i, doc in enumerate(docs):
        print("---------")
        print(f"Resultado {i+1}")
        print("Fonte:", doc.metadata["source"])
        print("Título:", doc.metadata["title"])
        print("Texto:", doc.page_content[:400])
        print()


if __name__ == "__main__":
    main()