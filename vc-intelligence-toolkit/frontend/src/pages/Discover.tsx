import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ActionButton from "@/components/ActionButton";
import LoadingReasoning from "@/components/LoadingReasoning";
import PageShell from "@/components/PageShell";
import ReportCard from "@/components/ReportCard";
import StatusPill from "@/components/StatusPill";
import StepBadge from "@/components/StepBadge";
import { discoverCandidates } from "@/services/api";
import type { Candidate } from "@/types/api";

const steps = [
  "Fetching GitHub...",
  "Reading Hacker News...",
  "Scanning arXiv...",
  "Computing similarity...",
  "Generating reasoning...",
];

const exampleQueries = ["AI infra", "agentic dev tools", "healthcare AI", "developer tools"];

export default function Discover() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("AI agent developer tools");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Candidate[]>([]);

  async function runDiscovery() {
    setLoading(true);
    setError(null);
    setResults([]);
    const started = Date.now();
    try {
      const data = await discoverCandidates(query);
      const minimum = steps.length * 400;
      const remaining = Math.max(0, minimum - (Date.now() - started));
      window.setTimeout(() => setResults(data), remaining);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Discovery failed");
    } finally {
      const minimum = steps.length * 400;
      const remaining = Math.max(0, minimum - (Date.now() - started));
      window.setTimeout(() => setLoading(false), remaining);
    }
  }

  return (
    <PageShell>
      <StepBadge number={1} label="Discover" />
      <section className="mt-8 max-w-4xl">
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">Corridor Atlas</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          Search the frontier and surface companies with meaningful proximity to
          VC's portfolio.
        </p>
      </section>

      <div className="mt-12 flex flex-col gap-4 md:flex-row">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="AI-native infrastructure..."
          className="min-h-[64px] flex-1 rounded-full border border-border bg-white px-7 font-sans text-base text-ink outline-none transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] placeholder:text-base placeholder:text-ink-secondary focus:border-ink"
        />
        <ActionButton onClick={runDiscovery} disabled={loading || !query.trim()} loading={loading}>
          Run Discovery
        </ActionButton>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {exampleQueries.map((exampleQuery) => (
          <button
            key={exampleQuery}
            type="button"
            onClick={() => setQuery(exampleQuery)}
            className="rounded-full border border-border bg-white px-3 py-1.5 text-xs font-medium text-ink-secondary transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] hover:text-ink"
          >
            {exampleQuery}
          </button>
        ))}
      </div>

      {loading ? <LoadingReasoning steps={steps} /> : null}
      {error ? <p className="mt-8 text-sm text-terracotta">{error}</p> : null}

      <section className="mt-14 grid gap-6 md:grid-cols-2">
        {results.map((candidate) => (
          <ReportCard key={candidate.id ?? candidate.company} className="min-h-[420px]">
            <div className="pr-10">
              <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                {candidate.source ?? "candidate"}
              </p>
              <h2 className="mt-4 text-[clamp(1.7rem,3vw,3rem)]">
                {candidate.company}
              </h2>
              <p className="mt-5 line-clamp-4 text-sm leading-6 text-ink-secondary">
                {candidate.description}
              </p>
              <div className="mt-6 flex flex-wrap gap-4">
                <StatusPill label={`Similarity ${formatPercent(candidate.similarity_score)}`} tone="accent" />
                <StatusPill label={`Confidence ${formatPercent(candidate.confidence)}`} />
              </div>
              {candidate.reasoning ? (
                <p className="mt-6 text-sm leading-6 text-ink">{candidate.reasoning}</p>
              ) : null}
              <div className="mt-6 space-y-2 pb-12">
                {(candidate.portfolio_matches ?? []).slice(0, 3).map((match) => (
                  <p key={match.name} className="text-xs text-ink-secondary">
                    {match.name} - {formatPercent(match.similarity)}
                  </p>
                ))}
              </div>
              {candidate.id ? (
                <ActionButton
                  className="mt-2"
                  onClick={() => navigate(`/diligence?candidate_id=${candidate.id}`)}
                >
                  Send to Diligence
                </ActionButton>
              ) : null}
            </div>
          </ReportCard>
        ))}
      </section>
    </PageShell>
  );
}

function formatPercent(value?: number | null) {
  if (typeof value !== "number") return "n/a";
  return `${Math.round(value * 100)}%`;
}
