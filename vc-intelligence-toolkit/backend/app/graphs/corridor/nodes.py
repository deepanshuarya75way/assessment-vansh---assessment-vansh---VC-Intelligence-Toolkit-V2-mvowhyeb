import asyncio
import math
import re
from typing import Any

from sqlalchemy import select

from app.core.config import settings
from app.database.session import get_sessionmaker
from app.models.portfolio import PortfolioCompany
from app.prompts.corridor_reasoning import CORRIDOR_REASONING_PROMPT
from app.utils.arxiv import search_arxiv
from app.utils.embedding import embed_text
from app.utils.github import search_github
from app.utils.groq_client import get_groq_client
from app.utils.hn import search_hackernews
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def fetch_github_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Fetching GitHub repositories...")
    results = await search_github(state["search_query"], limit=10)
    logger.info("Found %s GitHub results", len(results))
    return {"github_results": results}


async def fetch_hn_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Fetching Hacker News stories...")
    results = await search_hackernews(state["search_query"], limit=10)
    logger.info("Found %s Hacker News results", len(results))
    return {"hn_results": results}


async def fetch_arxiv_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Fetching arXiv papers...")
    results = await search_arxiv(state["search_query"], limit=10)
    logger.info("Found %s arXiv results", len(results))
    return {"arxiv_results": results}


def merge_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Merging discovery results...")
    merged = []
    seen: set[tuple[str, str]] = set()

    for item in state.get("github_results", []):
        candidate = {
            "name": item.get("name") or "Unnamed GitHub repository",
            "description": item.get("description") or "",
            "source": "github",
            "url": item.get("url"),
        }
        _append_unique(merged, seen, candidate)

    for item in state.get("hn_results", []):
        candidate = {
            "name": item.get("title") or "Untitled Hacker News story",
            "description": _hn_description(item),
            "source": "hackernews",
            "url": item.get("url"),
        }
        _append_unique(merged, seen, candidate)

    for item in state.get("arxiv_results", []):
        candidate = {
            "name": item.get("title") or "Untitled arXiv paper",
            "description": item.get("summary") or "",
            "source": "arxiv",
            "url": item.get("url"),
        }
        _append_unique(merged, seen, candidate)

    logger.info("Merged %s candidates", len(merged))
    return {"merged_candidates": merged}


async def embedding_similarity_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Scoring candidates against portfolio embeddings...")
    portfolio_context = await _fetch_portfolio_context()
    scored = []

    for candidate in state.get("merged_candidates", []):
        description = candidate.get("description") or candidate.get("name") or ""
        if not description.strip():
            continue
        candidate_embedding = await asyncio.to_thread(embed_text, description)
        matches = _top_portfolio_matches(candidate_embedding, portfolio_context, limit=3)
        similarity_score = matches[0]["similarity"] if matches else 0.0
        scored.append(
            {
                **candidate,
                "similarity_score": similarity_score,
                "portfolio_matches": matches,
            }
        )

    scored.sort(key=lambda item: item.get("similarity_score") or 0.0, reverse=True)
    top_candidates = scored[:5]
    logger.info("Scored %s candidates; selected top %s", len(scored), len(top_candidates))
    return {
        "portfolio_context": portfolio_context,
        "candidate_scores": scored,
        "top_candidates": top_candidates,
    }


async def reasoning_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Generating Corridor reasoning with Groq...")
    client = get_groq_client()
    reasoned = []
    for candidate in state.get("top_candidates", []):
        nearest = _nearest_portfolio_label(candidate)
        prompt = CORRIDOR_REASONING_PROMPT.format(
            search_query=state["search_query"],
            name=candidate.get("name", ""),
            description=candidate.get("description", ""),
            portfolio_match=nearest,
            similarity_score=candidate.get("similarity_score") or 0.0,
        )
        response = await client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=220,
        )
        content = response.choices[0].message.content or ""
        confidence_label = _extract_confidence_label(content)
        reasoned.append(
            {
                **candidate,
                "reasoning": content.strip(),
                "confidence_label": confidence_label,
                "confidence": _confidence_score(confidence_label),
            }
        )

    logger.info("Generated reasoning for %s candidates", len(reasoned))
    return {"reasoning": reasoned}


def output_formatter_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Formatting Corridor output...")
    final_output = []
    for candidate in state.get("reasoning", []):
        final_output.append(
            {
                "company": _truncate(candidate.get("name") or "Unknown candidate", 255),
                "description": candidate.get("description") or "",
                "source": candidate.get("source"),
                "github_url": candidate.get("url"),
                "similarity_score": candidate.get("similarity_score"),
                "portfolio_matches": candidate.get("portfolio_matches") or [],
                "confidence": candidate.get("confidence"),
                "reasoning": candidate.get("reasoning"),
            }
        )
    logger.info("Formatted %s Corridor candidates", len(final_output))
    return {"final_output": final_output}


def _append_unique(
    merged: list[dict[str, Any]],
    seen: set[tuple[str, str]],
    candidate: dict[str, Any],
) -> None:
    key = ((candidate.get("source") or "").lower(), (candidate.get("url") or candidate.get("name") or "").lower())
    if key in seen:
        return
    seen.add(key)
    merged.append(candidate)


def _hn_description(item: dict[str, Any]) -> str:
    title = item.get("title") or ""
    points = item.get("points") or 0
    comments = item.get("num_comments") or 0
    return f"{title}. Hacker News story with {points} points and {comments} comments."


async def _fetch_portfolio_context() -> list[dict[str, Any]]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await session.execute(select(PortfolioCompany))
        companies = result.scalars().all()
    return [
        {
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "embedding": company.embedding,
        }
        for company in companies
        if company.embedding
    ]


def _top_portfolio_matches(
    candidate_embedding: list[float],
    portfolio_context: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    matches = []
    for company in portfolio_context:
        similarity = _cosine_similarity(candidate_embedding, company["embedding"])
        matches.append(
            {
                "id": company["id"],
                "name": company["name"],
                "description": company["description"],
                "similarity": similarity,
            }
        )
    matches.sort(key=lambda item: item["similarity"], reverse=True)
    return matches[:limit]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _nearest_portfolio_label(candidate: dict[str, Any]) -> str:
    matches = candidate.get("portfolio_matches") or []
    if not matches:
        return "No portfolio match available"
    match = matches[0]
    return f"{match.get('name')} ({match.get('description')})"


def _extract_confidence_label(text: str) -> str:
    match = re.search(r"confidence:\s*(high|medium|low)", text, re.IGNORECASE)
    if not match:
        return "Medium"
    return match.group(1).capitalize()


def _confidence_score(label: str) -> float:
    return {"High": 0.9, "Medium": 0.65, "Low": 0.35}.get(label, 0.65)


def _truncate(value: str, max_length: int) -> str:
    return value if len(value) <= max_length else value[: max_length - 3] + "..."
