import { apiClient } from '@/lib/api/client';
import { Investigation } from './types';

export const getInvestigations = async (incidentId: string): Promise<Investigation[]> => {
  return apiClient.get<Investigation[]>(`api/v1/incidents/${incidentId}/investigations`);
};

export const getInvestigation = async (incidentId: string, investigationId: string): Promise<Investigation> => {
  return apiClient.get<Investigation>(`api/v1/incidents/${incidentId}/investigations/${investigationId}`);
};

export const createInvestigation = async (incidentId: string): Promise<Investigation> => {
  return apiClient.post<Investigation>(`api/v1/incidents/${incidentId}/investigations`);
};
