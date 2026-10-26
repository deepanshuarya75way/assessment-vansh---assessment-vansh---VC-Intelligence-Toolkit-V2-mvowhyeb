from typing import Any, TypedDict


class MoatlensState(TypedDict, total=False):
    candidate: dict[str, Any]
    extracted_claims: dict[str, Any]
    bull_report: str
    bear_report: str
    conflicts: list[str]
    final_report: dict[str, Any]
    retry_count: int
