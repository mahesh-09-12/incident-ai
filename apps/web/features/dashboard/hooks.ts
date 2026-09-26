import { useQuery } from '@tanstack/react-query';
import { getDashboardStats } from './api';

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: getDashboardStats,
    refetchInterval: 5000, // Poll every 5s for dashboard updates
  });
};
