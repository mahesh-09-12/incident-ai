"use client";

import React from 'react';
import Link from 'next/link';
import { useIncidents } from '../hooks';
import { IncidentListItem } from './incident-list-item';

export function IncidentList() {
  const { data: incidents, isLoading, isError, error, refetch, isFetching } = useIncidents();

  if (isLoading) {
    return (
      <div className="animate-pulse flex flex-col gap-4 w-full" aria-busy="true" aria-label="Loading incidents">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-panel rounded-lg p-4 sm:p-6 h-32 w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-5 w-16 bg-slate-800 rounded"></div>
              <div className="h-5 w-16 bg-slate-800 rounded"></div>
              <div className="h-4 w-24 bg-slate-800 rounded hidden sm:block"></div>
            </div>
            <div className="h-6 w-full sm:w-3/4 bg-slate-800 rounded mb-2"></div>
            <div className="h-4 w-2/3 sm:w-1/2 bg-slate-800 rounded"></div>
          </div>
        ))}
        <span className="sr-only">Loading incidents...</span>
      </div>
    );
  }

  if (isError) {
    let errorTitle = 'Failed to load incidents';
    let errorMessage = 'An unexpected error occurred while communicating with the server.';

    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorTitle = 'Connection Error';
        errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
      } else if (error.name === 'ApiError') {
        errorTitle = 'Server Error';
        errorMessage = error.message || errorMessage;
      } else {
        errorMessage = error.message;
      }
    }

    return (
      <div 
        role="alert" 
        aria-live="assertive"
        className="border border-red-500/20 bg-red-500/10 rounded-lg p-4 sm:p-6 flex flex-col items-center justify-center text-center w-full max-w-full overflow-hidden"
      >
        <h3 className="text-base sm:text-lg font-medium text-red-400 mb-2">{errorTitle}</h3>
        <p className="text-red-400/80 mb-6 text-sm max-w-[280px] sm:max-w-sm break-words">
          {errorMessage}
        </p>
        <button 
          onClick={() => refetch()}
          disabled={isFetching}
          aria-busy={isFetching}
          className="px-4 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-slate-200 border border-slate-700 hover:border-slate-600 hover:shadow-[0_0_15px_-3px_rgba(255,255,255,0.05)] rounded text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isFetching ? 'Retrying...' : 'Retry request'}
        </button>
      </div>
    );
  }

  // Handle malformed/unexpected API response (e.g. not an array)
  if (incidents !== undefined && !Array.isArray(incidents)) {
    return (
      <div 
        role="alert"
        aria-live="assertive"
        className="border border-amber-500/20 bg-amber-500/10 rounded-lg p-4 sm:p-6 flex flex-col items-center justify-center text-center w-full max-w-full overflow-hidden"
      >
        <h3 className="text-base sm:text-lg font-medium text-amber-400 mb-2">Unexpected Data Format</h3>
        <p className="text-amber-400/80 mb-6 text-sm max-w-[280px] sm:max-w-sm break-words">
          The server returned data in an unexpected format.
        </p>
        <button 
          onClick={() => refetch()}
          disabled={isFetching}
          aria-busy={isFetching}
          className="px-4 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-slate-200 border border-slate-700 hover:border-slate-600 hover:shadow-[0_0_15px_-3px_rgba(255,255,255,0.05)] rounded text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isFetching ? 'Retrying...' : 'Retry request'}
        </button>
      </div>
    );
  }

  if (!incidents || incidents.length === 0) {
    return (
      <div className="border border-slate-800 border-dashed rounded-lg p-6 sm:p-12 flex flex-col items-center justify-center text-center w-full">
        <h3 className="text-base sm:text-lg font-medium text-slate-300 mb-2">No incidents found</h3>
        <p className="text-slate-500 mb-6 max-w-[280px] sm:max-w-sm text-sm sm:text-base">
          There are currently no incidents recorded in this workspace. 
          When an incident occurs, it will appear here.
        </p>
        <Link 
          href="/incidents/new"
          className="px-4 py-2 bg-indigo-600/20 text-indigo-300 hover:bg-indigo-500/30 neon-border shadow-[0_0_10px_-2px_rgba(99,102,241,0.3)] hover:shadow-[0_0_20px_-3px_rgba(99,102,241,0.6)] border border-indigo-500/50 rounded text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950"
        >
          Create your first incident
        </Link>
      </div>
    );
  }

  return (
    <ul className="flex flex-col gap-4">
      {incidents.map((incident) => (
        <IncidentListItem key={incident.id} incident={incident} />
      ))}
    </ul>
  );
}
