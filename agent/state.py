from typing import TypedDict, Annotated, List, Optional
import operator


class AgentState(TypedDict):
    query: str
    sub_questions: List[str]
    retrieved_docs: Annotated[List[dict], operator.add]
    web_results: Annotated[List[dict], operator.add]
    calc_results: Annotated[List[dict], operator.add]
    final_answer: Optional[str]
    citations: List[str]
    tools_used: Annotated[List[str], operator.add]
    error: Optional[str]
