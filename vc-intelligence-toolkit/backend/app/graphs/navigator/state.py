from typing import Any, TypedDict


class NavigatorState(TypedDict, total=False):
    candidate: dict[str, Any]
    diligence: dict[str, Any]
    application: dict[str, Any] | str
    retrieved_context: list[dict[str, Any]]
    scores: dict[str, float]
    recommendation: dict[str, Any]
