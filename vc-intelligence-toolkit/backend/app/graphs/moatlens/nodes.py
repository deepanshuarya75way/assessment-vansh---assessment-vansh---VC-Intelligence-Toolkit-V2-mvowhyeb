import json
import re
from typing import Any, Literal

from app.core.config import settings
from app.prompts.moatlens_prompts import (
    BEAR_AGENT_PROMPT,
    BULL_AGENT_PROMPT,
    CLAIM_EXTRACTION_PROMPT,
    CONFLICT_CHECKER_PROMPT,
    SYNTHESIS_PROMPT,
)
from app.schemas.diligence import DiligenceJSON
from app.utils.groq_client import get_groq_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def claim_extraction_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Extracting claims...")
    candidate = state["candidate"]
    candidate_text = "\n".join(
        [
            f"Company: {candidate.get('company', '')}",
            f"Description: {candidate.get('description', '')}",
            f"Reasoning: {candidate.get('reasoning', '')}",
            f"Source: {candidate.get('source', '')}",
            f"URL: {candidate.get('github_url', '')}",
        ]
    )
    content = await _call_groq(
        CLAIM_EXTRACTION_PROMPT.format(candidate_text=candidate_text)
        + "\n\nRespond only with valid JSON.",
        temperature=0.1,
        max_tokens=450,
    )
    claims = _parse_json_object(content)
    logger.info("Extracted claims for %s", claims.get("company", candidate.get("company")))
    return {"extracted_claims": claims, "retry_count": state.get("retry_count", 0)}


async def bull_agent_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Running Bull Agent...")
    report = await _call_groq(
        BULL_AGENT_PROMPT.format(
            extracted_claims=json.dumps(state.get("extracted_claims", {}), indent=2)
        )
        + "\n\nRespond only with valid JSON.",
        temperature=0.25,
        max_tokens=650,
    )
    logger.info("Bull Agent completed")
    return {"bull_report": report.strip()}


async def bear_agent_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Running Bear Agent...")
    report = await _call_groq(
        BEAR_AGENT_PROMPT.format(
            extracted_claims=json.dumps(state.get("extracted_claims", {}), indent=2)
        )
        + "\n\nRespond only with valid JSON.",
        temperature=0.25,
        max_tokens=650,
    )
    logger.info("Bear Agent completed")
    return {"bear_report": report.strip()}


async def conflict_checker_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Checking conflicts...")
    content = await _call_groq(
        CONFLICT_CHECKER_PROMPT.format(
            bull_report=state.get("bull_report", ""),
            bear_report=state.get("bear_report", ""),
        )
        + "\n\nRespond only with valid JSON.",
        temperature=0.0,
        max_tokens=350,
    )
    conflicts = _parse_json_object(content).get("conflicts", [])
    if not isinstance(conflicts, list):
        conflicts = [str(conflicts)]
    logger.info("Conflict check found %s conflicts", len(conflicts))
    return {"conflicts": [str(conflict) for conflict in conflicts]}


def reflection_node(state: dict[str, Any]) -> dict[str, Any]:
    retry_count = state.get("retry_count", 0) + 1
    logger.info("Reflecting on conflicts; retry count is %s", retry_count)
    return {"retry_count": retry_count}


def reflection_edge(state: dict[str, Any]) -> Literal["reflect", "synthesize"]:
    conflicts = state.get("conflicts") or []
    retry_count = state.get("retry_count", 0)
    if conflicts and retry_count < 1:
        logger.info("Reflection loop reachable: routing back to Bull/Bear agents")
        return "reflect"
    logger.info("Reflection loop not taken; proceeding to synthesis")
    return "synthesize"


async def synthesis_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Synthesizing report...")
    content = await _call_groq(
        SYNTHESIS_PROMPT.format(
            extracted_claims=json.dumps(state.get("extracted_claims", {}), indent=2),
            bull_report=state.get("bull_report", ""),
            bear_report=state.get("bear_report", ""),
            conflicts=json.dumps(state.get("conflicts", []), indent=2),
        )
        + "\n\nRespond only with valid JSON.",
        temperature=0.1,
        max_tokens=900,
    )
    report = DiligenceJSON.model_validate(_parse_json_object(content)).model_dump()
    logger.info("Synthesized MoatLens report")
    return {"final_report": report}


async def _call_groq(prompt: str, temperature: float, max_tokens: int) -> str:
    client = get_groq_client()
    response = await client.chat.completions.create(
        model=settings.model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


def _parse_json_object(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"conflicts": []}
