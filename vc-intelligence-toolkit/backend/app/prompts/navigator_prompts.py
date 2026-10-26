SWARMSPACE_PROGRAMS = [
    {
        "name": "Investment",
        "description": "$1M-$10M checks, Seed/Series A, strong traction and defensible AI moat required",
    },
    {
        "name": "AI Studio",
        "description": "12-week cohort, up to $1M, for early/pre-product teams with strong technical signal in foundational models, agents, embodied systems, edge computing, AI infra, or AI+hard sciences",
    },
    {
        "name": "Research Lab",
        "description": "Frontier research on real-world problems, for teams stronger on research depth than commercial traction",
    },
    {
        "name": "Community",
        "description": "Founder salons, demo days, mentorship — for early-stage or exploratory founders not yet ready for formal programs",
    },
    {
        "name": "Monitor",
        "description": "Promising but too early or missing key evidence — revisit in 3-6 months",
    },
]

APPLICATION_PARSING_PROMPT = """Extract structured fields from this SwarmSpace application.

Application:
{application_text}

Return only JSON:
{{
  "founder_name": "...",
  "description": "...",
  "stage": "...",
  "traction_summary": "...",
  "github_url": "..."
}}
Use "unknown" for missing fields.
"""

ROUTING_PROMPT = """Route this candidate to the best SwarmSpace pathway.

Candidate:
{candidate}

Diligence:
{diligence}

Application:
{application}

Retrieved program context:
{retrieved_context}

Score all five pathways from 0 to 1 and pick the best one. Consider traction, AI moat, technical signal, research depth, evidence quality, and readiness.

Return only JSON:
{{
  "scores": {{
    "Investment": 0.0,
    "AI Studio": 0.0,
    "Research Lab": 0.0,
    "Community": 0.0,
    "Monitor": 0.0
  }},
  "recommended_pathway": "...",
  "reasoning": "concise rationale",
  "weakest_evidence_areas": ["..."]
}}
"""

INTERVIEW_QUESTIONS_PROMPT = """Generate 3-5 targeted interview questions for this SwarmSpace routing decision.

Candidate:
{candidate}

Diligence:
{diligence}

Application:
{application}

Routing evaluation:
{evaluation}

Focus on weakest evidence areas, program fit, moat, traction, and technical depth.
Return only JSON:
{{"interview_questions": ["..."]}}
"""
