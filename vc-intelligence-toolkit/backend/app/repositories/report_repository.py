from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportType


async def create(
    db: AsyncSession,
    candidate_id: int,
    report_type: ReportType,
    content: dict[str, Any],
) -> Report:
    report = Report(
        candidate_id=candidate_id,
        report_type=report_type,
        content=content,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_by_id(db: AsyncSession, report_id: int) -> Report | None:
    return await db.get(Report, report_id)


async def get_by_candidate_id(db: AsyncSession, candidate_id: int) -> list[Report]:
    result = await db.execute(
        select(Report)
        .where(Report.candidate_id == candidate_id)
        .order_by(Report.created_at.desc())
    )
    return list(result.scalars().all())
