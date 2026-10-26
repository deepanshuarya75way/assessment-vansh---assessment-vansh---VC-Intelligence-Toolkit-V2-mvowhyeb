import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import ActionButton from "@/components/ActionButton";
import LoadingReasoning from "@/components/LoadingReasoning";
import PageShell from "@/components/PageShell";
import StatusPill from "@/components/StatusPill";
import StepBadge from "@/components/StepBadge";
import { evaluateDiligence } from "@/services/api";
import type { DiligenceReport } from "@/types/api";

const steps = [
  "Extracting claims...",
  "Running Bull Agent...",
  "Running Bear Agent...",
  "Checking conflicts...",
  "Synthesizing...",
];

export default function Diligence() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [candidateId, setCandidateId] = useState(params.get("candidate_id") ?? "");
  const [report, setReport] = useState<DiligenceReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parsedId = useMemo(() => Number(candidateId), [candidateId]);

  async function runDiligence() {
    if (!parsedId) return;
    setLoading(true);
    setError(null);
    setReport(null);
    const started = Date.now();
    try {
      const data = await evaluateDiligence(parsedId);
      const minimum = steps.length * 400;
      const remaining = Math.max(0, minimum - (Date.now() - started));
      window.setTimeout(() => setReport(data), remaining);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Diligence failed");
    } finally {
      const minimum = steps.length * 400;
      const remaining = Math.max(0, minimum - (Date.now() - started));
      window.setTimeout(() => setLoading(false), remaining);
    }
  }

  return (
    <PageShell>
      <StepBadge number={2} label="Evaluate" />
      <section className="mt-8 max-w-4xl">
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">MoatLens</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          Pressure-test AI-native defensibility through paired upside and risk
          arguments.
        </p>
      </section>

      <div className="mt-12 flex flex-col gap-4 md:flex-row">
        <input
          value={candidateId}
          onChange={(event) => setCandidateId(event.target.value)}
          placeholder="Candidate ID"
          className="min-h-[64px] w-full rounded-full border border-border bg-white px-7 font-sans text-base text-ink outline-none transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] placeholder:text-base placeholder:text-ink-secondary focus:border-ink md:max-w-sm"
        />
        <ActionButton onClick={runDiligence} disabled={loading || !parsedId} loading={loading}>
          Run Diligence
        </ActionButton>
      </div>

      {loading ? <LoadingReasoning steps={steps} /> : null}
      {error ? <p className="mt-8 text-sm text-terracotta">{error}</p> : null}

      {report ? (
        <section className="mt-14 space-y-8">
          <div className="rounded-xl border border-border bg-white p-6">
            <div className="flex flex-wrap gap-5">
              <StatusPill label={`Overall ${report.overall_score.toFixed(2)}`} tone="accent" />
              <StatusPill label={`Confidence ${formatPercent(report.confidence)}`} />
              <StatusPill
                label={report.human_review_required ? "Human review required" : "No human review"}
                tone={report.human_review_required ? "accent" : "dark"}
              />
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <QuietList title="Strengths" items={report.strengths} />
            <QuietList title="Weaknesses" items={report.weaknesses} />
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <TextBlock title="Wrapper risk" text={report.wrapper_risk} />
            <TextBlock title="Data moat" text={report.data_moat} />
            <TextBlock title="Model dependency" text={report.model_dependency} />
          </div>

          <div className="rounded-xl border border-terracotta bg-white p-6">
            <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
              Missing evidence
            </p>
            <p className="mt-3 text-ink">{report.missing_evidence}</p>
          </div>

          <ActionButton onClick={() => navigate(`/route?candidate_id=${parsedId}`)}>
            Send to Navigator
          </ActionButton>
        </section>
      ) : null}
    </PageShell>
  );
}

function QuietList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl border border-border bg-white p-6">
      <h2 className="text-[clamp(1.8rem,3vw,3rem)]">{title}</h2>
      <ul className="mt-6 space-y-3">
        {items.map((item) => (
          <li key={item} className="text-sm leading-6 text-ink-secondary">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function TextBlock({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-xl border border-border bg-white p-6">
      <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
        {title}
      </p>
      <p className="mt-4 text-sm leading-6 text-ink">{text}</p>
    </div>
  );
}

function formatPercent(value?: number | null) {
  if (typeof value !== "number") return "n/a";
  return `${Math.round(value * 100)}%`;
}
