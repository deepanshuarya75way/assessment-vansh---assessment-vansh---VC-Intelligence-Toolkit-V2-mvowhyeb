export type PortfolioMatch = {
  id?: number;
  name: string;
  description?: string;
  similarity?: number;
};

export type Candidate = {
  id?: number;
  company: string;
  description: string;
  source?: string | null;
  github_url?: string | null;
  similarity_score?: number | null;
  portfolio_matches?: PortfolioMatch[] | null;
  confidence?: number | null;
  reasoning?: string | null;
  created_at?: string;
};

export type DiligenceReport = {
  strengths: string[];
  weaknesses: string[];
  wrapper_risk: string;
  data_moat: string;
  model_dependency: string;
  overall_score: number;
  confidence: number;
  human_review_required: boolean;
  missing_evidence: string;
};

export type Recommendation = {
  recommended_pathway: string;
  confidence: number;
  interview_questions: string[];
  reasoning: string;
  human_review: boolean;
};

export type RunRecord = {
  id: number;
  module: string;
  status: string;
  started_at: string;
  completed_at?: string | null;
};

export type ReportRecord = {
  id: number;
  candidate_id: number;
  report_type: string;
  content: unknown;
  created_at: string;
};
