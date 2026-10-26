from fastapi import APIRouter

from app.database.session import get_sessionmaker
from app.repositories import run_repository

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def get_history() -> list[dict]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        runs = await run_repository.list_all(session)

    return [
        {
            "id": run.id,
            "module": run.module_name,
            "status": run.status,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
        }
        for run in runs
    ]
