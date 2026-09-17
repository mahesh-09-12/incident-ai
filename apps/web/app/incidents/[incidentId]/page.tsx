import React from 'react';
import { IncidentDetail } from '@/features/incidents/components/incident-detail';

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
      <main>
        <IncidentDetail incidentId={incidentId} />
      </main>
    </div>
  );
}
