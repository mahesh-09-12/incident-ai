"use client";

import React from 'react';
import Link from 'next/link';
import { useInvestigation } from '../hooks';
import { Investigation } from '../types';
import { useIncident } from '@/features/incidents/hooks';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

export function InvestigationResult({ incidentId, investigationId }: { incidentId: string; investigationId: string }) {
  const { data: investigation, isLoading, isError, error, refetch } = useInvestigation(incidentId, investigationId);
  const { data: incident } = useIncident(incidentId);

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6" aria-busy="true">
        <div className="h-8 w-1/3 bg-slate-800 rounded"></div>
        <div className="h-4 w-1/4 bg-slate-800 rounded"></div>
        <div className="space-y-4 mt-8">
          <div className="h-6 w-1/4 bg-slate-800 rounded"></div>
          <div className="h-24 w-full bg-slate-800 rounded"></div>
        </div>
        <div className="space-y-4 mt-6">
          <div className="h-6 w-1/4 bg-slate-800 rounded"></div>
          <div className="h-24 w-full bg-slate-800 rounded"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    let errorMessage = 'Failed to load investigation report.';
    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Unable to connect to the server. Please check your network connection.';
      } else {
        errorMessage = error.message;
      }
    }
    return (
      <div role="alert" className="border border-red-500/20 bg-red-500/10 rounded-lg p-6 flex flex-col items-center justify-center text-center">
        <h3 className="text-lg font-medium text-red-400 mb-2">Error Loading Report</h3>
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

  if (!investigation) {
    return (
      <div className="border border-slate-800 border-dashed rounded-lg p-12 text-center w-full">
        <h3 className="text-lg font-medium text-slate-300 mb-2">Investigation Not Found</h3>
        <p className="text-slate-500 text-sm mb-6">The investigation you requested does not exist.</p>
        <Link 
          href={`/incidents/${incidentId}`}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-medium transition-colors"
        >
          Back to Incident
        </Link>
      </div>
    );
  }

  const renderStatusBadge = (status: Investigation['status']) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">Completed</span>;
      case 'FAILED':
        return <span className="px-2 py-1 text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 rounded">Failed</span>;
      case 'RUNNING':
        return <span className="px-2 py-1 text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">Running</span>;
      case 'PENDING':
        return <span className="px-2 py-1 text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">Pending</span>;
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">{status}</span>;
    }
  };

  const incidentTitle = incident?.title || 'Loading...';

  const investigationBreadcrumb = (
    <div className="mb-6 w-full overflow-hidden">
      <Breadcrumb>
        <BreadcrumbList className="flex-nowrap">
          <BreadcrumbItem className="whitespace-nowrap shrink-0">
            <BreadcrumbLink asChild>
              <Link href="/">Home</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator className="shrink-0" />
          <BreadcrumbItem className="whitespace-nowrap shrink-0">
            <BreadcrumbLink asChild>
              <Link href="/incidents">Incidents</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator className="shrink-0" />
          <BreadcrumbItem className="min-w-0 shrink">
            <BreadcrumbLink className="truncate block max-w-[120px] sm:max-w-[250px]" asChild>
              <Link href={`/incidents/${incidentId}`}>
                {incidentTitle}
              </Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator className="shrink-0" />
          <BreadcrumbItem className="whitespace-nowrap shrink-0">
            <BreadcrumbPage>Investigation</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    </div>
  );

  return (
    <div className="space-y-8 max-w-full">
      {investigationBreadcrumb}
      <header className="border-b border-slate-800 pb-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight break-words">
              Investigation Report
            </h1>
            <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
              <span className="text-slate-400">ID: <span className="text-slate-300 font-mono">{investigation.id.split('-')[0]}</span></span>
              <span className="text-slate-500 hidden sm:inline">&bull;</span>
              {renderStatusBadge(investigation.status)}
              <span className="text-slate-500 hidden sm:inline">&bull;</span>
              <span className="text-slate-400">
                Completed: {investigation.completed_at ? new Date(investigation.completed_at).toLocaleString() : 'N/A'}
              </span>
            </div>
          </div>
          <div className="flex-shrink-0">
             <Link 
              href={`/incidents/${incidentId}`}
              className="inline-flex items-center px-4 py-2 border border-slate-700 bg-transparent hover:bg-slate-800 text-slate-300 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 w-full sm:w-auto justify-center"
            >
              &larr; Back to Incident
            </Link>
          </div>
        </div>
      </header>

      {investigation.status === 'FAILED' && (
        <div role="alert" className="border border-red-500/20 bg-red-500/10 rounded-lg p-6">
          <h3 className="text-lg font-medium text-red-400 mb-2">Analysis Failed</h3>
          <p className="text-red-400/80 text-sm">
            The AI analysis encountered a problem and could not complete. Please return to the incident and try again.
          </p>
        </div>
      )}

      {investigation.status !== 'FAILED' && investigation.status !== 'COMPLETED' && (
        <div role="alert" className="border border-blue-500/20 bg-blue-500/10 rounded-lg p-6 text-center">
          <h3 className="text-lg font-medium text-blue-400 mb-2">Investigation In Progress</h3>
          <p className="text-blue-400/80 text-sm mb-4">
            The AI model is currently analyzing the evidence.
          </p>
          <div className="flex justify-center">
            <svg className="animate-spin h-8 w-8 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </div>
      )}

      {investigation.status === 'COMPLETED' && (
        <div className="space-y-6">
          <section className="bg-slate-900 border border-slate-800 rounded-lg p-5 sm:p-6">
            <h2 className="text-lg font-semibold text-slate-200 mb-3 border-b border-slate-800 pb-2">
              Summary
            </h2>
            <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed break-words">
              {investigation.summary || 'No summary available.'}
            </div>
          </section>

          <section className="bg-slate-900 border border-slate-800 rounded-lg p-5 sm:p-6">
            <h2 className="text-lg font-semibold text-slate-200 mb-3 border-b border-slate-800 pb-2">
              Root Cause
            </h2>
            <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed break-words">
              {investigation.root_cause || 'No root cause identified.'}
            </div>
          </section>

          <section className="bg-slate-900 border border-slate-800 rounded-lg p-5 sm:p-6">
            <h2 className="text-lg font-semibold text-slate-200 mb-3 border-b border-slate-800 pb-2">
              Recommendations
            </h2>
            <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed break-words">
              {investigation.recommendations || 'No recommendations provided.'}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
