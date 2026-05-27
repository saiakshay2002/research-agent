import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import AgentState
from tools.vector_search import VectorSearchTool
from tools.web_search import WebSearchTool
from tools.calculator import CalculatorTool
from ops.logger import QueryLogger
from ops.metrics import (
    TOOL_USAGE_COUNTER,
    NODE_LATENCY,
    track_time,
)

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
logger = QueryLogger()
vector_tool = VectorSearchTool()
web_tool = WebSearchTool()
calc_tool = CalculatorTool()


def planner_node(state: AgentState) -> dict:
    """Break the user query into focused sub-questions."""
    with track_time(NODE_LATENCY, {"node": "planner"}):
        system = SystemMessage(content=(
            "You are a research planner. Given a user question, break it into "
            "2-4 focused sub-questions that together fully answer the original. "
            "Also decide which tools are needed: 'vector_search', 'web_search', 'calculator'. "
            "Respond ONLY as JSON: "
            '{"sub_questions": [...], "tools_needed": [...]}'
        ))
        human = HumanMessage(content=state["query"])
        response = llm.invoke([system, human])

        try:
            raw = response.content.strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            parsed = json.loads(raw)
            sub_questions = parsed.get("sub_questions", [state["query"]])
            tools_needed = parsed.get("tools_needed", ["web_search"])
        except Exception:
            sub_questions = [state["query"]]
            tools_needed = ["web_search"]

        return {
            "sub_questions": sub_questions,
            "tools_used": tools_needed,
        }


def retriever_node(state: AgentState) -> dict:
    """Run retrieval across all needed tools in parallel."""
    retrieved_docs = []
    web_results = []
    calc_results = []
    tools_used = state.get("tools_used", [])

    for question in state["sub_questions"]:

        if "vector_search" in tools_used:
            with track_time(NODE_LATENCY, {"node": "vector_search"}):
                TOOL_USAGE_COUNTER.labels(tool="vector_search").inc()
                docs = vector_tool.search(question, k=3)
                retrieved_docs.extend(docs)

        if "web_search" in tools_used:
            with track_time(NODE_LATENCY, {"node": "web_search"}):
                TOOL_USAGE_COUNTER.labels(tool="web_search").inc()
                results = web_tool.search(question)
                web_results.extend(results)

        if "calculator" in tools_used:
            math_match = re.search(r"[\d\s\+\-\*\/\(\)\.]+", question)
            if math_match:
                with track_time(NODE_LATENCY, {"node": "calculator"}):
                    TOOL_USAGE_COUNTER.labels(tool="calculator").inc()
                    result = calc_tool.evaluate(math_match.group())
                    calc_results.append({"expression": math_match.group(), "result": result})

    return {
        "retrieved_docs": retrieved_docs,
        "web_results": web_results,
        "calc_results": calc_results,
    }


def synthesizer_node(state: AgentState) -> dict:
    """Synthesize all retrieved context into a final cited answer."""
    with track_time(NODE_LATENCY, {"node": "synthesizer"}):
        context_parts = []
        citations = []

        for i, doc in enumerate(state["retrieved_docs"]):
            context_parts.append(f"[DOC-{i+1}] {doc.get('content', '')[:500]}")
            citations.append(f"DOC-{i+1}: {doc.get('source', 'Local document')}")

        for i, result in enumerate(state["web_results"]):
            context_parts.append(f"[WEB-{i+1}] {result.get('content', '')[:500]}")
            citations.append(f"WEB-{i+1}: {result.get('url', 'Web source')}")

        for calc in state["calc_results"]:
            context_parts.append(f"[CALC] {calc['expression']} = {calc['result']}")

        context = "\n\n".join(context_parts) if context_parts else "No context retrieved."

        system = SystemMessage(content=(
            "You are a research assistant. Answer the question using the provided context. "
            "Cite sources inline using their tags like [DOC-1] or [WEB-2]. "
            "Be concise, accurate, and structured. If context is insufficient, say so."
        ))
        human = HumanMessage(content=(
            f"Question: {state['query']}\n\nContext:\n{context}"
        ))

        response = llm.invoke([system, human])

        return {
            "final_answer": response.content,
            "citations": citations,
        }


def error_node(state: AgentState) -> dict:
    return {
        "final_answer": "An error occurred during research. Please try again.",
        "citations": [],
    }
