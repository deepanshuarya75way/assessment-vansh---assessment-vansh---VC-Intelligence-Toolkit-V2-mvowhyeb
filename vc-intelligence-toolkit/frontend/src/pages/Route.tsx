import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useSearchParams } from "react-router-dom";
import ActionButton from "@/components/ActionButton";
import LoadingReasoning from "@/components/LoadingReasoning";
import PageShell from "@/components/PageShell";
import StatusPill from "@/components/StatusPill";
import StepBadge from "@/components/StepBadge";
import { getCandidateReports, getCandidates, routeCandidate } from "@/services/api";
import type { Candidate, Recommendation, ReportRecord } from "@/types/api";

const steps = [
  "Parsing application...",
  "Retrieving program context...",
  "Evaluating pathway fit...",
  "Deriving confidence...",
  "Generating interview questions...",
];

const sampleText =
  "Founder: Mira Patel. We are building an AI coding agent platform for enterprise engineering teams with design partners, strong GitHub activity, and early evidence of reduced maintenance work.";

type RouteLocationState = {
  candidate_id?: string | number;
};

export default function RoutePage() {
  const [params] = useSearchParams();
  const location = useLocation();
  const locationState = location.state as RouteLocationState | null;
  const initialCandidateId =
    params.get("candidate_id") ?? (locationState?.candidate_id ? String(locationState.candidate_id) : "");
  const [candidateId, setCandidateId] = useState(initialCandidateId);
  const [applicationText, setApplicationText] = useState(() => (initialCandidateId ? "" : sampleText));
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const applicationTextEdited = useRef(false);
  const parsedId = useMemo(() => Number(candidateId), [candidateId]);

  useEffect(() => {
    if (!candidateId.trim() || !parsedId) return;

    let cancelled = false;

    async function loadCandidateContext() {
      applicationTextEdited.current = false;

      try {
        const [candidatesResult, reportsResult] = await Promise.allSettled([
          getCandidates(),
          getCandidateReports(parsedId),
        ]);

        if (cancelled) return;

        const candidate =
          candidatesResult.status === "fulfilled"
            ? candidatesResult.value.find((item) => item.id === parsedId) ?? null
            : null;
        const reports = reportsResult.status === "fulfilled" ? reportsResult.value : [];
        const nextValue = buildApplicationText(candidate, reports);

        if (!applicationTextEdited.current && nextValue) {
          setApplicationText(nextValue);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load candidate context");
        }
      }
    }

    loadCandidateContext();

    return () => {
      cancelled = true;
    };
  }, [candidateId, parsedId]);

  async function runRouting() {
    if (!parsedId || !applicationText.trim()) return;
    setLoading(true);
    setError(null);
    setRecommendation(null);
    const started = Date.now();
    try {
      const data = await routeCandidate(parsedId, applicationText);
      const minimum = steps.length * 400;
      const remaining = Math.max(0, minimum - (Date.now() - started));
      window.setTimeout(() => setRecommendation(data), remaining);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Routing failed");
    } finally {
      const minimum = steps.length * 400;
      const remaining = Math.max(0, minimum - (Date.now() - started));
      window.setTimeout(() => setLoading(false), remaining);
    }
  }

  return (
    <PageShell>
      <StepBadge number={3} label="Route" />
      <section className="mt-8 max-w-4xl">
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">Navigator</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          Route a founder toward the SwarmSpace pathway that matches readiness,
          technical signal, and evidence quality.
        </p>
      </section>

      <div className="mt-12 grid gap-4">
        <input
          value={candidateId}
          onChange={(event) => setCandidateId(event.target.value)}
          placeholder="Candidate ID"
          className="min-h-[64px] w-full rounded-full border border-border bg-white px-7 font-sans text-base text-ink outline-none transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] placeholder:text-base placeholder:text-ink-secondary focus:border-ink md:max-w-sm"
        />
        <textarea
          value={applicationText}
          onChange={(event) => {
            applicationTextEdited.current = true;
            setApplicationText(event.target.value);
          }}
          className="min-h-[220px] rounded-xl border border-border bg-white p-6 font-sans text-base leading-7 text-ink outline-none transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] placeholder:text-base placeholder:text-ink-secondary focus:border-ink"
          placeholder="Paste or edit the candidate context here..."
        />
        <ActionButton
          onClick={runRouting}
          disabled={loading || !parsedId || !applicationText.trim()}
          loading={loading}
        >
          Get Recommendation
        </ActionButton>
      </div>

      {loading ? <LoadingReasoning steps={steps} /> : null}
      {error ? <p className="mt-8 text-sm text-terracotta">{error}</p> : null}

      {recommendation ? (
        <section className="mt-14 rounded-xl border border-border bg-white p-8">
          <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
            Recommended pathway
          </p>
          <h2 className="mt-4 text-[clamp(3rem,7vw,7rem)]">
            {recommendation.recommended_pathway}
          </h2>
          <div className="mt-6 flex flex-wrap gap-5">
            <StatusPill label={`Confidence ${formatPercent(recommendation.confidence)}`} tone="accent" />
            <StatusPill
              label={recommendation.human_review ? "Human review" : "Autonomous route"}
              tone={recommendation.human_review ? "accent" : "dark"}
            />
          </div>
          <p className="mt-8 max-w-3xl text-base leading-7 text-ink-secondary">
            {recommendation.reasoning}
          </p>
          <ol className="mt-10 max-w-3xl space-y-4">
            {recommendation.interview_questions.map((question, index) => (
              <li key={question} className="grid grid-cols-[32px_1fr] gap-4 text-sm leading-6">
                <span className="font-medium text-ink">{index + 1}</span>
                <span className="text-ink-secondary">{question}</span>
              </li>
            ))}
          </ol>
        </section>
      ) : null}
    </PageShell>
  );
}

function formatPercent(value?: number | null) {
  if (typeof value !== "number") return "n/a";
  return `${Math.round(value * 100)}%`;
}

function buildApplicationText(candidate: Candidate | null, reports: ReportRecord[]) {
  const parts: string[] = [];

  if (candidate?.company) {
    parts.push(`Company: ${candidate.company}`);
  }

  if (candidate?.description) {
    parts.push(`Description: ${candidate.description}`);
  }

  const reasoning = candidate?.reasoning ?? extractReportReasoning(reports);
  if (reasoning) {
    parts.push(`Reasoning: ${reasoning}`);
  }

  return parts.join("\n\n");
}

function extractReportReasoning(reports: ReportRecord[]) {
  const diligenceReport = reports.find((report) => report.report_type === "diligence");
  if (!diligenceReport) return "";

  if (typeof diligenceReport.content === "string") {
    return diligenceReport.content;
  }

  if (diligenceReport.content && typeof diligenceReport.content === "object") {
    return JSON.stringify(diligenceReport.content, null, 2);
  }

  return "";
}
