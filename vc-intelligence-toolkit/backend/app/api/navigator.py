from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.navigator_service import run_navigator_routing

router = APIRouter(prefix="/api/navigator", tags=["navigator"])


class NavigatorRouteRequest(BaseModel):
    candidate_id: int = Field(..., ge=1)
    application_text: str = Field(..., min_length=1)


@router.post("/route")
async def route_navigator(request: NavigatorRouteRequest) -> dict:
    return await run_navigator_routing(request.candidate_id, request.application_text)
