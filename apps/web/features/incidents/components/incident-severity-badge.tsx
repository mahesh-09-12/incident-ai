import React from 'react';

const severityConfig = {
  critical: 'bg-red-500/10 text-red-400 border-red-500/20',
  high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  low: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
} as const;

export function IncidentSeverityBadge({ severity }: { severity: string }) {
  const normalizedSeverity = severity.toLowerCase();
  const classes = severityConfig[normalizedSeverity as keyof typeof severityConfig] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${classes}`}>
      <span className="sr-only">Severity: </span>
      {severity}
    </span>
  );
}
