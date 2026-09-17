"use client";

import React from 'react';
import Link from 'next/link';
import { useIncidents } from '../hooks';
import { IncidentListItem } from './incident-list-item';

export function IncidentList() {
  const { data: incidents, isLoading, isError, error, refetch } = useIncidents();

  if (isLoading) {
    return (
      <div className="animate-pulse flex flex-col gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="border border-slate-800 bg-slate-900 rounded-lg p-6 h-32">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-5 w-16 bg-slate-800 rounded"></div>
              <div className="h-5 w-16 bg-slate-800 rounded"></div>
              <div className="h-4 w-24 bg-slate-800 rounded"></div>
            </div>
            <div className="h-6 w-3/4 bg-slate-800 rounded mb-2"></div>
            <div className="h-4 w-1/2 bg-slate-800 rounded"></div>
          </div>
        ))}
        <span className="sr-only">Loading incidents...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="border border-red-500/20 bg-red-500/10 rounded-lg p-6 flex flex-col items-center justify-center text-center">
        <h3 className="text-lg font-medium text-red-400 mb-2">Failed to load incidents</h3>
        <p className="text-red-400/80 mb-6 text-sm">
          {error instanceof Error ? error.message : 'An unexpected error occurred while communicating with the server.'}
        </p>
        <button 
          onClick={() => refetch()}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500"
        >
          Retry request
        </button>
      </div>
    );
  }

  if (!incidents || incidents.length === 0) {
    return (
      <div className="border border-slate-800 border-dashed rounded-lg p-12 flex flex-col items-center justify-center text-center">
        <h3 className="text-lg font-medium text-slate-300 mb-2">No incidents found</h3>
        <p className="text-slate-500 mb-6 max-w-sm">
          There are currently no incidents recorded in this workspace. 
          When an incident occurs, it will appear here.
        </p>
        <Link 
          href="/incidents/new"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950"
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
