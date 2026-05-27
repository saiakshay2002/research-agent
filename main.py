import time
import json
from dotenv import load_dotenv

load_dotenv()

from ops.tracer import configure_tracing
from ops.logger import QueryLogger
from ops.metrics import QUERY_COUNTER, QUERY_LATENCY, start_metrics_server
from agent.graph import research_graph

configure_tracing()

logger = QueryLogger()


def run_query(query: str) -> dict:
    """Run a single research query through the agent graph."""
    print(f"\n🔍 Query: {query}\n{'─'*60}")

    start = time.time()
    success = True
    result = {}

    try:
        initial_state = {
            "query": query,
            "sub_questions": [],
            "retrieved_docs": [],
            "web_results": [],
            "calc_results": [],
            "final_answer": None,
            "citations": [],
            "tools_used": [],
            "error": None,
        }

        result = research_graph.invoke(initial_state)
        print(f"\n✅ Answer:\n{result.get('final_answer', 'No answer generated.')}")

        if result.get("citations"):
            print(f"\n📎 Citations:")
            for c in result["citations"]:
                print(f"   • {c}")

    except Exception as e:
        success = False
        print(f"❌ Error: {e}")
        result = {"final_answer": str(e), "citations": [], "tools_used": []}

    finally:
        elapsed_ms = (time.time() - start) * 1000
        tools = result.get("tools_used", [])
        answer = result.get("final_answer", "")

        logger.log(
            query=query,
            tools_used=tools,
            latency_ms=elapsed_ms,
            success=success,
            answer_len=len(answer),
        )

        QUERY_COUNTER.labels(status="success" if success else "error").inc()
        QUERY_LATENCY.observe(elapsed_ms / 1000)

        print(f"\n⏱️  Latency: {elapsed_ms:.0f}ms | Tools: {tools}")

    return result


if __name__ == "__main__":
    start_metrics_server(port=8000)

    queries = [
    "What are the common diabetes medicines and their side effects?",
    "How does insulin work in treating diabetes?",
    "What are the different types of diabetes medications?",
]

    for q in queries:
        run_query(q)
        print("\n" + "="*60)
