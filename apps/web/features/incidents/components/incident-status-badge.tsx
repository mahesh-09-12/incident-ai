import React from 'react';

const statusConfig = {
  open: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 shadow-[0_0_8px_-2px_rgba(99,102,241,0.4)]',
  investigating: 'bg-purple-500/10 text-purple-400 border-purple-500/30 shadow-[0_0_8px_-2px_rgba(168,85,247,0.4)]',
  resolved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_8px_-2px_rgba(16,185,129,0.4)]',
  closed: 'bg-slate-800/50 text-slate-400 border-slate-700 shadow-[0_0_8px_-2px_rgba(148,163,184,0.1)]',
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
