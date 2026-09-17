import React from 'react';
import Link from 'next/link';
import { Incident } from '../types';
import { IncidentSeverityBadge } from './incident-severity-badge';
import { IncidentStatusBadge } from './incident-status-badge';

export function IncidentListItem({ incident }: { incident: Incident }) {
  // compact description
  const compactDescription = incident.description?.length > 120 
    ? incident.description.substring(0, 120) + '...'
    : incident.description;

  const createdDate = new Date(incident.created_at).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  return (
    <li className="group border border-slate-800 bg-slate-900 hover:bg-slate-800/50 hover:border-slate-700 rounded-lg transition-colors overflow-hidden">
      <Link href={`/incidents/${incident.id}`} className="block p-4 sm:p-6 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-inset rounded-lg">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <IncidentSeverityBadge severity={incident.severity} />
              <IncidentStatusBadge status={incident.status} />
              <span className="text-sm text-slate-500 truncate" title={`Service: ${incident.service}`}>
                <span className="sr-only">Service:</span>
                {incident.service}
              </span>
              <span className="text-slate-600 text-sm" aria-hidden="true">&bull;</span>
              <span className="text-sm text-slate-500 truncate" title={`Environment: ${incident.environment}`}>
                <span className="sr-only">Environment:</span>
                {incident.environment}
              </span>
            </div>
            
            <h3 className="text-base sm:text-lg font-semibold text-slate-100 truncate mb-1">
              {incident.title}
            </h3>
            
            <p className="text-sm text-slate-400 line-clamp-2">
              {compactDescription}
            </p>
          </div>
          
          <div className="flex-shrink-0 flex sm:flex-col items-center sm:items-end justify-between sm:justify-start">
            <time dateTime={incident.created_at} className="text-xs text-slate-500 font-mono">
              {createdDate}
            </time>
          </div>
          
        </div>
      </Link>
    </li>
  );
}
