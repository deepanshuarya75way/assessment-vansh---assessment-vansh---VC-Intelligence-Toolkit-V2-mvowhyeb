from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.services.corridor_service import run_corridor_discovery

router = APIRouter(prefix="/api/corridor", tags=["corridor"])


class CorridorDiscoverRequest(BaseModel):
    query: str = Field(..., min_length=1)


@router.post("/discover")
async def discover_corridor(request: CorridorDiscoverRequest) -> list[dict]:
    return await run_corridor_discovery(request.query)
