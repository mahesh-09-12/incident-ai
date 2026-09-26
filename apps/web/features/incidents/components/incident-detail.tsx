"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useIncident, useDeleteIncident } from '../hooks';
import { IncidentSeverityBadge } from './incident-severity-badge';
import { IncidentStatusBadge } from './incident-status-badge';
import Link from 'next/link';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { EvidenceList } from '@/features/evidence/components/evidence-list';
import { useEvidenceList } from '@/features/evidence/hooks';
import { InvestigationList } from '@/features/investigations/components/investigation-list';
import { IncidentEditForm } from './incident-edit-form';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export function IncidentDetail({ incidentId }: { incidentId: string }) {
  const router = useRouter();
  const { data: incident, isLoading, isError, error, refetch } = useIncident(incidentId);
  const { data: evidenceList } = useEvidenceList(incidentId);
  const deleteMutation = useDeleteIncident();
  
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  
  const hasEvidence = !!evidenceList && evidenceList.length > 0;

  const handleDelete = async () => {
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteMutation.mutateAsync(incidentId);
      router.push('/incidents');
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          setDeleteError('Unable to connect to the server. Please check your internet connection.');
        } else {
          setDeleteError(err.message);
        }
      } else {
        setDeleteError('An unexpected error occurred while deleting the incident.');
      }
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6" aria-busy="true">
        <div className="h-8 w-1/3 bg-slate-800 rounded"></div>
        <div className="h-4 w-1/4 bg-slate-800 rounded mt-2"></div>
        <div className="flex gap-4 mt-6">
          <div className="h-6 w-20 bg-slate-800 rounded"></div>
          <div className="h-6 w-24 bg-slate-800 rounded"></div>
        </div>
        <div className="h-24 w-full bg-slate-800 rounded mt-6"></div>
      </div>
    );
  }

  if (isError) {
    let errorMessage = 'Failed to load incident details.';
    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Unable to connect to the server. Please check your network connection.';
      } else {
        errorMessage = error.message;
      }
    }
    return (
      <div role="alert" className="border border-red-500/20 bg-red-500/10 rounded-lg p-6 flex flex-col items-center justify-center text-center">
        <h3 className="text-lg font-medium text-red-400 mb-2">Error Loading Incident</h3>
        <p className="text-red-400/80 mb-6 text-sm max-w-md">{errorMessage}</p>
        <button 
          onClick={() => refetch()}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="border border-slate-800 border-dashed rounded-lg p-12 text-center w-full">
        <h3 className="text-lg font-medium text-slate-300 mb-2">Incident Not Found</h3>
        <p className="text-slate-500 text-sm">The incident you requested does not exist or you do not have access to it.</p>
      </div>
    );
  }

  const incidentBreadcrumb = (
    <div className="mb-6 w-full overflow-hidden">
      <Breadcrumb>
        <BreadcrumbList className="flex-nowrap">
          <BreadcrumbItem className="whitespace-nowrap shrink-0">
            <BreadcrumbLink asChild>
              <Link href="/dashboard">Dashboard</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator className="shrink-0" />
          <BreadcrumbItem className="whitespace-nowrap shrink-0">
            <BreadcrumbLink asChild>
              <Link href="/incidents">Incidents</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator className="shrink-0" />
          <BreadcrumbItem className="min-w-0">
            <BreadcrumbPage className="truncate block max-w-[150px] sm:max-w-[400px]">
              {incident.title}
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    </div>
  );

  if (isEditing) {
    return (
      <div className="space-y-6">
        {incidentBreadcrumb}
        <header className="border-b border-slate-800 pb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight drop-shadow-[0_0_8px_rgba(255,255,255,0.15)]">
            Edit Incident
          </h1>
        </header>
        <div className="glass-panel rounded-lg p-5 sm:p-6">
          <IncidentEditForm 
            incident={incident} 
            onCancel={() => setIsEditing(false)} 
            onSuccess={() => setIsEditing(false)} 
          />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-full">
      {incidentBreadcrumb}
      
      {deleteError && (
        <div role="alert" className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded p-4">
          <p className="font-medium">Failed to delete incident</p>
          <p className="mt-1 opacity-80">{deleteError}</p>
        </div>
      )}

      <header className="border-b border-slate-800 pb-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight break-words drop-shadow-[0_0_8px_rgba(255,255,255,0.15)]">
              {incident.title}
            </h1>
            <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
              <IncidentSeverityBadge severity={incident.severity} />
              <IncidentStatusBadge status={incident.status} />
              <span className="text-slate-500 hidden sm:inline">&bull;</span>
              <span className="text-slate-400">Environment: <strong className="text-slate-300 font-medium">{incident.environment}</strong></span>
              <span className="text-slate-500 hidden sm:inline">&bull;</span>
              <span className="text-slate-400">Service: <strong className="text-slate-300 font-medium">{incident.service}</strong></span>
            </div>
            <p className="mt-4 text-xs text-slate-500">
              Created {new Date(incident.created_at).toLocaleString()}
            </p>
          </div>
          
          <div className="flex-shrink-0 flex items-center gap-3">
            <button
              onClick={() => setIsEditing(true)}
              disabled={isDeleting}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50 border border-slate-700 cursor-pointer"
            >
              Edit Incident
            </button>
            <AlertDialog>
              <AlertDialogTrigger
                disabled={isDeleting}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 border border-red-500/20 cursor-pointer"
              >
                {isDeleting ? 'Deleting...' : 'Delete Incident'}
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-slate-900 border-slate-800">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-slate-100">Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription className="text-slate-400">
                    This action cannot be undone. This will permanently delete this incident.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700 hover:text-white focus:ring-slate-500">Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete} className="bg-red-600 text-white hover:bg-red-700 focus:ring-red-500">Delete Incident</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </header>
      
      <section>
        <h2 className="text-lg font-medium text-slate-200 mb-3">Description</h2>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 sm:p-5 whitespace-pre-wrap text-sm text-slate-300 break-words">
          {incident.description}
        </div>
      </section>

      <div className="flex flex-col gap-8">
        <section>
          <h2 className="text-lg font-medium text-slate-200 mb-3 border-b border-slate-800 pb-2">
            Evidence
          </h2>
          <div className="mt-4">
            <EvidenceList incidentId={incidentId} />
          </div>
        </section>

        <section>
          <h2 className="text-lg font-medium text-slate-200 mb-3 border-b border-slate-800 pb-2">
            Investigations
          </h2>
          <div className="mt-4">
            <InvestigationList incidentId={incidentId} hasEvidence={hasEvidence} />
          </div>
        </section>
      </div>
    </div>
  );
}
