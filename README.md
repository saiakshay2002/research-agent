# 🔍 Multi-Tool Research Agent with Observability

A production-grade **Agentic RAG** system built with **LangGraph + LangSmith**, featuring multi-source retrieval, full execution tracing, and a real-time ops dashboard.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────┐
│    Planner Node     │  ← Breaks query into sub-questions
└────────┬────────────┘
         │
    ┌────┴──────────────┐
    ▼                   ▼
[Vector DB Tool]   [Web Search Tool]   [Calculator Tool]
 (Chroma + local)   (Tavily API)        (math expressions)
    │                   │                    │
    └────────┬──────────┘                    │
             ▼                              ▼
       ┌─────────────┐              ┌──────────────┐
       │  Reranker   │              │   Synthesizer │
       └──────┬──────┘              └──────┬───────┘
              └──────────┬─────────────────┘
                         ▼
                  Final Answer + Citations
                         │
                         ▼
              ┌─────────────────────┐
              │  LangSmith Tracing  │  ← Every node traced
              │  Prometheus Metrics │  ← Latency, tool usage
              │  SQLite Logs        │  ← Per-query ops log
              └─────────────────────┘
```

---

## 🗂️ Project Structure

```
research-agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py          # LangGraph state machine
│   ├── nodes.py          # Planner, Retriever, Synthesizer nodes
│   └── state.py          # AgentState TypedDict
├── tools/
│   ├── __init__.py
│   ├── vector_search.py  # Chroma vector DB retrieval
│   ├── web_search.py     # Tavily web search
│   └── calculator.py     # Math expression evaluator
├── ops/
│   ├── __init__.py
│   ├── logger.py         # SQLite query logger
│   ├── metrics.py        # Prometheus metrics
│   └── tracer.py         # LangSmith tracing config
├── dashboard/
│   └── app.py            # Streamlit ops dashboard
├── tests/
│   ├── test_tools.py
│   └── test_agent.py
├── .github/
│   └── workflows/
│       └── eval.yml      # CI eval pipeline
├── ingest.py             # Document ingestion script
├── main.py               # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/research-agent.git
cd research-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Ingest documents

```bash
python ingest.py --docs ./your-docs-folder
```

### 4. Run the agent

```bash
python main.py
```

### 5. Launch the ops dashboard

```bash
streamlit run dashboard/app.py
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (for LLM + embeddings) |
| `TAVILY_API_KEY` | Tavily search API key (free tier works) |
| `LANGCHAIN_API_KEY` | LangSmith API key (free tier works) |
| `LANGCHAIN_PROJECT` | LangSmith project name |
| `LANGCHAIN_TRACING_V2` | Set to `true` to enable tracing |

---

## 📊 Ops Features

| Feature | Tool | What it tracks |
|---|---|---|
| Execution tracing | LangSmith | Every node, input, output, latency |
| Query logging | SQLite | Query, tools used, latency, cost, tokens |
| Metrics | Prometheus | Tool usage count, p95 latency, error rate |
| Dashboard | Streamlit | Real-time ops view across all queries |
| CI evals | GitHub Actions | Runs golden Q&A eval on every PR |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🔄 CI/CD

Every PR triggers:
1. Unit tests for all tools and agent nodes
2. Golden dataset eval (10 Q&A pairs)
3. PR blocked if answer quality drops below threshold

---

## 📈 Resume Bullet

> Built a multi-tool agentic RAG system using LangGraph with vector DB, live web search, and calculator tools — integrated LangSmith tracing, Prometheus metrics, and a Streamlit ops dashboard tracking per-query latency, tool usage, and cost across all agent executions.

---

## 🛠️ Tech Stack

- **Agent framework**: LangGraph
- **LLM**: Groq LLaMA 3.3 70B
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (free, local)
- **Vector DB**: Chroma (local)
- **Web search**: Tavily API
- **Tracing**: LangSmith
- **Metrics**: Prometheus + prometheus-client
- **Dashboard**: Streamlit
- **Logging**: SQLite via Python sqlite3
- **CI**: GitHub Actions
