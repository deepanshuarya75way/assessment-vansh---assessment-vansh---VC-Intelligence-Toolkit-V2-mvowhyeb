import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import PageShell from "@/components/PageShell";
import ReportCard from "@/components/ReportCard";
import StatusPill from "@/components/StatusPill";
import { getCandidateReports, getCandidates } from "@/services/api";
import type { Candidate, DiligenceReport, Recommendation, ReportRecord } from "@/types/api";

export default function CandidateDetail() {
  const { id } = useParams();
  const candidateId = Number(id);
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [candidateError, setCandidateError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || Number.isNaN(candidateId)) {
      setError("Invalid candidate id");
      setLoading(false);
      return;
    }

    let cancelled = false;

    setLoading(true);
    setError(null);
    setCandidateError(null);

    getCandidateReports(candidateId)
      .then((data) => {
        if (!cancelled) {
          setReports(data);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    getCandidates()
      .then((data) => {
        if (!cancelled) {
          setCandidate(data.find((item) => item.id === candidateId) ?? null);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setCandidateError(err.message);
          setCandidate(null);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [candidateId, id]);

  const diligenceReport = reports.find((report) => report.report_type === "diligence");
  const recommendationReport = reports.find(
    (report) => report.report_type === "recommendation",
  );
  const diligenceContent = parseDiligenceReport(diligenceReport?.content);
  const recommendationContent = parseRecommendationReport(recommendationReport?.content);

  return (
    <PageShell>
      <section className="max-w-4xl">
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">Candidate Detail</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          Review the current diligence and routing output for this candidate.
        </p>
      </section>

      {loading ? <p className="mt-8 text-sm text-ink-secondary">Loading candidate reports...</p> : null}
      {error ? <p className="mt-8 text-sm text-terracotta">{error}</p> : null}
      {candidateError ? <p className="mt-4 text-sm text-terracotta">{candidateError}</p> : null}

      {!loading && !error ? (
        <section className="mt-14 space-y-8">
          {candidate ? (
            <div className="rounded-xl border border-border bg-white p-6">
              <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                Candidate
              </p>
              <h2 className="mt-4 text-[clamp(1.8rem,3vw,3rem)]">{candidate.company}</h2>
              <p className="mt-5 text-base leading-7 text-ink-secondary">
                {candidate.description}
              </p>
              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <InfoBlock label="Similarity score" value={formatPercent(candidate.similarity_score)} />
                <InfoBlock label="Confidence" value={formatPercent(candidate.confidence)} />
              </div>
            </div>
          ) : null}

          {diligenceReport ? (
            <ReportCard className="min-h-[240px]">
              <div className="pr-12">
                <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                  diligence
                </p>
                <h2 className="mt-4 text-[clamp(1.8rem,3vw,3rem)]">Diligence Report</h2>

                {diligenceContent ? (
                  <div className="mt-8 space-y-8">
                    {diligenceContent.human_review_required ? (
                      <div className="flex flex-col gap-3 rounded-xl border border-terracotta bg-cream p-5 md:flex-row md:items-center md:justify-between">
                        <div className="flex items-start gap-3">
                          <span className="mt-0.5 grid h-8 w-8 place-items-center rounded-full border border-terracotta text-terracotta">
                            <AlertTriangle className="h-4 w-4" />
                          </span>
                          <div>
                            <p className="text-base font-medium text-ink">Human Review Required</p>
                            <p className="mt-1 text-sm leading-6 text-ink-secondary">
                              This diligence report needs a manual review before routing decisions are finalized.
                            </p>
                          </div>
                        </div>
                        <StatusPill label="Human review required" tone="accent" />
                      </div>
                    ) : null}

                    <div className="grid gap-4 md:grid-cols-2">
                      <InfoBlock label="Wrapper risk" value={diligenceContent.wrapper_risk} />
                      <InfoBlock label="Data moat" value={diligenceContent.data_moat} />
                      <InfoBlock label="Model dependency" value={diligenceContent.model_dependency} />
                      <InfoBlock label="Overall score" value={formatPercent(diligenceContent.overall_score)} />
                      <InfoBlock label="Confidence" value={formatPercent(diligenceContent.confidence)} />
                    </div>

                    <div className="grid gap-6 lg:grid-cols-2">
                      <ListPanel
                        title="Strengths"
                        items={diligenceContent.strengths}
                        iconTone="positive"
                      />
                      <ListPanel
                        title="Weaknesses"
                        items={diligenceContent.weaknesses}
                        iconTone="warning"
                      />
                    </div>

                    <div>
                      <div className="my-6 h-px bg-border" />
                      <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                        Missing evidence
                      </p>
                      <div className="mt-4 rounded-xl border border-border bg-cream p-5">
                        <p className="text-base leading-7 text-ink-secondary">
                          {diligenceContent.missing_evidence}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="mt-5 text-base leading-7 text-ink-secondary">
                    Diligence report data is not available in the expected format.
                  </p>
                )}
              </div>
            </ReportCard>
          ) : (
            <div className="rounded-xl border border-border bg-white p-6">
              <p className="text-lg leading-8 text-ink-secondary">
                No diligence or routing reports yet
              </p>
              <div className="mt-6 flex flex-wrap gap-4">
                <Link
                  className="inline-flex items-center gap-3 rounded-full border border-ink px-5 py-3 text-sm font-medium text-ink transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] hover:border-ink"
                  to={`/diligence?candidate_id=${candidateId}`}
                >
                  Run Diligence
                </Link>
                <Link
                  className="inline-flex items-center gap-3 rounded-full border border-ink px-5 py-3 text-sm font-medium text-ink transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] hover:border-ink"
                  to={`/route?candidate_id=${candidateId}`}
                >
                  Run Routing
                </Link>
              </div>
            </div>
          )}

          {recommendationReport ? (
            <ReportCard className="min-h-[240px]">
              <div className="pr-12">
                <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                  {recommendationReport.report_type}
                </p>
                <h2 className="mt-4 text-[clamp(1.8rem,3vw,3rem)]">
                  {formatReportTitle(recommendationReport.report_type)}
                </h2>

                {recommendationContent ? (
                  <div className="mt-8 space-y-8">
                    <div className="flex flex-wrap gap-3">
                      <StatusPill label={recommendationContent.recommended_pathway} tone="dark" />
                      <StatusPill
                        label={recommendationContent.human_review ? "Human review" : "Autonomous route"}
                        tone={recommendationContent.human_review ? "accent" : "muted"}
                      />
                    </div>

                    <div className="grid gap-4 md:grid-cols-3">
                      <InfoBlock label="Recommended pathway" value={recommendationContent.recommended_pathway} />
                      <InfoBlock label="Confidence" value={formatPercent(recommendationContent.confidence)} />
                      <InfoBlock
                        label="Human review"
                        value={recommendationContent.human_review ? "Required" : "Not required"}
                      />
                    </div>

                    <div>
                      <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                        Reasoning
                      </p>
                      <p className="mt-4 text-base leading-7 text-ink-secondary">
                        {recommendationContent.reasoning}
                      </p>
                    </div>

                    <div>
                      <div className="my-6 h-px bg-border" />
                      <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
                        Interview questions
                      </p>
                      <ul className="mt-4 space-y-3">
                        {recommendationContent.interview_questions.length > 0 ? (
                          recommendationContent.interview_questions.map((question) => (
                            <li key={question} className="flex items-start gap-3 text-sm leading-6 text-ink-secondary">
                              <span className="mt-0.5 grid h-5 w-5 flex-none place-items-center rounded-full border border-ink text-ink">
                                <CheckCircle2 className="h-3 w-3" />
                              </span>
                              <span>{question}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-sm leading-6 text-ink-secondary">No interview questions reported</li>
                        )}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="mt-5 text-base leading-7 text-ink-secondary">
                    Recommendation data is not available in the expected format.
                  </p>
                )}
              </div>
            </ReportCard>
          ) : null}
        </section>
      ) : null}
    </PageShell>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-cream p-5">
      <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">{label}</p>
      <p className="mt-3 text-base text-ink">{value}</p>
    </div>
  );
}

function formatPercent(value?: number | null) {
  if (typeof value !== "number") return "n/a";
  return `${Math.round(value * 100)}%`;
}

function parseDiligenceReport(content: unknown): DiligenceReport | null {
  if (!content) return null;

  if (typeof content === "string") {
    try {
      const parsed = JSON.parse(content) as DiligenceReport;
      return parsed;
    } catch {
      return null;
    }
  }

  if (typeof content === "object" && !Array.isArray(content)) {
    return content as DiligenceReport;
  }

  return null;
}

function parseRecommendationReport(content: unknown): Recommendation | null {
  if (!content) return null;

  if (typeof content === "string") {
    try {
      return JSON.parse(content) as Recommendation;
    } catch {
      return null;
    }
  }

  if (typeof content === "object" && !Array.isArray(content)) {
    return content as Recommendation;
  }

  return null;
}

function ListPanel({
  title,
  items,
  iconTone,
}: {
  title: string;
  items: string[];
  iconTone: "positive" | "warning";
}) {
  const emptyState = items.length === 0 ? ["No items reported"] : items;

  return (
    <div className="rounded-xl border border-border bg-white p-5">
      <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">{title}</p>
      <ul className="mt-4 space-y-3">
        {emptyState.map((item) => (
          <li key={item} className="flex items-start gap-3 text-sm leading-6 text-ink-secondary">
            <span
              className={[
                "mt-0.5 grid h-5 w-5 flex-none place-items-center rounded-full border",
                iconTone === "positive"
                  ? "border-ink text-ink"
                  : "border-terracotta text-terracotta",
              ].join(" ")}
            >
              {iconTone === "positive" ? (
                <CheckCircle2 className="h-3 w-3" />
              ) : (
                <AlertTriangle className="h-3 w-3" />
              )}
            </span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatReportTitle(reportType: string) {
  if (reportType === "diligence") return "Diligence Report";
  if (reportType === "recommendation") return "Routing Report";
  return "Report";
}

function formatReportContent(content: unknown) {
  if (typeof content === "string") return content;
  return JSON.stringify(content, null, 2);
}
