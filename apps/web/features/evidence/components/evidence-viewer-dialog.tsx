import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useEvidenceContent } from '../hooks';
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { FileText, FileWarning } from 'lucide-react';

interface EvidenceViewerDialogProps {
  incidentId: string;
  evidenceId: string | null;
  filename: string | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EvidenceViewerDialog({
  incidentId,
  evidenceId,
  filename,
  isOpen,
  onOpenChange,
}: EvidenceViewerDialogProps) {
  // Only fetch content if the dialog is open and we have a valid evidenceId
  const shouldFetch = isOpen && !!evidenceId;
  const { data, isLoading, isError, error } = useEvidenceContent(
    incidentId,
    evidenceId || '',
    shouldFetch
  );

  let errorMsg = 'Failed to load evidence content.';
  if (isError && error instanceof Error) {
    if (error.message.includes('Evidence content not found')) {
      errorMsg = 'The physical evidence file was not found or has been deleted.';
    } else {
      errorMsg = error.message;
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col bg-slate-900 border-slate-800 text-slate-200">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 truncate">
            <FileText className="w-5 h-5 text-indigo-400 flex-shrink-0" />
            <span className="truncate">{filename || 'Evidence Document'}</span>
          </DialogTitle>
          <DialogDescription className="text-slate-400 truncate">
            {evidenceId ? `ID: ${evidenceId}` : ''}
            {data && ` • Type: ${data.contentType}`}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 min-h-[200px] mt-4 relative overflow-hidden flex flex-col">
          {isLoading && (
            <div className="space-y-4">
              <Skeleton className="h-4 w-full bg-slate-800" />
              <Skeleton className="h-4 w-5/6 bg-slate-800" />
              <Skeleton className="h-4 w-4/6 bg-slate-800" />
              <Skeleton className="h-4 w-full bg-slate-800" />
            </div>
          )}

          {isError && (
            <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400">
              <FileWarning className="h-4 w-4" />
              <AlertTitle>Error Loading Evidence</AlertTitle>
              <AlertDescription>{errorMsg}</AlertDescription>
            </Alert>
          )}

          {data && (
            data.isText ? (
              <ScrollArea className="flex-1 border border-slate-800 rounded-md bg-slate-950 p-4">
                {data.text ? (
                  <pre className="text-xs sm:text-sm font-mono text-slate-300 whitespace-pre-wrap break-words leading-relaxed">
                    {data.text}
                  </pre>
                ) : (
                  <p className="text-slate-500 italic text-sm text-center pt-8">File is empty.</p>
                )}
              </ScrollArea>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center border border-slate-800 rounded-md bg-slate-950 p-8 text-center">
                <FileWarning className="w-12 h-12 text-amber-500/50 mb-4" />
                <p className="text-slate-300 font-medium mb-2">Binary or Unsupported Format</p>
                <p className="text-sm text-slate-500 mb-6">
                  This file type ({data.contentType}) cannot be displayed as text.
                </p>
                {/* To provide a seamless download behavior we could use a link, but keeping it simple for the viewer */}
              </div>
            )
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
