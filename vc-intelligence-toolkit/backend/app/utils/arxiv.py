import xml.etree.ElementTree as ET

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


async def search_arxiv(query: str, limit: int = 10) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                "https://export.arxiv.org/api/query",
                params={
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": limit,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
            )
            response.raise_for_status()
            root = ET.fromstring(response.text)
    except Exception:
        logger.exception("arXiv search failed for query: %s", query)
        return []

    results = []
    for entry in root.findall("atom:entry", ATOM_NAMESPACE)[:limit]:
        title = entry.findtext("atom:title", default="", namespaces=ATOM_NAMESPACE)
        summary = entry.findtext("atom:summary", default="", namespaces=ATOM_NAMESPACE)
        published = entry.findtext("atom:published", default="", namespaces=ATOM_NAMESPACE)
        url = entry.findtext("atom:id", default="", namespaces=ATOM_NAMESPACE)
        results.append(
            {
                "title": " ".join(title.split()),
                "summary": " ".join(summary.split()),
                "url": url,
                "published": published,
            }
        )
    return results
