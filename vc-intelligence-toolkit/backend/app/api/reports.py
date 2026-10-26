from fastapi import APIRouter, HTTPException

from app.database.session import get_sessionmaker
from app.repositories import report_repository

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{report_id}")
async def get_report(report_id: int) -> dict:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        report = await report_repository.get_by_id(session, report_id)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "candidate_id": report.candidate_id,
        "report_type": report.report_type,
        "content": report.content,
        "created_at": report.created_at,
    }
