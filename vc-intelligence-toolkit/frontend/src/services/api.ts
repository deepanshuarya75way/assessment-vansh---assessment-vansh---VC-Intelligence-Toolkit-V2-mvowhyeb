import type {
  Candidate,
  DiligenceReport,
  Recommendation,
  ReportRecord,
  RunRecord,
} from "@/types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function discoverCandidates(query: string) {
  return request<Candidate[]>("/api/corridor/discover", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export function evaluateDiligence(candidateId: number) {
  return request<DiligenceReport>("/api/moatlens/evaluate", {
    method: "POST",
    body: JSON.stringify({ candidate_id: candidateId }),
  });
}

export function routeCandidate(candidateId: number, applicationText: string) {
  return request<Recommendation>("/api/navigator/route", {
    method: "POST",
    body: JSON.stringify({
      candidate_id: candidateId,
      application_text: applicationText,
    }),
  });
}

export function getHistory() {
  return request<RunRecord[]>("/api/history");
}

export function getCandidates() {
  return request<Candidate[]>("/api/candidates");
}

export function getCandidateReports(candidateId: number) {
  return request<ReportRecord[]>(`/api/candidates/${candidateId}/reports`);
}

export function getReport(id: number) {
  return request<ReportRecord>(`/api/reports/${id}`);
}
