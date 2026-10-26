from typing import Any, TypedDict


class CorridorState(TypedDict, total=False):
    search_query: str
    github_results: list[dict[str, Any]]
    hn_results: list[dict[str, Any]]
    arxiv_results: list[dict[str, Any]]
    merged_candidates: list[dict[str, Any]]
    portfolio_context: list[dict[str, Any]]
    candidate_scores: list[dict[str, Any]]
    top_candidates: list[dict[str, Any]]
    reasoning: list[dict[str, Any]]
    final_output: list[dict[str, Any]]
