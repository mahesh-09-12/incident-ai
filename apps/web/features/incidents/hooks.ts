import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getIncidents,
  getIncident,
  createIncident,
  updateIncident,
  deleteIncident,
} from './api';
import { IncidentCreate, IncidentUpdate, GetIncidentsParams } from './types';

export const incidentKeys = {
  all: ['incidents'] as const,
  lists: () => [...incidentKeys.all, 'list'] as const,
  list: (filters: GetIncidentsParams) => [...incidentKeys.lists(), { filters }] as const,
  details: () => [...incidentKeys.all, 'detail'] as const,
  detail: (id: string) => [...incidentKeys.details(), id] as const,
};

export function useIncidents(params?: GetIncidentsParams) {
  return useQuery({
    queryKey: incidentKeys.list(params || {}),
    queryFn: () => getIncidents(params),
  });
}

export function useIncident(id: string) {
  return useQuery({
    queryKey: incidentKeys.detail(id),
    queryFn: () => getIncident(id),
    enabled: !!id,
  });
}

export function useCreateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: IncidentCreate) => createIncident(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: incidentKeys.lists() });
    },
  });
}

export function useUpdateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: IncidentUpdate }) => updateIncident(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: incidentKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: incidentKeys.lists() });
    },
  });
}

export function useDeleteIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteIncident(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: incidentKeys.lists() });
      queryClient.removeQueries({ queryKey: incidentKeys.detail(id) });
    },
  });
}
