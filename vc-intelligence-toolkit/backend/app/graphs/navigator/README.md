# Navigator

Navigator turns an evaluated candidate plus its latest diligence report into a routing recommendation and saves the recommendation to the database.

## Install
1. `cd backend`
2. `python -m venv .venv`
3. Activate the venv, then `pip install -r requirements.txt`
4. Set `GROQ_API_KEY`, `DATABASE_URL`, and `EMBEDDING_MODEL`

## Run
```bash
curl -X POST http://localhost:8000/api/navigator/route \
  -H "Content-Type: application/json" \
  -d "{\"candidate_id\":1,\"application_text\":\"Ship a concise application review.\"}"
```

## Output
```json
{
  "recommended_pathway": "Advance",
  "confidence": 0.86,
  "interview_questions": ["..."],
  "reasoning": "...",
  "human_review": false
}
```