import { useEffect, useMemo, useState } from "react";
import ActionButton from "@/components/ActionButton";
import PageShell from "@/components/PageShell";
import StatusPill from "@/components/StatusPill";
import { getHistory } from "@/services/api";
import type { RunRecord } from "@/types/api";

export const DEMO_VIDEO_URL = "https://youtu.be/9K8Z_SpsUR0";

export default function Dashboard() {
  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    getHistory()
      .then((data) => {
        if (!cancelled) {
          setRuns(data);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const breakdown = useMemo(() => {
    return runs.reduce<Record<string, number>>((acc, run) => {
      acc[run.status] = (acc[run.status] ?? 0) + 1;
      return acc;
    }, {});
  }, [runs]);

  const totalRuns = runs.length;
  const completedRuns = breakdown.completed ?? 0;
  const failedRuns = breakdown.failed ?? 0;
  const moduleSummary = formatModuleSummary(runs);

  return (
    <PageShell>
      <section className="max-w-4xl">
        <p className="mb-5 text-sm uppercase tracking-[0.18em] text-ink-secondary">
          Dashboard
        </p>
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">Overview</h1>
        <div className="mt-6">
          <ActionButton
            onClick={() => window.open(DEMO_VIDEO_URL, "_blank", "noopener,noreferrer")}
          >
            Watch Demo
          </ActionButton>
        </div>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          A quiet view of recent intelligence workflows across discovery,
          diligence, and routing.
        </p>
      </section>

      {error ? <p className="mt-10 text-sm text-terracotta">{error}</p> : null}

      {loading ? <p className="mt-10 text-sm text-ink-secondary">Loading dashboard data... This may take a few moments. In the meantime, feel free to watch the demo. </p> : null}

      <section className="mt-16 grid gap-6">
        <div className="rounded-xl border border-border bg-white p-8">
          <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">
            Workflow snapshot
          </p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <MetricBlock label="Total runs" value={String(totalRuns)} />
            <MetricBlock label="Completed" value={String(completedRuns)} />
            <MetricBlock label="Failed" value={String(failedRuns)} />
          </div>
          <div className="mt-8 border-t border-border pt-5">
            <p className="text-sm uppercase tracking-[0.16em] text-ink-secondary">By module</p>
            <p className="mt-3 text-sm leading-6 text-ink-secondary">{moduleSummary}</p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-white p-8">
          <h2 className="text-[clamp(1.8rem,3vw,3rem)]">Recent runs</h2>
          <div className="mt-8 divide-y divide-border">
            {runs.slice(0, 8).map((run) => (
              <div key={run.id} className="flex items-center justify-between gap-6 py-4">
                <div>
                  <p className="font-medium capitalize">{run.module}</p>
                  <p className="mt-1 text-sm text-ink-secondary">
                    {formatDate(run.started_at)}
                  </p>
                </div>
                <StatusPill label={run.status} tone={run.status === "completed" ? "dark" : "accent"} />
              </div>
            ))}
          </div>
        </div>
      </section>
    </PageShell>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Pending";
  return new Date(value).toLocaleString();
}

function formatModuleSummary(runs: RunRecord[]) {
  const counts = runs.reduce<Record<string, number>>((acc, run) => {
    const key = formatModuleName(run.module);
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});

  const order = ["Corridor", "MoatLens", "Navigator"];
  return order.map((name) => `${name} ${counts[name] ?? 0}`).join(" · ");
}

function formatModuleName(module: string) {
  const normalized = module.toLowerCase();
  if (normalized.includes("corridor")) return "Corridor";
  if (normalized.includes("moatlens")) return "MoatLens";
  if (normalized.includes("navigator")) return "Navigator";
  return module;
}

function MetricBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-cream p-5">
      <p className="min-h-[2.5rem] text-sm uppercase tracking-[0.16em] text-ink-secondary">
        {label}
      </p>
      <p className="mt-3 text-3xl font-medium tracking-tight text-ink">{value}</p>
    </div>
  );
}
