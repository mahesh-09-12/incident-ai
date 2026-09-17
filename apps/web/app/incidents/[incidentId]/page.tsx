import React from 'react';
import { EvidenceList } from '@/features/evidence/components/evidence-list';

export const metadata = {
  title: 'Incident Details | IncidentAI',
  description: 'View incident details and manage evidence',
};

export default async function IncidentDetailPage({
  params,
}: {
  params: Promise<{ incidentId: string }>;
}) {
  const resolvedParams = await params;
  const { incidentId } = resolvedParams;

  return (
    <div className="w-full max-w-5xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
      <header className="mb-8 border-b border-slate-800 pb-5">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight">Incident Details</h1>
        <p className="text-sm sm:text-base text-slate-400 mt-2">
          Manage evidence and artifacts for this incident.
        </p>
      </header>
      
      <main className="space-y-8">
        <section>
          <h2 className="text-xl font-semibold text-slate-100 mb-4 tracking-tight border-b border-slate-800 pb-2">
            Evidence Management
          </h2>
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-5 sm:p-6">
            <EvidenceList incidentId={incidentId} />
          </div>
        </section>
      </main>
    </div>
  );
}
