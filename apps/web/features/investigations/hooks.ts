import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getInvestigations, getInvestigation, createInvestigation } from './api';

export const investigationKeys = {
  all: ['investigations'] as const,
  lists: () => [...investigationKeys.all, 'list'] as const,
  list: (incidentId: string) => [...investigationKeys.lists(), { incidentId }] as const,
  details: () => [...investigationKeys.all, 'detail'] as const,
  detail: (incidentId: string, investigationId: string) => [...investigationKeys.details(), incidentId, investigationId] as const,
};

export function useInvestigations(incidentId: string) {
  return useQuery({
    queryKey: investigationKeys.list(incidentId),
    queryFn: () => getInvestigations(incidentId),
    enabled: !!incidentId,
    refetchInterval: (query) => {
      const investigations = query.state.data;
      if (investigations?.some(inv => inv.status === 'RUNNING' || inv.status === 'PENDING')) {
        return 3000;
      }
      return false;
    },
  });
}

export function useInvestigation(incidentId: string, investigationId: string) {
  return useQuery({
    queryKey: investigationKeys.detail(incidentId, investigationId),
    queryFn: () => getInvestigation(incidentId, investigationId),
    enabled: !!incidentId && !!investigationId,
    refetchInterval: (query) => {
      const investigation = query.state.data;
      if (investigation?.status === 'RUNNING' || investigation?.status === 'PENDING') {
        return 3000;
      }
      return false;
    },
  });
}

export function useCreateInvestigation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (incidentId: string) => createInvestigation(incidentId),
    onSuccess: (_, incidentId) => {
      queryClient.invalidateQueries({ queryKey: investigationKeys.list(incidentId) });
    },
  });
}
