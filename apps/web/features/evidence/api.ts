import { apiClient } from '@/lib/api/client';
import { Evidence } from './types';

export const getEvidenceList = async (incidentId: string): Promise<Evidence[]> => {
  return apiClient.get<Evidence[]>(`api/v1/incidents/${incidentId}/evidence`);
};

export const uploadEvidence = async (incidentId: string, file: File): Promise<Evidence> => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post<Evidence>(`api/v1/incidents/${incidentId}/evidence`, formData);
};

export const deleteEvidence = async (incidentId: string, evidenceId: string): Promise<void> => {
  // incidentId is part of the logical domain but the backend endpoint just needs evidenceId
  return apiClient.delete<void>(`api/v1/incidents/${incidentId}/evidence/${evidenceId}`);
};
