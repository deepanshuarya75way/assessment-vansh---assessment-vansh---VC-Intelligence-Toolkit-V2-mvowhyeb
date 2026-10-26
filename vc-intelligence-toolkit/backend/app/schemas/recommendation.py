from pydantic import BaseModel


class RecommendationJSON(BaseModel):
    recommended_pathway: str
    confidence: float
    interview_questions: list[str]
    reasoning: str
    human_review: bool
