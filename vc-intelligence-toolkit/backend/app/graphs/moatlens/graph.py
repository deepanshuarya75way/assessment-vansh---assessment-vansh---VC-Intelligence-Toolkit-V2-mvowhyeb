from langgraph.graph import END, START, StateGraph

from app.graphs.moatlens.nodes import (
    bear_agent_node,
    bull_agent_node,
    claim_extraction_node,
    conflict_checker_node,
    reflection_edge,
    reflection_node,
    synthesis_node,
)
from app.graphs.moatlens.state import MoatlensState

builder = StateGraph(MoatlensState)

builder.add_node("claim_extraction", claim_extraction_node)
builder.add_node("bull_agent", bull_agent_node)
builder.add_node("bear_agent", bear_agent_node)
builder.add_node("conflict_checker", conflict_checker_node)
builder.add_node("reflection", reflection_node)
builder.add_node("synthesis", synthesis_node)

builder.add_edge(START, "claim_extraction")
builder.add_edge("claim_extraction", "bull_agent")
builder.add_edge("claim_extraction", "bear_agent")
builder.add_edge("bull_agent", "conflict_checker")
builder.add_edge("bear_agent", "conflict_checker")
builder.add_conditional_edges(
    "conflict_checker",
    reflection_edge,
    {
        "reflect": "reflection",
        "synthesize": "synthesis",
    },
)
builder.add_edge("reflection", "bull_agent")
builder.add_edge("reflection", "bear_agent")
builder.add_edge("synthesis", END)

moatlens_graph = builder.compile()
