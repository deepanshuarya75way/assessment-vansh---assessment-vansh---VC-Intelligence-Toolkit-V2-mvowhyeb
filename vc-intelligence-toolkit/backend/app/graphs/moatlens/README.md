# MoatLens

MoatLens evaluates a saved candidate, synthesizes a diligence report, and writes that report back to the database for later routing.

## Install
1. `cd backend`
2. `python -m venv .venv`
3. Activate the venv, then `pip install -r requirements.txt`
4. Set `GROQ_API_KEY`, `DATABASE_URL`, and `EMBEDDING_MODEL`

## Run
```bash
curl -X POST http://localhost:8000/api/moatlens/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"candidate_id\":1}"
```

## Output
```json
{
  "strengths": ["..."],
  "weaknesses": ["..."],
  "wrapper_risk": "...",
  "data_moat": "...",
  "model_dependency": "...",
  "overall_score": 0.78,
  "confidence": 0.81,
  "human_review_required": false,
  "missing_evidence": "..."
}
```