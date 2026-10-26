from datetime import datetime

from app.database.session import get_sessionmaker
from app.graphs.moatlens.graph import moatlens_graph
from app.models.report import ReportType
from app.repositories import candidate_repository, report_repository, run_repository
from app.schemas.candidate import CandidateOut
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def run_moatlens_evaluation(candidate_id: int) -> dict:
    logger.info("Starting MoatLens evaluation for candidate %s", candidate_id)
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        candidate = await candidate_repository.get_by_id(session, candidate_id)
        if candidate is None:
            raise ValueError(f"Candidate {candidate_id} not found.")
        candidate_payload = CandidateOut.model_validate(candidate).model_dump()
        run = await run_repository.create(session, module_name="moatlens", status="running")

    try:
        state = await moatlens_graph.ainvoke(
            {"candidate": candidate_payload, "retry_count": 0}
        )
        final_report = state["final_report"]

        async with sessionmaker() as session:
            await report_repository.create(
                session,
                candidate_id=candidate_id,
                report_type=ReportType.diligence,
                content=final_report,
            )
            await run_repository.update_status(
                session,
                run_id=run.id,
                status="completed",
                completed_at=datetime.utcnow(),
            )

        logger.info("MoatLens evaluation completed for candidate %s", candidate_id)
        return final_report
    except Exception:
        async with sessionmaker() as session:
            await run_repository.update_status(
                session,
                run_id=run.id,
                status="failed",
                completed_at=datetime.utcnow(),
            )
        logger.exception("MoatLens evaluation failed")
        raise
