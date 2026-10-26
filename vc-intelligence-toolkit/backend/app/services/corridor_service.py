from datetime import datetime

from app.database.session import get_sessionmaker
from app.graphs.corridor.graph import corridor_graph
from app.repositories import candidate_repository, run_repository
from app.schemas.candidate import CandidateCreate, CandidateOut
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def run_corridor_discovery(search_query: str) -> list[dict]:
    logger.info("Starting Corridor discovery for query: %s", search_query)
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        run = await run_repository.create(session, module_name="corridor", status="running")

    try:
        state = await corridor_graph.ainvoke({"search_query": search_query})
        final_output = state.get("final_output", [])

        saved_candidates = []
        async with sessionmaker() as session:
            for candidate in final_output:
                saved = await candidate_repository.create(
                    session,
                    CandidateCreate(**candidate),
                )
                saved_candidates.append(CandidateOut.model_validate(saved).model_dump())
            await run_repository.update_status(
                session,
                run_id=run.id,
                status="completed",
                completed_at=datetime.utcnow(),
            )

        logger.info(
            "Corridor discovery completed with %s saved candidates",
            len(saved_candidates),
        )
        return saved_candidates
    except Exception:
        async with sessionmaker() as session:
            await run_repository.update_status(
                session,
                run_id=run.id,
                status="failed",
                completed_at=datetime.utcnow(),
            )
        logger.exception("Corridor discovery failed")
        raise
