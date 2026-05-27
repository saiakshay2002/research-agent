from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import planner_node, retriever_node, synthesizer_node, error_node


def should_synthesize(state: AgentState) -> str:
    if state.get("error"):
        return "handle_error"
    return "synthesizer"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("handle_error", error_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_conditional_edges(
        "retriever",
        should_synthesize,
        {
            "synthesizer": "synthesizer",
            "handle_error": "handle_error",
        },
    )
    graph.add_edge("synthesizer", END)
    graph.add_edge("handle_error", END)

    return graph.compile()


research_graph = build_graph()