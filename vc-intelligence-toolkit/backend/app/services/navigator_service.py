from datetime import datetime

from sqlalchemy import select

from app.database.session import get_sessionmaker
from app.graphs.navigator.graph import navigator_graph
from app.models.report import Report, ReportType
from app.repositories import candidate_repository, report_repository, run_repository
from app.schemas.candidate import CandidateOut
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def run_navigator_routing(candidate_id: int, application_text: str) -> dict:
    logger.info("Starting SwarmSpace Navigator routing for candidate %s", candidate_id)
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        candidate = await candidate_repository.get_by_id(session, candidate_id)
        if candidate is None:
            raise ValueError(f"Candidate {candidate_id} not found.")
        diligence = await _get_latest_diligence_report(session, candidate_id)
        if diligence is None:
            raise ValueError(f"No diligence report found for candidate {candidate_id}.")
        candidate_payload = CandidateOut.model_validate(candidate).model_dump()
        run = await run_repository.create(session, module_name="navigator", status="running")

    try:
        state = await navigator_graph.ainvoke(
            {
                "candidate": candidate_payload,
                "diligence": diligence,
                "application": application_text,
            }
        )
        recommendation = state["recommendation"]

        async with sessionmaker() as session:
            await report_repository.create(
                session,
                candidate_id=candidate_id,
                report_type=ReportType.recommendation,
                content=recommendation,
            )
            await run_repository.update_status(
                session,
                run_id=run.id,
                status="completed",
                completed_at=datetime.utcnow(),
            )

        logger.info("Navigator routing completed for candidate %s", candidate_id)
        return recommendation
    except Exception:
        async with sessionmaker() as session:
            await run_repository.update_status(
                session,
                run_id=run.id,
                status="failed",
                completed_at=datetime.utcnow(),
            )
        logger.exception("Navigator routing failed")
        raise


async def _get_latest_diligence_report(session, candidate_id: int) -> dict | None:
    result = await session.execute(
        select(Report)
        .where(
            Report.candidate_id == candidate_id,
            Report.report_type == ReportType.diligence,
        )
        .order_by(Report.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    return report.content if report is not None else None
