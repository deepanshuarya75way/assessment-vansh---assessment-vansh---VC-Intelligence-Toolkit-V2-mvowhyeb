CLAIM_EXTRACTION_PROMPT = """Extract structured diligence claims from this candidate.

Candidate input:
{candidate_text}

Return only compact JSON with keys:
company, product, customers, ai_usage, proprietary_assets
Use strings or arrays. If unknown, use "unknown".
"""

BULL_AGENT_PROMPT = """You are the Bull Agent for an AI-native diligence review.

Extracted claims:
{extracted_claims}

Argue the investment upside. Explicitly address:
- wrapper risk
- model dependency
- proprietary data
- technical defensibility
- long-term moat

Return concise prose with evidence-based claims only.
"""

BEAR_AGENT_PROMPT = """You are the Bear Agent for an AI-native diligence review.

Extracted claims:
{extracted_claims}

Argue the risks. Explicitly address:
- wrapper risk
- model dependency
- proprietary data gaps
- technical defensibility gaps
- long-term moat or commodity risk

Return concise prose with evidence-based claims only.
"""

CONFLICT_CHECKER_PROMPT = """Compare the Bull and Bear reports for direct contradictions or unsupported claims.

Bull report:
{bull_report}

Bear report:
{bear_report}

Return only JSON:
{{"conflicts": ["..."]}}
Use an empty list when there are no material conflicts.
"""

SYNTHESIS_PROMPT = """Synthesize a final AI-native diligence report from the inputs.

Extracted claims:
{extracted_claims}

Bull report:
{bull_report}

Bear report:
{bear_report}

Conflicts:
{conflicts}

Return only valid JSON matching this schema:
{{
  "strengths": ["..."],
  "weaknesses": ["..."],
  "wrapper_risk": "Low|Medium|High plus short rationale",
  "data_moat": "short assessment",
  "model_dependency": "short assessment",
  "overall_score": 0.0,
  "confidence": 0.0,
  "human_review_required": true,
  "missing_evidence": "short description"
}}

Scores must be numbers from 0 to 1.
"""
