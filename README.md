# LINK Apresentação : https://app.slidespeak.co/presentation/cmmtw7a3u012ep408eq0ckd4f/share?openPanel=ASSISTANT


# Observatório Político do Brasil

Sistema baseado em **RAG (Retrieval-Augmented Generation)** para consulta e geração automática de briefings políticos a partir de notícias recentes.

O projeto utiliza **LLMs locais via Ollama**, **LangGraph para orquestração**, **vector database (Chroma)** para recuperação de documentos.

---

# Objetivo do Projeto

O objetivo do sistema é permitir:

1. **Responder perguntas sobre política brasileira** com base em notícias reais.
2. **Gerar briefings automáticos** sobre temas políticos recentes.
3. Garantir que as respostas sejam **baseadas em evidências do corpus**.
4. Demonstrar o uso de **LLMs integrados a sistemas de recuperação e automação**.
5. Integrar ferramentas externas através do **Model Context Protocol (MCP)**. (NÃO FOI POSSÍVEL REALIZAR)

---

# Arquitetura do Sistema

O sistema é dividido em quatro camadas principais.

```
Usuário
   │
   ▼
Interface (CLI / Streamlit)
   │
   ▼
LangGraph Agent
   │
   ├── RAG (consulta)
   │     ├── ChromaDB
   │     ├── embeddings (nomic-embed-text)
   │     └── LLM (Qwen via Ollama)
   │
   ├── Automação
   │     └── geração de briefings
   │
   └── MCP Tools
         ├── list_articles
         ├── get_article
         └── build_timeline
```

---

# Tecnologias Utilizadas

### LLM

* Ollama
* Modelo: **qwen2.5:7b** (SE MUITO PESADO USAR qwen2.5:3b)

### Frameworks

* LangChain
* LangGraph

### Banco Vetorial

* ChromaDB

### Embeddings

* nomic-embed-text

### Interface

* Streamlit

### Coleta de notícias

* RSS feeds
* Trafilatura

### Outras bibliotecas

* pandas
* numpy
* tqdm

---

# Estrutura do Projeto

```
src/

agents/
    automation.py
    qa_agent.py

graph/
    build_graph.py

retrieval/
    retriever.py
    vector_store.py

mcp/
    server.py
    client.py
    tools.py

data/
    raw/
    processed/

config.py
```

---

# Corpus de Dados

O corpus é composto por notícias políticas coletadas de fontes públicas, incluindo:

* Agência Brasil
* G1
* Terra
* r7
* Folha
* Estadão
* Correios Brasiliense
* O globo
* ...

Os dados passam por:

1. download de feeds RSS
2. extração de conteúdo
3. limpeza do texto
4. indexação no banco vetorial

Campos armazenados:

```
doc_id
title
source
published_at
url
content_clean
```

---

# Pipeline RAG

O pipeline de perguntas segue as etapas:

### 1. Entrada da pergunta

Usuário envia uma pergunta.

Exemplo:

```
O que aconteceu com Bolsonaro nos últimos dias?
```

---

### 2. Recuperação de documentos

O sistema busca documentos relevantes no **ChromaDB** utilizando embeddings.

```
embedding(question)
   ↓
vector search
   ↓
top-k documentos
```

---

### 3. Geração da resposta

O LLM recebe:

* pergunta do usuário
* trechos recuperados
* instruções de grounding

O modelo então gera a resposta baseada nos documentos.

---

### 4. Validação da resposta

O sistema executa um **self-check** para verificar se a resposta está suportada pelas evidências recuperadas.

Se não houver evidência suficiente:

```
Self-check reprovado
Motivo: Pergunta não suportada pelas evidências recuperadas
```

---

# Automação de Briefings

Além do modo de perguntas, o sistema também gera **briefings automáticos**.

Exemplo de comando:

```
Gerar briefing sobre Bolsonaro nos últimos 7 dias
```

O sistema:

1. identifica o tema
2. recupera notícias recentes
3. organiza os eventos
4. gera um resumo estruturado

Formato do briefing:

```
Resumo executivo

Principais eventos

Fontes utilizadas
```

---

# Integração com MCP (NÃO FOI COMPLETADO)

O projeto implementa um **servidor MCP próprio** para expor ferramentas estruturadas de acesso ao corpus.

Servidor MCP:

```
src/mcp/server.py
```

Cliente MCP:

```
src/mcp/client.py
```

---

# Tools MCP Disponíveis (INCOMPLETO)

## list_articles

Lista artigos disponíveis no corpus.

Entrada:

```
{}
```

Saída:

```
lista de artigos
```

---

## get_article

Retorna o conteúdo completo de um artigo.

Entrada:

```
doc_id
```

Saída:

```
title
source
published_at
url
content_clean
```

---

## build_timeline

Constrói uma linha do tempo de eventos relacionados a um tema.

Entrada:

```
keyword
```

Saída:

```
lista cronológica de artigos
```

---

# Segurança do MCP (INCOMPLETO)

Para evitar uso indevido do sistema, foram implementadas medidas de segurança.

### Allowlist de ferramentas

Apenas três tools são expostas:

```
list_articles
get_article
build_timeline
```

Nenhuma outra função do sistema pode ser chamada via MCP.

---

### Escopo restrito

O servidor MCP tem acesso apenas ao:

```
data/processed
```

Não há acesso a:

* sistema operacional
* arquivos externos
* rede

---

### Controle de acesso

As tools não permitem:

* execução de código
* escrita em disco
* chamadas arbitrárias

---

### Registro de chamadas

As chamadas MCP são registradas no log:

```
ListToolsRequest
CallToolRequest
```

Isso permite auditar o uso das ferramentas.

---

# Avaliação do Sistema

A avaliação considerou dois aspectos principais.

---

## Qualidade das respostas (RAG)

Critérios avaliados:

* relevância das respostas
* grounding em documentos
* presença de citações
* robustez a perguntas fora do corpus

O sistema utiliza **self-checking** para evitar alucinações.

---

## Qualidade dos briefings

Os briefings gerados foram avaliados considerando:

* fidelidade às fontes
* clareza
* organização dos eventos
* cobertura temporal

---

# Limitações

Algumas limitações do sistema incluem:

* dependência da cobertura do corpus
* ausência de verificação factual externa
* possível perda de contexto em documentos muito longos

---

# Como Executar

## 1. Instalar dependências

```
pip install -r requirements.txt
```

---

## 2. Instalar modelos Ollama

```
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

---

## 3. Iniciar servidor MCP

```
python -m src.mcp.server
```

---

## 4. Executar cliente MCP

```
python -m src.mcp.client
```

---

## 5. Executar o sistema

```
python src/main.py
```

ou

```
streamlit run src/app.py
```

---

# Exemplo de Uso

Pergunta:

```
Quem ganhou a Copa do Mundo de 1994?
```

Resultado:

```
Self-check reprovado
Motivo: Pergunta não suportada pelas evidências recuperadas
```

---

Pergunta:

```
Gerar briefing sobre Bolsonaro nos últimos 7 dias
```

Resultado:

```
Resumo executivo
...

Principais eventos
...

Fontes utilizadas
...
```

---

# Conclusão

O projeto demonstra a integração de:

* **LLMs locais**
* **RAG**
* **automação de tarefas**

Esse tipo de arquitetura permite construir sistemas de IA **mais confiáveis, auditáveis e baseados em evidências**.

