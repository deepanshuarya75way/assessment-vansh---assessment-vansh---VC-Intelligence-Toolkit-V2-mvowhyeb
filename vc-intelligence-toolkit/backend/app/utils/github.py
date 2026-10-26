import httpx

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def search_github(query: str, limit: int = 10) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                "https://api.github.com/search/repositories",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        logger.exception("GitHub search failed for query: %s", query)
        return []

    results = []
    for item in payload.get("items", [])[:limit]:
        results.append(
            {
                "name": item.get("full_name") or item.get("name"),
                "description": item.get("description") or "",
                "url": item.get("html_url"),
                "stars": item.get("stargazers_count", 0),
                "topics": item.get("topics") or [],
                "language": item.get("language"),
            }
        )
    return results
