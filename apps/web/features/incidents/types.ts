export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: string;
  environment: string;
  service: string;
  status: string;
  created_at: string;
}

export interface IncidentCreate {
  title: string;
  description: string;
  severity: string;
  environment: string;
  service: string;
}

export interface IncidentUpdate {
  title?: string;
  description?: string;
  severity?: string;
  environment?: string;
  service?: string;
  status?: string;
}

export interface GetIncidentsParams {
  skip?: number;
  limit?: number;
  severity?: string;
  status?: string;
}
