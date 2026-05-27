"""
Golden dataset eval — run by CI on every PR.
Checks that the agent produces non-empty answers for known queries.
"""
import pytest
from unittest.mock import patch, MagicMock


GOLDEN_DATASET = [
    {
        "query": "What is 25 * 48?",
        "expected_keywords": ["1200"],
        "tools": ["calculator"],
    },
    {
        "query": "Explain what LangGraph is in one sentence.",
        "expected_keywords": ["graph", "agent", "state"],
        "tools": ["web_search"],
    },
]


class TestAgentEval:
    """
    Lightweight eval tests that mock external API calls
    so they run fast in CI without consuming API quota.
    """

    def _mock_planner_response(self, query: str, tools: list) -> MagicMock:
        import json
        m = MagicMock()
        m.content = json.dumps({
            "sub_questions": [query],
            "tools_needed": tools,
        })
        return m

    def _mock_synthesizer_response(self, answer: str) -> MagicMock:
        m = MagicMock()
        m.content = answer
        return m

    @pytest.mark.parametrize("sample", GOLDEN_DATASET)
    def test_agent_returns_answer(self, sample):
        """Agent should return a non-empty answer for every golden query."""
        with patch("agent.nodes.llm") as mock_llm, \
             patch("agent.nodes.web_tool") as mock_web, \
             patch("agent.nodes.vector_tool") as mock_vec, \
             patch("agent.nodes.calc_tool") as mock_calc:

            mock_llm.invoke.side_effect = [
                self._mock_planner_response(sample["query"], sample["tools"]),
                self._mock_synthesizer_response(
                    f"Mock answer containing {' '.join(sample['expected_keywords'])}"
                ),
            ]
            mock_web.search.return_value = [{"content": "mock web result", "url": "http://test.com"}]
            mock_vec.search.return_value = [{"content": "mock doc", "source": "test.pdf", "score": 0.9}]
            mock_calc.evaluate.return_value = 1200

            from agent.graph import research_graph

            result = research_graph.invoke({
                "query": sample["query"],
                "sub_questions": [],
                "retrieved_docs": [],
                "web_results": [],
                "calc_results": [],
                "final_answer": None,
                "citations": [],
                "tools_used": [],
                "error": None,
            })

            assert result.get("final_answer"), "Agent must return a non-empty answer"
            answer_lower = result["final_answer"].lower()
            for kw in sample["expected_keywords"]:
                assert kw.lower() in answer_lower, (
                    f"Expected keyword '{kw}' not found in answer: {result['final_answer']}"
                )
