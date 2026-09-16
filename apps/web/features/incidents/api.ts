import { apiClient } from '@/lib/api/client';
import { Incident, IncidentCreate, IncidentUpdate, GetIncidentsParams } from './types';

export const getIncidents = async (params?: GetIncidentsParams): Promise<Incident[]> => {
  const queryParams: Record<string, string> = {};
  
  if (params) {
    if (params.skip !== undefined) queryParams.skip = params.skip.toString();
    if (params.limit !== undefined) queryParams.limit = params.limit.toString();
    if (params.severity) queryParams.severity = params.severity;
    if (params.status) queryParams.status = params.status;
  }

  return apiClient.get<Incident[]>('api/v1/incidents', { params: queryParams });
};

export const getIncident = async (id: string): Promise<Incident> => {
  return apiClient.get<Incident>(`api/v1/incidents/${id}`);
};

export const createIncident = async (data: IncidentCreate): Promise<Incident> => {
  return apiClient.post<Incident>('api/v1/incidents', data);
};

export const updateIncident = async (id: string, data: IncidentUpdate): Promise<Incident> => {
  return apiClient.patch<Incident>(`api/v1/incidents/${id}`, data);
};

export const deleteIncident = async (id: string): Promise<void> => {
  return apiClient.delete<void>(`api/v1/incidents/${id}`);
};
