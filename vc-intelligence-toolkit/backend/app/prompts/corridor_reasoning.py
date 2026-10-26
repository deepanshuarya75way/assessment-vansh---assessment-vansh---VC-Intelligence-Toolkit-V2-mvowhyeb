CORRIDOR_REASONING_PROMPT = """You are evaluating whether this company belongs in VC Fund's opportunity corridor.

Search query: {search_query}
Candidate: {name}
Description: {description}
Nearest portfolio match: {portfolio_match}
Similarity score: {similarity_score:.3f}

Write a concise "Why VC?" explanation in 2-3 sentences. End with exactly one confidence label on a new line:
Confidence: High
or
Confidence: Medium
or
Confidence: Low
"""
