"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useInvestigations, useCreateInvestigation } from '../hooks';
import { Investigation } from '../types';

export function InvestigationList({ incidentId, hasEvidence }: { incidentId: string, hasEvidence: boolean }) {
  const { data: investigations, isLoading, isError, error, refetch, isFetching } = useInvestigations(incidentId);
  const createMutation = useCreateInvestigation();
  
  const [createError, setCreateError] = useState<string | null>(null);
  const [showAllInvestigations, setShowAllInvestigations] = useState(false);

  const handleStartInvestigation = async () => {
    if (!hasEvidence || createMutation.isPending) return;
    setCreateError(null);
    try {
      await createMutation.mutateAsync(incidentId);
      // Automatically refetch to get the latest status if it's sync, 
      // but the hook already invalidates the list.
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          setCreateError('Unable to connect to the server.');
        } else {
          setCreateError(err.message);
        }
      } else {
        setCreateError('An unexpected error occurred while starting the investigation.');
      }
    }
  };

  const renderStatusBadge = (status: Investigation['status']) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">Completed</span>;
      case 'FAILED':
        return <span className="px-2 py-1 text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 rounded">Failed</span>;
      case 'RUNNING':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded inline-flex items-center">
            <svg className="animate-spin -ml-1 mr-1.5 h-3 w-3 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Running
          </span>
        );
      case 'PENDING':
        return <span className="px-2 py-1 text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">Pending</span>;
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">{status}</span>;
    }
  };

  if (isError) {
    let errorMessage = 'Failed to load investigation history.';
    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Unable to connect to the server.';
      } else {
        errorMessage = error.message;
      }
    }
    return (
      <div role="alert" className="border border-red-500/20 bg-red-500/10 rounded-lg p-6 text-center w-full">
        <h3 className="text-lg font-medium text-red-400 mb-2">Investigation History Error</h3>
        <p className="text-red-400/80 mb-4 text-sm">{errorMessage}</p>
        <button 
          onClick={() => refetch()}
          disabled={isFetching}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50"
        >
          {isFetching ? 'Retrying...' : 'Retry'}
        </button>
      </div>
    );
  }

  // Check for currently active or recent runs to disable start button intelligently if needed,
  // but requirements just say "prevent duplicate submissions". createMutation.isPending handles the immediate click.
  const hasRunning = investigations?.some(inv => inv.status === 'RUNNING' || inv.status === 'PENDING');

  return (
    <div className="space-y-6 w-full max-w-full overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel rounded-lg p-4 sm:p-5">
        <div>
          <h3 className="text-base font-medium text-slate-200">AI Investigation</h3>
          <p className="text-sm text-slate-400 mt-1 max-w-xl">
            Run an AI analysis on the attached evidence to automatically determine a summary, root cause, and recommendations.
          </p>
          {!hasEvidence && (
            <p className="text-sm text-amber-400 mt-2">
              Attach evidence to this incident before starting an investigation.
            </p>
          )}
        </div>
        <div className="flex-shrink-0 mt-2 sm:mt-0">
          <button
            onClick={handleStartInvestigation}
            disabled={!hasEvidence || createMutation.isPending || hasRunning}
            aria-busy={createMutation.isPending}
            className="w-full sm:w-auto px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex justify-center items-center cursor-pointer"
          >
            {createMutation.isPending ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Starting...
              </>
            ) : hasRunning ? (
              'Investigation Running...'
            ) : (
              'Start Investigation'
            )}
          </button>
        </div>
      </div>

      {createError && (
        <div role="alert" aria-live="assertive" className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded p-4">
          <p className="font-medium">Failed to start investigation</p>
          <p className="mt-1 opacity-80">{createError}</p>
        </div>
      )}

      <div>
        <h3 className="text-base font-medium text-slate-200 mb-4">Investigation History</h3>
        {isLoading ? (
          <div className="animate-pulse space-y-3" aria-busy="true">
            <div className="h-16 bg-slate-800 rounded w-full"></div>
            <div className="h-16 bg-slate-800 rounded w-full"></div>
          </div>
        ) : investigations && !Array.isArray(investigations) ? (
          <div role="alert" className="border border-amber-500/20 bg-amber-500/10 rounded p-6 text-center text-sm text-amber-400/80">
            Unexpected data format received from the server.
          </div>
        ) : investigations?.length === 0 ? (
          <div className="border border-slate-800 border-dashed rounded-lg p-8 text-center">
            <p className="text-slate-500 text-sm">No investigations have been run yet.</p>
          </div>
        ) : (
          <>
            <ul className="space-y-3">
              {(showAllInvestigations ? investigations : investigations?.slice(0, 3))?.map((inv) => (
                <li key={inv.id} className="glass-panel neon-glow-hover rounded-lg p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-sm font-medium text-slate-200 truncate">Run ID: {inv.id.substring(0, 8)}...</span>
                      {renderStatusBadge(inv.status)}
                    </div>
                    <div className="mt-2 text-xs text-slate-500 flex flex-wrap gap-3">
                      <span>Started: {new Date(inv.created_at).toLocaleString()}</span>
                      {inv.completed_at && <span>Completed: {new Date(inv.completed_at).toLocaleString()}</span>}
                    </div>
                  </div>
                  
                  <div className="flex-shrink-0 flex items-center gap-3">
                    {inv.status === 'COMPLETED' ? (
                      <Link 
                        href={`/incidents/${incidentId}/investigations/${inv.id}`}
                        className="inline-flex items-center px-3 py-1.5 border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500"
                      >
                        View Report
                      </Link>
                    ) : inv.status === 'FAILED' ? (
                      <button
                        onClick={handleStartInvestigation}
                        disabled={createMutation.isPending || hasRunning}
                        className="text-sm text-indigo-400 hover:text-indigo-300 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded px-2 py-1 disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
                      >
                        Retry
                      </button>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
            {investigations && investigations.length > 3 && !showAllInvestigations && (
              <button
                onClick={() => setShowAllInvestigations(true)}
                className="mt-3 text-sm text-slate-300 hover:text-slate-200 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 rounded px-4 py-2 cursor-pointer w-full text-center border border-dashed border-slate-700 hover:bg-slate-800 bg-slate-900/50"
              >
                See all investigations
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
