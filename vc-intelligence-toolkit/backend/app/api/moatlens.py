from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.moatlens_service import run_moatlens_evaluation

router = APIRouter(prefix="/api/moatlens", tags=["moatlens"])


class MoatlensEvaluateRequest(BaseModel):
    candidate_id: int = Field(..., ge=1)


@router.post("/evaluate")
async def evaluate_moatlens(request: MoatlensEvaluateRequest) -> dict:
    return await run_moatlens_evaluation(request.candidate_id)
