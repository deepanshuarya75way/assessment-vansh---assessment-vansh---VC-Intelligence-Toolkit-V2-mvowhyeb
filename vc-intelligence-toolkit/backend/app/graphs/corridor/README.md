# Corridor

Corridor discovers candidate companies from external sources, scores them against the portfolio context, and stores the resulting candidate records in the database.

## Install
1. `cd backend`
2. `python -m venv .venv`
3. Activate the venv, then `pip install -r requirements.txt`
4. Set `GROQ_API_KEY`, `DATABASE_URL`, `EMBEDDING_MODEL`, and `GITHUB_TOKEN`

## Run
```bash
curl -X POST http://localhost:8000/api/corridor/discover \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"AI infrastructure startups\"}"
```

## Output
```json
[
  {
    "id": 1,
    "company": "Example Co",
    "description": "...",
    "source": "hackernews",
    "github_url": "https://github.com/example/co",
    "similarity_score": 0.91,
    "portfolio_matches": [],
    "confidence": 0.84,
    "reasoning": "...",
    "created_at": "2026-07-09T12:00:00Z"
  }
]
```