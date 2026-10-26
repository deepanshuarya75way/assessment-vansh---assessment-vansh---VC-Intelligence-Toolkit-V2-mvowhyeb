from pydantic import BaseModel


class DiligenceJSON(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    wrapper_risk: str
    data_moat: str
    model_dependency: str
    overall_score: float
    confidence: float
    human_review_required: bool
    missing_evidence: str
