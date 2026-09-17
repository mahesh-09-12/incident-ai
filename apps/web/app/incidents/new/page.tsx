import React from 'react';
import { IncidentCreateForm } from '@/features/incidents/components/incident-create-form';

export const metadata = {
  title: 'Create Incident | IncidentAI',
  description: 'Report a new incident to the platform',
};

export default function NewIncidentPage() {
  return (
    <div className="w-full max-w-3xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
      <header className="mb-8 border-b border-slate-800 pb-5">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight">Create New Incident</h1>
        <p className="text-sm sm:text-base text-slate-400 mt-2">
          Report an ongoing incident or issue. Please provide as much detail as possible to assist with the investigation.
        </p>
      </header>
      
      <main>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-5 sm:p-8">
          <IncidentCreateForm />
        </div>
      </main>
    </div>
  );
}
