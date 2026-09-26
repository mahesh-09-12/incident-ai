export type InvestigationStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface EvidenceReference {
  evidence_id: string;
  filename: string;
  explanation: string;
}

export interface Hypothesis {
  id: string;
  hypothesis: string;
  reasoning: string;
  supporting_evidence: EvidenceReference[] | null;
  contradicting_evidence: EvidenceReference[] | null;
  missing_evidence: string[] | null;
}

export interface Investigation {
  id: string;
  incident_id: string;
  status: InvestigationStatus;
  summary: string | null;
  root_cause: string | null;
  recommendations: string | null;
  supporting_evidence: EvidenceReference[] | null;
  contradicting_evidence: EvidenceReference[] | null;
  missing_evidence: string[] | null;
  hypotheses: Hypothesis[] | null;
  created_at: string;
  completed_at: string | null;
}
