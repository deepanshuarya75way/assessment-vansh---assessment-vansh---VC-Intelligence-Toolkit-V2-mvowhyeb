import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


async def search_hackernews(query: str, limit: int = 10) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                "https://hn.algolia.com/api/v1/search",
                params={"query": query, "tags": "story", "hitsPerPage": limit},
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        logger.exception("Hacker News search failed for query: %s", query)
        return []

    results = []
    for item in payload.get("hits", [])[:limit]:
        results.append(
            {
                "title": item.get("title") or item.get("story_title") or "",
                "url": item.get("url") or item.get("story_url"),
                "points": item.get("points") or 0,
                "num_comments": item.get("num_comments") or 0,
                "created_at": item.get("created_at"),
            }
        )
    return results
