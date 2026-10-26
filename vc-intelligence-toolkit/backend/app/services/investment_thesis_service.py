
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.investment_thesis import InvestmentThesisRule, ScreeningResult


def compare(actual: Any, operator: str, expected: Any) -> bool:
    if actual is None:
        return False

    try:
        if operator == "eq":
            return actual == expected
        if operator == "neq":
            return actual != expected
        if operator == "gt":
            return actual > expected
        if operator == "gte":
            return actual >= expected
        if operator == "lt":
            return actual < expected
        if operator == "lte":
            return actual <= expected
        if operator == "in":
            return actual in expected
        if operator == "contains":
            return expected in actual
    except (TypeError, ValueError):
        return False

    return False


def evaluate_rules(
    rules: list[InvestmentThesisRule],
    startup: dict[str, Any],
) -> dict[str, Any]:
    matrix = []
    weighted_pass = 0.0
    total_weight = 0.0
    mandatory_failures = []

    for rule in rules:
        if not rule.is_active:
            continue

        actual = startup.get(rule.field_name)
        passed = compare(actual, rule.operator, rule.expected_value)

        total_weight += rule.weight
        if passed:
            weighted_pass += rule.weight
        elif rule.is_mandatory:
            mandatory_failures.append(rule.name)

        matrix.append({
            "rule_id": rule.id,
            "rule": rule.name,
            "field": rule.field_name,
            "operator": rule.operator,
            "expected": rule.expected_value,
            "actual": actual,
            "weight": rule.weight,
            "mandatory": rule.is_mandatory,
            "passed": passed,
            "status": "met" if passed else "missed",
        })

    score = (
        round(weighted_pass / total_weight * 100, 2)
        if total_weight else 0.0
    )

    return {
        "compatibility_score": score,
        "status": "disqualified" if mandatory_failures else "qualified",
        "mandatory_failures": mandatory_failures,
        "matrix": matrix,
    }


async def screen_candidate(
    session: AsyncSession,
    candidate_id: int,
    startup_data: dict[str, Any],
) -> dict[str, Any]:
    candidate = await session.get(Candidate, candidate_id)

    if candidate is None:
        raise LookupError("Candidate not found")

    startup = {
        "id": candidate.id,
        "company": candidate.company,
        "description": candidate.description,
        "source": candidate.source,
        "github_url": candidate.github_url,
        "similarity_score": candidate.similarity_score,
        "confidence": candidate.confidence,
        "portfolio_matches": candidate.portfolio_matches,
    }
    startup.update(startup_data)

    query = select(InvestmentThesisRule).where(
        InvestmentThesisRule.is_active.is_(True)
    )
    rules = list((await session.scalars(query)).all())

    if not rules:
        raise ValueError("No active investment thesis rules are configured")

    result = evaluate_rules(rules, startup)

    record = ScreeningResult(
        candidate_id=candidate_id,
        compatibility_score=result["compatibility_score"],
        status=result["status"],
        matrix=result["matrix"],
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    return {
        "id": record.id,
        "candidate_id": candidate_id,
        **result,
        "created_at": record.created_at,
    }
