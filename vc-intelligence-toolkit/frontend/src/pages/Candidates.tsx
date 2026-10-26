import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageShell from "@/components/PageShell";
import { getCandidates } from "@/services/api";
import type { Candidate } from "@/types/api";

export default function Candidates() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    getCandidates()
      .then((data) => {
        if (!cancelled) {
          setCandidates(data);
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
        <h1 className="text-[clamp(1.75rem,3vw,2.5rem)]">Candidates</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-secondary">
          A compact list of discovered candidates with their current similarity and confidence signals.
        </p>
      </section>

      {error ? <p className="mt-8 text-sm text-terracotta">{error}</p> : null}

      <section className="mt-14 overflow-hidden rounded-xl border border-border bg-white">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-border text-sm text-ink-secondary">
              <th className="px-6 py-5 font-medium">Candidate ID</th>
              <th className="px-6 py-5 font-medium">Company</th>
              <th className="px-6 py-5 font-medium">Similarity</th>
              <th className="px-6 py-5 font-medium">Confidence</th>
              <th className="px-6 py-5 font-medium">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td className="px-6 py-8 text-sm text-ink-secondary" colSpan={5}>
                  Loading candidates...
                </td>
              </tr>
            ) : candidates.length === 0 ? (
              <tr>
                <td className="px-6 py-8 text-sm text-ink-secondary" colSpan={5}>
                  No data yet
                </td>
              </tr>
            ) : candidates.map((candidate) => (
              <tr key={candidate.id}>
                <td className="px-6 py-5 text-sm text-ink-secondary">
                  {candidate.id ?? "n/a"}
                </td>
                <td className="px-6 py-5">
                  <Link className="hover:text-ink" to={`/candidates/${candidate.id}`}>
                    {candidate.company}
                  </Link>
                </td>
                <td className="px-6 py-5 text-sm text-ink-secondary">
                  {formatPercent(candidate.similarity_score)}
                </td>
                <td className="px-6 py-5 text-sm text-ink-secondary">
                  {formatPercent(candidate.confidence)}
                </td>
                <td className="px-6 py-5 text-sm text-ink-secondary">
                  {formatDate(candidate.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </PageShell>
  );
}

function formatPercent(value?: number | null) {
  if (typeof value !== "number") return "n/a";
  return `${Math.round(value * 100)}%`;
}

function formatDate(value?: string | null) {
  if (!value) return "Pending";
  return new Date(value).toLocaleString();
}