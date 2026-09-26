"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useInvestigation } from '../hooks';
import { Investigation, EvidenceReference } from '../types';
import { useIncident } from '@/features/incidents/hooks';
import { EvidenceViewerDialog } from '@/features/evidence/components/evidence-viewer-dialog';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, FileX } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";

export function InvestigationResult({ incidentId, investigationId }: { incidentId: string; investigationId: string }) {
  const { data: investigation, isLoading, isError, error, refetch } = useInvestigation(incidentId, investigationId);
  const { data: incident } = useIncident(incidentId);

  const [selectedEvidence, setSelectedEvidence] = useState<{ id: string; filename: string } | null>(null);

  const handleEvidenceClick = (id: string, filename: string) => {
    setSelectedEvidence({ id, filename });
  };

  const handleCloseDialog = (open: boolean) => {
    if (!open) setSelectedEvidence(null);
  };

  if (isLoading) {
    return (
      <div className="space-y-6" aria-busy="true">
        <Skeleton className="h-8 w-1/3 bg-slate-800" />
        <Skeleton className="h-4 w-1/4 bg-slate-800" />
        <div className="space-y-4 mt-8">
          <Skeleton className="h-6 w-1/4 bg-slate-800" />
          <Skeleton className="h-24 w-full bg-slate-800" />
        </div>
        <div className="space-y-4 mt-6">
          <Skeleton className="h-6 w-1/4 bg-slate-800" />
          <Skeleton className="h-24 w-full bg-slate-800" />
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
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 cursor-pointer"
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
        return <Badge className="bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border-emerald-500/20">Completed</Badge>;
      case 'FAILED':
        return <Badge variant="destructive">Failed</Badge>;
      case 'RUNNING':
        return <Badge className="bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 border-blue-500/20">Running</Badge>;
      case 'PENDING':
        return <Badge variant="secondary">Pending</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const renderEvidenceList = (evidenceList: EvidenceReference[] | null | undefined, emptyMessage: string) => {
    if (!evidenceList || evidenceList.length === 0) {
      return <p className="text-slate-400 italic text-sm">{emptyMessage}</p>;
    }
    return (
      <ul className="space-y-4">
        {evidenceList.map((item, idx) => (
          <li key={idx} className="bg-slate-950 border border-slate-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              <button
                onClick={() => handleEvidenceClick(item.evidence_id, item.filename)}
                className="text-sm font-medium text-blue-400 hover:underline hover:text-blue-300 text-left cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1 -mx-1"
                aria-label={`View evidence ${item.filename}`}
              >
                {item.filename || 'Unknown File'}
              </button>
              <span className="text-xs text-slate-500 font-mono ml-2 hidden sm:inline-block truncate">
                {item.evidence_id}
              </span>
            </div>
            <div className="text-sm text-slate-300 leading-relaxed pl-6">
              {item.explanation}
            </div>
          </li>
        ))}
      </ul>
    );
  };

  const renderMissingEvidence = (missingEvidenceList: string[] | null | undefined, emptyMessage: string) => {
    if (!missingEvidenceList || missingEvidenceList.length === 0) {
      return <p className="text-slate-400 italic text-sm">{emptyMessage}</p>;
    }
    return (
      <ul className="space-y-3">
        {missingEvidenceList.map((item, idx) => (
          <li key={idx} className="flex gap-3 bg-slate-950 border border-slate-800 rounded-md p-4">
            <FileX className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-slate-300 leading-relaxed">{item}</span>
          </li>
        ))}
      </ul>
    );
  };

  const incidentTitle = incident?.title || 'Loading...';

  const investigationBreadcrumb = (
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
          <Alert className="bg-indigo-500/10 text-indigo-200 border-indigo-500/20">
            <AlertTitle className="text-indigo-400 font-semibold">AI-Generated Analysis</AlertTitle>
            <AlertDescription className="text-indigo-200/80 mt-2">
              This investigation report was generated automatically by an AI model based on the provided evidence. 
              Please review and verify these conclusions carefully, as AI analysis may be incomplete or inaccurate and should not be treated as guaranteed fact.
            </AlertDescription>
          </Alert>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg text-slate-200">Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed break-words">
                {investigation.summary || 'No summary available.'}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg text-slate-200">Most Supported Hypothesis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed break-words">
                {investigation.root_cause || 'No root cause identified.'}
              </div>
            </CardContent>
          </Card>

          {investigation.hypotheses && investigation.hypotheses.length > 0 ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-lg text-slate-200">Investigation Hypotheses</CardTitle>
              </CardHeader>
              <CardContent>
                <Accordion className="w-full space-y-4">
                  {investigation.hypotheses.map((hyp, index) => {
                    const isRootCauseMatch = investigation.root_cause?.includes(hyp.id) || investigation.root_cause?.includes(hyp.hypothesis);
                    
                    return (
                      <AccordionItem key={hyp.id || index} value={`hyp-${index}`} className="border border-slate-800 rounded-lg bg-slate-900 overflow-hidden px-4">
                        <AccordionTrigger className="hover:no-underline py-4 text-left">
                          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 w-full pr-4">
                            <span className="font-semibold text-slate-200 text-sm sm:text-base">
                              {hyp.id}: {hyp.hypothesis}
                            </span>
                            {isRootCauseMatch && (
                              <Badge className="w-fit bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shrink-0">
                                Most Supported
                              </Badge>
                            )}
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="pt-2 pb-6 space-y-6">
                          <div>
                            <h4 className="text-sm font-semibold text-slate-300 mb-2">Reasoning</h4>
                            <p className="text-sm text-slate-400 leading-relaxed whitespace-pre-wrap break-words bg-slate-950 p-4 rounded-md border border-slate-800">
                              {hyp.reasoning || 'No reasoning provided.'}
                            </p>
                          </div>

                          <Separator className="bg-slate-800" />
                          
                          <div>
                            <h4 className="text-sm font-semibold text-slate-300 mb-3">Supporting Evidence</h4>
                            {renderEvidenceList(hyp.supporting_evidence, "No supporting evidence provided for this hypothesis.")}
                          </div>

                          <Separator className="bg-slate-800" />
                          
                          <div>
                            <h4 className="text-sm font-semibold text-slate-300 mb-3">Contradicting Evidence</h4>
                            {renderEvidenceList(hyp.contradicting_evidence, "No contradicting evidence found for this hypothesis.")}
                          </div>

                          <Separator className="bg-slate-800" />
                          
                          <div>
                            <h4 className="text-sm font-semibold text-slate-300 mb-3">Missing Evidence</h4>
                            {renderMissingEvidence(hyp.missing_evidence, "No missing evidence identified for this hypothesis.")}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    );
                  })}
                </Accordion>
              </CardContent>
            </Card>
          ) : (
            // Backward compatibility for legacy investigations
            <>
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-200">Supporting Evidence</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderEvidenceList(investigation.supporting_evidence, "No supporting evidence provided.")}
                </CardContent>
              </Card>
              
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-200">Contradicting Evidence</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderEvidenceList(investigation.contradicting_evidence, "No contradicting evidence found.")}
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-200">Missing Evidence / What to Investigate Next</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderMissingEvidence(investigation.missing_evidence, "No missing evidence identified.")}
                </CardContent>
              </Card>
            </>
          )}

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg text-slate-200">Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed break-words">
                {investigation.recommendations || 'No recommendations provided.'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <EvidenceViewerDialog
        incidentId={incidentId}
        evidenceId={selectedEvidence?.id || null}
        filename={selectedEvidence?.filename || null}
        isOpen={!!selectedEvidence}
        onOpenChange={handleCloseDialog}
      />
    </div>
  );
}
