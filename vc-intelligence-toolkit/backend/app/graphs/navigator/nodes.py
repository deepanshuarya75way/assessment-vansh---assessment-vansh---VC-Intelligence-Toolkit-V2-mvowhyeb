import asyncio
import json
import math
import re
from typing import Any

from app.core.config import settings
from app.prompts.navigator_prompts import (
    APPLICATION_PARSING_PROMPT,
    INTERVIEW_QUESTIONS_PROMPT,
    ROUTING_PROMPT,
    SWARMSPACE_PROGRAMS,
)
from app.schemas.recommendation import RecommendationJSON
from app.utils.embedding import embed_text
from app.utils.groq_client import get_groq_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

_program_embeddings: list[dict[str, Any]] | None = None


async def application_parsing_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Parsing SwarmSpace application...")
    application = state["application"]
    if isinstance(application, dict):
        logger.info("Application already structured; passing through")
        return {"application": application}

    content = await _call_groq(
        APPLICATION_PARSING_PROMPT.format(application_text=application),
        temperature=0.0,
        max_tokens=450,
    )
    parsed = _parse_json_object(content)
    logger.info("Parsed application for %s", parsed.get("founder_name", "unknown"))
    return {"application": parsed}


async def retrieve_context_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Retrieving SwarmSpace program context...")
    query_text = _combined_context_text(state)
    query_embedding = await asyncio.to_thread(embed_text, query_text)
    programs = await _get_program_embeddings()

    ranked = []
    for program in programs:
        ranked.append(
            {
                "name": program["name"],
                "description": program["description"],
                "relevance": _cosine_similarity(query_embedding, program["embedding"]),
            }
        )
    ranked.sort(key=lambda item: item["relevance"], reverse=True)
    logger.info("Retrieved %s program contexts", len(ranked))
    return {"retrieved_context": ranked}


async def evaluate_fit_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Evaluating SwarmSpace pathway fit...")
    content = await _call_groq(
        ROUTING_PROMPT.format(
            candidate=json.dumps(state.get("candidate", {}), indent=2, default=str),
            diligence=json.dumps(state.get("diligence", {}), indent=2, default=str),
            application=json.dumps(state.get("application", {}), indent=2, default=str),
            retrieved_context=json.dumps(
                state.get("retrieved_context", []), indent=2, default=str
            ),
        ),
        temperature=0.1,
        max_tokens=850,
    )
    evaluation = _parse_json_object(content)
    scores = _normalize_scores(evaluation.get("scores", {}))
    recommendation = {
        "recommended_pathway": evaluation.get("recommended_pathway")
        or _best_pathway(scores),
        "reasoning": evaluation.get("reasoning", ""),
        "weakest_evidence_areas": evaluation.get("weakest_evidence_areas", []),
    }
    logger.info("Best pathway: %s", recommendation["recommended_pathway"])
    return {"scores": scores, "recommendation": recommendation}


def confidence_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Deriving Navigator confidence...")
    scores = state.get("scores", {})
    sorted_scores = sorted(scores.values(), reverse=True)
    top_score = sorted_scores[0] if sorted_scores else 0.0
    margin = top_score - sorted_scores[1] if len(sorted_scores) > 1 else top_score
    diligence_confidence = float(state.get("diligence", {}).get("confidence") or 0.5)
    confidence = max(0.0, min(1.0, (top_score * 0.55) + (margin * 0.2) + (diligence_confidence * 0.25)))
    recommendation = {**state.get("recommendation", {}), "confidence": confidence}
    logger.info("Navigator confidence: %.2f", confidence)
    return {"recommendation": recommendation}


async def interview_question_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Generating Navigator interview questions...")
    content = await _call_groq(
        INTERVIEW_QUESTIONS_PROMPT.format(
            candidate=json.dumps(state.get("candidate", {}), indent=2, default=str),
            diligence=json.dumps(state.get("diligence", {}), indent=2, default=str),
            application=json.dumps(state.get("application", {}), indent=2, default=str),
            evaluation=json.dumps(state.get("recommendation", {}), indent=2, default=str),
        ),
        temperature=0.2,
        max_tokens=550,
    )
    questions = _parse_json_object(content).get("interview_questions", [])
    if not isinstance(questions, list):
        questions = [str(questions)]
    recommendation = {
        **state.get("recommendation", {}),
        "interview_questions": [str(question) for question in questions][:5],
    }
    logger.info("Generated %s interview questions", len(recommendation["interview_questions"]))
    return {"recommendation": recommendation}


def formatter_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Formatting Navigator recommendation...")
    recommendation = state.get("recommendation", {})
    confidence = float(recommendation.get("confidence") or 0.0)
    human_review = confidence < 0.75 or _needs_human_review(state)
    output = RecommendationJSON(
        recommended_pathway=recommendation.get("recommended_pathway") or "Monitor",
        confidence=confidence,
        interview_questions=recommendation.get("interview_questions") or [],
        reasoning=recommendation.get("reasoning") or "",
        human_review=human_review,
    ).model_dump()
    logger.info("Formatted Navigator recommendation: %s", output["recommended_pathway"])
    return {"recommendation": output}


async def _call_groq(prompt: str, temperature: float, max_tokens: int) -> str:
    client = get_groq_client()
    response = await client.chat.completions.create(
        model=settings.model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


async def _get_program_embeddings() -> list[dict[str, Any]]:
    global _program_embeddings
    if _program_embeddings is None:
        embeddings = []
        for program in SWARMSPACE_PROGRAMS:
            embedding = await asyncio.to_thread(embed_text, program["description"])
            embeddings.append({**program, "embedding": embedding})
        _program_embeddings = embeddings
    return _program_embeddings


def _combined_context_text(state: dict[str, Any]) -> str:
    return "\n".join(
        [
            json.dumps(state.get("candidate", {}), default=str),
            json.dumps(state.get("diligence", {}), default=str),
            json.dumps(state.get("application", {}), default=str),
        ]
    )


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _parse_json_object(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_scores(raw_scores: dict[str, Any]) -> dict[str, float]:
    scores = {}
    for program in SWARMSPACE_PROGRAMS:
        name = program["name"]
        try:
            scores[name] = max(0.0, min(1.0, float(raw_scores.get(name, 0.0))))
        except (TypeError, ValueError):
            scores[name] = 0.0
    return scores


def _best_pathway(scores: dict[str, float]) -> str:
    if not scores:
        return "Monitor"
    return max(scores, key=scores.get)


def _needs_human_review(state: dict[str, Any]) -> bool:
    diligence = state.get("diligence", {})
    application = state.get("application", {})
    if diligence.get("human_review_required"):
        return True
    weak_areas = state.get("recommendation", {}).get("weakest_evidence_areas") or []
    return bool(weak_areas) or "unknown" in json.dumps(application).lower()
