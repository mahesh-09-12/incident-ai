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

export interface EvidenceContentResponse {
  text: string;
  isText: boolean;
  contentType: string;
}

export const getEvidenceContent = async (incidentId: string, evidenceId: string): Promise<EvidenceContentResponse> => {
  const result = await apiClient.getText(`api/v1/incidents/${incidentId}/evidence/${evidenceId}/content`);
  const contentType = result.contentType.toLowerCase();
  
  const isText = contentType.includes('text/') || 
                 contentType.includes('application/json') || 
                 contentType.includes('application/xml') || 
                 contentType.includes('application/yaml') ||
                 contentType.includes('application/x-yaml');

  return {
    text: result.text,
    contentType: result.contentType,
    isText
  };
};
