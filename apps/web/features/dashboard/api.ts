import { apiClient } from '@/lib/api/client';

export interface DashboardStats {
  total_incidents: number;
  open_incidents: number;
  investigations_running: number;
  investigations_completed: number;
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  return apiClient.get<DashboardStats>('api/v1/dashboard/stats');
};
