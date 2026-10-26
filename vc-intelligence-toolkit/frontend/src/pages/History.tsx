import { useEffect, useState } from "react";
import PageShell from "@/components/PageShell";
import StatusPill from "@/components/StatusPill";
import { getHistory } from "@/services/api";
import type { RunRecord } from "@/types/api";

export default function History() {
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

  return (
    <PageShell>
      <section className="max-w-4xl">
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">Run History</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          A restrained operational record of the toolkit's recent module runs.
        </p>
      </section>

      {error ? <p className="mt-8 text-sm text-terracotta">{error}</p> : null}

      <section className="mt-14 overflow-hidden rounded-xl border border-border bg-white">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-border text-sm text-ink-secondary">
              <th className="px-6 py-5 font-medium">Module</th>
              <th className="px-6 py-5 font-medium">Status</th>
              <th className="px-6 py-5 font-medium">Started</th>
              <th className="px-6 py-5 font-medium">Completed</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td className="px-6 py-8 text-sm text-ink-secondary" colSpan={4}>
                  Loading history...
                </td>
              </tr>
            ) : runs.length === 0 ? (
              <tr>
                <td className="px-6 py-8 text-sm text-ink-secondary" colSpan={4}>
                  No data yet
                </td>
              </tr>
            ) : runs.map((run) => (
              <tr key={run.id}>
                <td className="px-6 py-5 capitalize">{run.module}</td>
                <td className="px-6 py-5">
                  <StatusPill label={run.status} tone={run.status === "completed" ? "dark" : "accent"} />
                </td>
                <td className="px-6 py-5 text-sm text-ink-secondary">
                  {formatDate(run.started_at)}
                </td>
                <td className="px-6 py-5 text-sm text-ink-secondary">
                  {formatDate(run.completed_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </PageShell>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Pending";
  return new Date(value).toLocaleString();
}
