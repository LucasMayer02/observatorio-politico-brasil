import asyncio

from langchain_ollama import ChatOllama

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.mcp.tools import get_mcp_tools
import json

def normalize_mcp_result(result):
    import json

    if isinstance(result, dict):
        return result

    if isinstance(result, list) and len(result) > 0:
        first = result[0]

        if isinstance(first, dict) and "text" in first:
            try:
                return json.loads(first["text"])
            except Exception:
                return {"content_clean": first["text"]}

    return {}

def automation_node(state):
    question = state.get("question", "").strip()

    if not question:
        return {
            "automation_result": {
                "status": "error",
                "message": "Pergunta vazia para automação.",
                "briefing": "",
                "sources": []
            }
        }

    tools = get_mcp_tools()

    timeline_tool = None
    article_tool = None

    for tool in tools:
        if tool.name == "build_timeline":
            timeline_tool = tool
        elif tool.name == "get_article":
            article_tool = tool

    if timeline_tool is None or article_tool is None:
        return {
            "automation_result": {
                "status": "error",
                "message": "Tools MCP necessárias não encontradas.",
                "briefing": "",
                "sources": []
            }
        }

    keyword = "bolsonaro"
    lowered = question.lower()

    if "stf" in lowered:
        keyword = "stf"
    elif "senado" in lowered:
        keyword = "senado"
    elif "câmara" in lowered or "camara" in lowered:
        keyword = "câmara"
    elif "congresso" in lowered:
        keyword = "congresso"
    elif "bolsonaro" in lowered:
        keyword = "bolsonaro"

    timeline = asyncio.run(timeline_tool.ainvoke({"keyword": keyword}))

    if not timeline:
        return {
            "automation_result": {
                "status": "no_evidence",
                "message": "Não encontrei evidências suficientes no corpus atual.",
                "briefing": "",
                "sources": []
            }
        }

    evidence_blocks = []
    sources = []

    for idx, item in enumerate(timeline[:5], start=1):
        doc_id = item.get("doc_id", "")
        article_raw = asyncio.run(article_tool.ainvoke({"doc_id": doc_id}))
        article = normalize_mcp_result(article_raw)

        content = article.get("content_clean", "")[:700].strip()

        evidence_blocks.append(
            f"[{idx}] Título: {article.get('title', '')}\n"
            f"Fonte: {article.get('source', '')}\n"
            f"Data: {article.get('published_at', '')}\n"
            f"URL: {article.get('url', '')}\n"
            f"Conteúdo: {content}\n"
        )

        sources.append(
            {
                "id": idx,
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "published_at": article.get("published_at", ""),
                "source": article.get("source", ""),
                "snippet": content[:300],
            }
        )

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    prompt = f"""
Você é um assistente que gera briefings políticos com base apenas nas evidências fornecidas.

Pedido:
{question}

Evidências:
{chr(10).join(evidence_blocks)}

Instruções:
- Responder em português.
- Usar somente as evidências fornecidas.
- Produzir um briefing curto e claro.
- Organizar a resposta em:
  1. Resumo executivo
  2. Principais eventos
  3. Fontes utilizadas
- Não inventar fatos.
- Como existem evidências fornecidas, gere o briefing com base nelas.
- Só responda "Não encontrei evidências suficientes no corpus atual." se as evidências estiverem vazias.
"""

    response = llm.invoke(prompt)
    briefing = response.content.strip()

    return {
        "automation_result": {
            "status": "ok" if briefing else "error",
            "message": "",
            "briefing": briefing,
            "sources": sources,
        }
    }