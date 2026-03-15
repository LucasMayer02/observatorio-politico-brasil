# Observatório Político Brasil

PoC open source de sistema agêntico em LangChain/LangGraph para responder perguntas sobre notícias políticas recentes do Brasil com citações verificáveis e gerar briefings automáticos por tema e período.

## Objetivo

Facilitar o acesso organizado e verificável a informações públicas sobre política brasileira usando RAG, agentes, automação e MCP.

## Escopo inicial

- Notícias políticas do Brasil
- Fontes públicas e abertas
- Perguntas e respostas com citações
- Geração de briefings automáticos
- Integração com MCP

## Stack

- Python
- LangChain
- LangGraph
- Chroma
- Streamlit
- Ollama
- HuggingFace Embeddings

## Estrutura do projeto

- `app/`: interface Streamlit
- `ingest/`: coleta, limpeza, chunking e indexação
- `src/`: agentes, grafo, RAG, MCP e utilitários
- `eval/`: avaliação de RAG e automação
- `tests/`: testes automatizados

## Status

Etapa 2 em andamento: estrutura inicial do projeto criada, grafo base implementado e interface Streamlit funcionando.

## Próximos passos

- Implementar coleta de notícias
- Limpar e normalizar os dados
- Criar pipeline de chunking e indexação
- Implementar retriever real
- Adicionar citações e self-check
- Implementar automação de briefing
- Integrar MCP