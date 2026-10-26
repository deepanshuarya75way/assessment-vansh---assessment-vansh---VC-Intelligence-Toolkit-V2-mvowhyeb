from fastapi import APIRouter, HTTPException

from app.database.session import get_sessionmaker
from app.repositories import candidate_repository, report_repository

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("")
async def get_candidates() -> list[dict]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        candidates = await candidate_repository.list_all(session)

    return [
        {
            "id": candidate.id,
            "company": candidate.company,
            "description": candidate.description,
            "source": candidate.source,
            "github_url": candidate.github_url,
            "similarity_score": candidate.similarity_score,
            "portfolio_matches": candidate.portfolio_matches,
            "confidence": candidate.confidence,
            "reasoning": candidate.reasoning,
            "created_at": candidate.created_at,
        }
        for candidate in candidates
    ]


@router.get("/{candidate_id}/reports")
async def get_candidate_reports(candidate_id: int) -> list[dict]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        candidate = await candidate_repository.get_by_id(session, candidate_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")

        reports = await report_repository.get_by_candidate_id(session, candidate_id)

    return [
        {
            "id": report.id,
            "candidate_id": report.candidate_id,
            "report_type": report.report_type,
            "content": report.content,
            "created_at": report.created_at,
        }
        for report in reports
    ]