export type InvestigationStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface Investigation {
  id: string;
  incident_id: string;
  status: InvestigationStatus;
  summary: string | null;
  root_cause: string | null;
  recommendations: string | null;
  created_at: string;
  completed_at: string | null;
}
