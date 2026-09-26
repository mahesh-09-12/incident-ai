import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getEvidenceList, uploadEvidence, deleteEvidence, getEvidenceContent } from './api';

export const evidenceKeys = {
  all: ['evidence'] as const,
  lists: () => [...evidenceKeys.all, 'list'] as const,
  list: (incidentId: string) => [...evidenceKeys.lists(), { incidentId }] as const,
};

export function useEvidenceList(incidentId: string) {
  return useQuery({
    queryKey: evidenceKeys.list(incidentId),
    queryFn: () => getEvidenceList(incidentId),
    enabled: !!incidentId,
  });
}

export function useUploadEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, file }: { incidentId: string; file: File }) => 
      uploadEvidence(incidentId, file),
    onSuccess: (_, { incidentId }) => {
      queryClient.invalidateQueries({ queryKey: evidenceKeys.list(incidentId) });
    },
  });
}

export function useDeleteEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, evidenceId }: { incidentId: string; evidenceId: string }) => 
      deleteEvidence(incidentId, evidenceId),
    onSuccess: (_, { incidentId }) => {
      queryClient.invalidateQueries({ queryKey: evidenceKeys.list(incidentId) });
    },
  });
}

export function useEvidenceContent(incidentId: string, evidenceId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['evidence', incidentId, evidenceId, 'content'],
    queryFn: () => getEvidenceContent(incidentId, evidenceId),
    enabled,
    staleTime: Infinity,
  });
}
