import React from 'react';

const statusConfig = {
  open: 'bg-slate-700 text-slate-100 border-slate-600',
  investigating: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  resolved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  closed: 'bg-slate-800 text-slate-400 border-slate-700',
} as const;

export function IncidentStatusBadge({ status }: { status: string }) {
  const normalizedStatus = status.toLowerCase();
  const classes = statusConfig[normalizedStatus as keyof typeof statusConfig] || 'bg-slate-700 text-slate-300 border-slate-600';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${classes}`}>
      <span className="sr-only">Status: </span>
      {status}
    </span>
  );
}
