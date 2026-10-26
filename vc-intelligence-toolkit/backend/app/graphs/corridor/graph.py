from langgraph.graph import END, START, StateGraph

from app.graphs.corridor.nodes import (
    embedding_similarity_node,
    fetch_arxiv_node,
    fetch_github_node,
    fetch_hn_node,
    merge_node,
    output_formatter_node,
    reasoning_node,
)
from app.graphs.corridor.state import CorridorState

builder = StateGraph(CorridorState)

builder.add_node("fetch_github", fetch_github_node)
builder.add_node("fetch_hn", fetch_hn_node)
builder.add_node("fetch_arxiv", fetch_arxiv_node)
builder.add_node("merge", merge_node)
builder.add_node("embedding_similarity", embedding_similarity_node)
builder.add_node("reasoning", reasoning_node)
builder.add_node("output_formatter", output_formatter_node)

builder.add_edge(START, "fetch_github")
builder.add_edge(START, "fetch_hn")
builder.add_edge(START, "fetch_arxiv")
builder.add_edge("fetch_github", "merge")
builder.add_edge("fetch_hn", "merge")
builder.add_edge("fetch_arxiv", "merge")
builder.add_edge("merge", "embedding_similarity")
builder.add_edge("embedding_similarity", "reasoning")
builder.add_edge("reasoning", "output_formatter")
builder.add_edge("output_formatter", END)

corridor_graph = builder.compile()
