import React from 'react';
import { InvestigationResult } from '@/features/investigations/components/investigation-result';

export const metadata = {
  title: 'Investigation Report | IncidentAI',
  description: 'View AI investigation results',
};

export default async function InvestigationResultPage({
  params,
}: {
  params: Promise<{ incidentId: string; investigationId: string }>;
}) {
  const resolvedParams = await params;
  const { incidentId, investigationId } = resolvedParams;

  return (
    <div className="w-full max-w-5xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
      <main>
        <InvestigationResult incidentId={incidentId} investigationId={investigationId} />
      </main>
    </div>
  );
}
