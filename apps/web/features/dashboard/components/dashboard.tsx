"use client";

import React from 'react';
import Link from 'next/link';
import { useIncidents } from '@/features/incidents/hooks';
import { useDashboardStats } from '../hooks';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { buttonVariants, Button } from '@/components/ui/button';
import { IncidentListItem } from '@/features/incidents/components/incident-list-item';
import { AlertCircle, Plus } from 'lucide-react';

export function Dashboard() {
  const { data: incidents, isLoading: isIncidentsLoading, isError: isIncidentsError, error: incidentsError, refetch: refetchIncidents } = useIncidents();
  const { data: stats, isLoading: isStatsLoading, isError: isStatsError, error: statsError, refetch: refetchStats } = useDashboardStats();

  const sortedIncidents = incidents 
    ? [...incidents].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()) 
    : [];
  const recentIncidents = sortedIncidents.slice(0, 5);

  if (isIncidentsError || isStatsError) {
    const errorMsg = isIncidentsError 
      ? (incidentsError instanceof Error ? incidentsError.message : 'An unexpected error occurred while communicating with the server.')
      : (statsError instanceof Error ? statsError.message : 'An unexpected error occurred while communicating with the server.');

    return (
      <div className="w-full max-w-6xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
        <Alert variant="destructive" className="max-w-2xl mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error loading dashboard</AlertTitle>
          <AlertDescription className="mt-2 flex flex-col gap-4">
            <p>{errorMsg}</p>
            <div>
              <Button onClick={() => { refetchIncidents(); refetchStats(); }} variant="destructive">
                Retry request
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Page Header */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight drop-shadow-[0_0_8px_rgba(255,255,255,0.15)]">Dashboard</h1>
          <p className="text-sm sm:text-base text-slate-400 mt-1">
            Overview of system incidents and investigation status.
          </p>
        </div>
        <div className="flex-shrink-0">
          <Link 
            href="/incidents/new"
            className={buttonVariants({ variant: "default" })}
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Incident
          </Link>
        </div>
      </header>

      {/* Incident Overview Stats */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-panel neon-glow-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-400">Total Incidents</CardTitle>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-8 w-16 bg-slate-800" />
            ) : (
              <div className="text-2xl font-bold text-slate-100 drop-shadow-[0_0_8px_rgba(255,255,255,0.15)]">{stats?.total_incidents || 0}</div>
            )}
          </CardContent>
        </Card>

        <Card className="glass-panel neon-glow-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-400">Open Incidents</CardTitle>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-8 w-16 bg-slate-800" />
            ) : (
              <div className="text-2xl font-bold text-slate-100 drop-shadow-[0_0_8px_rgba(255,255,255,0.15)]">{stats?.open_incidents || 0}</div>
            )}
          </CardContent>
        </Card>

        <Card className="glass-panel neon-glow-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-400">Investigations Running</CardTitle>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-8 w-16 bg-slate-800" />
            ) : (
              <div className="text-2xl font-bold text-indigo-400 drop-shadow-[0_0_8px_rgba(99,102,241,0.4)]">{stats?.investigations_running || 0}</div>
            )}
          </CardContent>
        </Card>

        <Card className="glass-panel neon-glow-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-400">Investigations Completed</CardTitle>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-8 w-16 bg-slate-800" />
            ) : (
              <div className="text-2xl font-bold text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.4)]">{stats?.investigations_completed || 0}</div>
            )}
          </CardContent>
        </Card>
      </div>

      <Separator className="bg-slate-800" />

      {/* Recent Incidents */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg sm:text-xl font-semibold text-slate-100 tracking-tight drop-shadow-[0_0_8px_rgba(255,255,255,0.15)]">Recent Incidents</h2>
          <Link 
            href="/incidents"
            className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            View all &rarr;
          </Link>
        </div>

        {isIncidentsLoading ? (
          <div className="flex flex-col gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32 w-full glass-panel rounded-lg" />
            ))}
          </div>
        ) : recentIncidents.length > 0 ? (
          <ul className="flex flex-col gap-4">
            {recentIncidents.map(incident => (
              <IncidentListItem key={incident.id} incident={incident} />
            ))}
          </ul>
        ) : (
          <div className="border border-slate-800 border-dashed rounded-lg p-12 flex flex-col items-center justify-center text-center">
            <h3 className="text-lg font-medium text-slate-300 mb-2">No incidents yet</h3>
            <p className="text-slate-500 mb-6 max-w-sm">
              Your workspace is clear. When new incidents occur, they will appear here.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
