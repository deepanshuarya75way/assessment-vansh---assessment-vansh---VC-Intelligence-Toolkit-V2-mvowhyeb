
from typing import Any
from math import isfinite

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.investment_thesis import InvestmentThesisRule, ScreeningResult


def compare(actual: Any, operator: str, expected: Any) -> bool:
    """Safely compare a startup value against a thesis criterion."""
    if actual is None:
        return False

    try:
        if operator == "eq":
            return actual == expected

        if operator == "neq":
            return actual != expected

        if operator in {"gt", "gte", "lt", "lte"}:
            if (
                isinstance(actual, bool)
                or isinstance(expected, bool)
                or not isinstance(actual, (int, float))
                or not isinstance(expected, (int, float))
            ):
                return False

            if not isfinite(actual) or not isfinite(expected):
                return False

            if operator == "gt":
                return actual > expected
            if operator == "gte":
                return actual >= expected
            if operator == "lt":
                return actual < expected
            return actual <= expected

        if operator == "in":
            if isinstance(expected, (list, tuple, set)):
                return actual in expected
            if isinstance(expected, str) and isinstance(actual, str):
                return actual.casefold() in expected.casefold()
            return False

        if operator == "contains":
            if isinstance(actual, str) and isinstance(expected, str):
                return expected.casefold() in actual.casefold()

            if isinstance(actual, (list, tuple, set)):
                return expected in actual

            if isinstance(actual, dict) and isinstance(expected, str):
                return expected in actual

            return False

    except (TypeError, ValueError, OverflowError):
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
        missing = actual is None
        passed = compare(actual, rule.operator, rule.expected_value)

        weight = float(rule.weight)
        total_weight += weight

        if passed:
            weighted_pass += weight
        elif rule.is_mandatory:
            mandatory_failures.append(rule.name)

        if passed:
            reason = "Criterion met."
        elif missing:
            reason = "Required startup information is missing."
        else:
            reason = (
                f"Actual value {actual!r} does not satisfy "
                f"{rule.operator} {rule.expected_value!r}."
            )

        matrix.append(
            {
                "rule_id": rule.id,
                "rule": rule.name,
                "field": rule.field_name,
                "operator": rule.operator,
                "expected": rule.expected_value,
                "actual": actual,
                "weight": weight,
                "mandatory": rule.is_mandatory,
                "passed": passed,
                "status": "met" if passed else "missed",
                "reason": reason,
                "missing_data": missing,
            }
        )

    score = (
        round(weighted_pass / total_weight * 100, 2)
        if total_weight > 0
        else 0.0
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

    # Explicit screening data overrides candidate fields.
    startup.update(startup_data)

    # Support common aliases without requiring separate rule logic.
    aliases = {
        "sector": ("target_sector", "industry", "sectors"),
        "target_sector": ("sector", "industry", "sectors"),
        "industry": ("sector", "target_sector", "sectors"),
        "valuation": ("valuation_cap", "valuation_usd"),
        "founder_experience": (
            "founder_background",
            "founder_bio",
            "founder_experience_years",
        ),
    }

    for field, alternatives in aliases.items():
        if startup.get(field) is None:
            for alternative in alternatives:
                if startup.get(alternative) is not None:
                    startup[field] = startup[alternative]
                    break

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
