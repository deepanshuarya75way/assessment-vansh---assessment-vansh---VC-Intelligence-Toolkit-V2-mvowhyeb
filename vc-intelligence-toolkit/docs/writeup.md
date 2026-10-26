# VC Intelligence Toolkit — Technical Writeup
### One writeup per tool: architecture choices, what worked, what I'd improve, what I'd need from the firm for production.

---

## Corridor Atlas

**Architecture choices**

Corridor Atlas is a LangGraph pipeline with a parallel fan-out at the start: three independent nodes (`fetch_github_node`, `fetch_hn_node`, `fetch_arxiv_node`) call the GitHub REST API, the HN Algolia API, and the arXiv API concurrently, since none of these calls depend on each other. Their outputs merge into a single normalized shape in `merge_node`. From there, `embedding_similarity_node` embeds every candidate's description using `sentence-transformers` (`all-MiniLM-L6-v2`, chosen for being free, local, and fast enough not to need a paid embedding API) and compares each one against VC's own portfolio embeddings, stored as pgvector columns directly in the Supabase database rather than a separate vector store. This avoids running two databases for one project. The top candidates by similarity go to `reasoning_node`, which calls Groq to generate a short "Why VC?" explanation citing the nearest portfolio match, plus a confidence level. `output_formatter_node` shapes everything into the `CandidateOut` schema and the service layer persists it as a `Candidate` row along with a `Run` record for tracking.

The core design decision was using VC's real portfolio as the thesis reference instead of a generic keyword filter. This is the one piece of the toolkit that structurally cannot work without VC's actual data, which was intentional.

**What worked**

The parallel fetch genuinely cuts latency versus a sequential version, and it's a clean demonstration of LangGraph doing more than a linear chain. The similarity-plus-reasoning combination also produced results that were more legible than raw scores alone. A partner reading "this resembles Composio because of X" gets more value than "similarity: 0.71."

**What I'd improve with more time**

The portfolio reference set is small, around 30 companies, which means matches can lean on surface-level keyword overlap rather than deeper thesis alignment. I'd want a larger, richer reference set, ideally including reasons *why* each portfolio company was a fit, not just its description, so the embedding captures investment logic rather than just product category. I'd also add the "contrarian slice" I described in the ideation doc: a small set of results deliberately chosen for low similarity but strong independent signal, to counteract the echo chamber effect that similarity-based sourcing tends to produce.

**What I'd need from the firm for production**

Real deal history beyond the public portfolio (why each investment was made, not just what the company does) would meaningfully improve the reasoning quality. I'd also want a GitHub token with higher rate limits for continuous background scanning rather than on-demand queries, and ideally a scheduling layer so this runs daily rather than only when triggered manually.

---

## AI MoatLens

**Architecture choices**

MoatLens is built as a multi-agent debate inside a single LangGraph. `claim_extraction_node` pulls structured facts out of a candidate's available information (product, customers, AI usage, proprietary assets) using Groq with JSON mode enforced. Two nodes then run in parallel off that same extracted data: `bull_agent_node`, arguing the investment case, and `bear_agent_node`, arguing the risk case with an AI-native lens (wrapper risk, model dependency, data moat, defensibility). Both feed into `conflict_checker_node`, which compares the two outputs for direct contradictions or claims unsupported by the extracted facts. A conditional edge checks whether conflicts were found and whether a retry hasn't already happened. If both are true, the graph loops back to regenerate Bull and Bear once before proceeding; otherwise it moves to `synthesis_node`, which produces the final `DiligenceJSON` with per-category risk notes, an overall score, a confidence value, and explicit `missing_evidence` and `human_review_required` fields.

The reflection loop was the deliberate centerpiece here. Rather than trusting two independently generated arguments, the system checks whether they actually hold together before finalizing anything.

**What worked**

The reflection loop is not just theoretical. In a real run, the conflict checker found five actual conflicts, triggered a regeneration of both agents, and then proceeded to synthesis at the retry cap, exactly as designed. Extracting claims into a shared structure before running Bull and Bear also kept both arguments grounded in the same facts instead of drifting into unrelated points.

**What I'd improve with more time**

Right now the retry cap is fixed at one. I'd want to make that adaptive, retrying more when conflicts are severe and stopping earlier when they're minor. I'd also add a lightweight grounding check that verifies specific factual claims (like a stated funding amount) against the original source text, rather than relying on the LLM's own consistency judgment alone.

**What I'd need from the firm for production**

Access to real data rooms and founder-provided materials rather than public descriptions would make the extracted claims meaningfully richer, which is the biggest lever on output quality here. I'd also want partner feedback on a batch of real outputs to calibrate what "high confidence" should actually mean in VC's own risk tolerance, since right now that threshold is my own judgment call rather than a calibrated one.

---

## SwarmSpace Navigator

**Architecture choices**

Navigator is the most retrieval-heavy of the three tools. `application_parsing_node` extracts structured fields from a raw application (founder name, description, stage, traction, links) using Groq when the input is unstructured text. `retrieve_context_node` is the RAG step: descriptions of all five SwarmSpace pathways (Investment, AI Studio, Research Lab, Community, Monitor) are embedded once, and the application is compared against them to retrieve the most relevant pathway context, grounded in SwarmSpace's own stated focus areas rather than a generic rubric. `evaluate_fit_node` scores the application across all five pathways using the candidate's data, any prior MoatLens diligence, the application itself, and the retrieved context together. `confidence_node` derives a confidence value from those scores, `interview_question_node` generates three to five questions specifically targeting the weakest evidence found upstream, and `formatter_node` produces the final `RecommendationJSON`.

The key architectural decision was pulling in MoatLens's diligence output as an input here rather than treating Navigator as isolated. Routing should reflect what's already been learned about a candidate, not re-derive everything from zero.

**What worked**

In a live run against a real discovered candidate, Navigator correctly pulled in the prior MoatLens report and generated interview questions that directly targeted gaps MoatLens had already flagged, like unclear customer traction and unproven technical defensibility, rather than generic questions. That connection between modules is the part of the toolkit I'm most confident actually reflects VC's real workflow rather than three disconnected demos glued together.

**What I'd improve with more time**

The pathway descriptions used for retrieval are currently static text I wrote based on public SwarmSpace information. I'd want these maintained by the firm directly, and ideally versioned, so the routing logic stays current as SwarmSpace's actual criteria evolve. I'd also add the identity-resolution layer described in the ideation doc as a future step, so a founder who first shows up through Corridor Atlas and later applies to SwarmSpace is recognized as the same person rather than creating a disconnected second profile.

**What I'd need from the firm for production**

Real, internally-maintained descriptions of what each pathway is currently looking for, since program criteria shift over time in ways public pages don't always reflect. I'd also want visibility into which past routing decisions turned out right or wrong, so the scoring logic could be tuned against real outcomes instead of my own first-pass judgment.
