"use client";

import React, { useState, useRef } from 'react';
import { useEvidenceList, useUploadEvidence, useDeleteEvidence } from '../hooks';
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

function formatBytes(bytes: number, decimals = 2) {
  if (!+bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

type FileStatus = 'pending' | 'uploading' | 'uploaded' | 'failed';

interface SelectedFile {
  id: string;
  file: File;
  status: FileStatus;
  error?: string;
}

export function EvidenceList({ incidentId }: { incidentId: string }) {
  const { data: evidenceList, isLoading, isError, error, refetch, isFetching } = useEvidenceList(incidentId);
  const uploadMutation = useUploadEvidence();
  const deleteMutation = useDeleteEvidence();
  
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [showAllEvidence, setShowAllEvidence] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).map(file => ({
        id: Math.random().toString(36).substring(7) + '-' + file.name,
        file,
        status: 'pending' as FileStatus,
      }));
      // Append new files to any existing pending/failed ones, drop uploaded ones
      setSelectedFiles(prev => [...prev.filter(f => f.status !== 'uploaded'), ...newFiles]);
      
      // Reset input so the same files can be selected again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const clearSelectedFiles = () => {
    setSelectedFiles([]);
  };

  const handleUpload = async () => {
    const filesToUpload = selectedFiles.filter(f => f.status === 'pending' || f.status === 'failed');
    if (filesToUpload.length === 0 || isUploading) return;
    
    setIsUploading(true);
    
    // Mark files as uploading
    setSelectedFiles(prev => prev.map(item => 
      filesToUpload.some(f => f.id === item.id) ? { ...item, status: 'uploading', error: undefined } : item
    ));
    
    const uploadPromises = filesToUpload.map(async (item) => {
      try {
        await uploadMutation.mutateAsync({ incidentId, file: item.file });
        setSelectedFiles(prev => prev.map(f => f.id === item.id ? { ...f, status: 'uploaded' } : f));
      } catch (err) {
        let errorMsg = 'Failed to upload';
        if (err instanceof Error) {
          if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
            errorMsg = 'Network error';
          } else {
            errorMsg = err.message;
          }
        }
        setSelectedFiles(prev => prev.map(f => f.id === item.id ? { ...f, status: 'failed', error: errorMsg } : f));
      }
    });

    await Promise.allSettled(uploadPromises);
    
    // Cleanup successfully uploaded files from the queue after a brief delay
    setTimeout(() => {
      setSelectedFiles(prev => prev.filter(f => f.status !== 'uploaded'));
    }, 2000);

    setIsUploading(false);
  };

  const handleDelete = async (evidenceId: string) => {
    setDeletingId(evidenceId);
    setDeleteError(null);
    try {
      await deleteMutation.mutateAsync({ incidentId, evidenceId });
    } catch (err) {
      let msg = 'Failed to delete evidence';
      if (err instanceof Error) {
        msg = err.message;
      }
      setDeleteError(msg);
    } finally {
      setDeletingId(null);
    }
  };

  // Render Error State for the List
  if (isError) {
    let errorMessage = 'An error occurred while loading evidence.';
    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Unable to connect to the server.';
      } else {
        errorMessage = error.message;
      }
    }

    return (
      <div role="alert" className="border border-red-500/20 bg-red-500/10 rounded-lg p-6 text-center w-full">
        <h3 className="text-lg font-medium text-red-400 mb-2">Failed to load evidence</h3>
        <p className="text-red-400/80 mb-4 text-sm break-words">{errorMessage}</p>
        <button 
          onClick={() => refetch()}
          disabled={isFetching}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50"
        >
          {isFetching ? 'Retrying...' : 'Retry'}
        </button>
      </div>
    );
  }

  // Handle Unexpected Data Format
  if (evidenceList !== undefined && !Array.isArray(evidenceList)) {
    return (
      <div role="alert" className="border border-amber-500/20 bg-amber-500/10 rounded-lg p-6 text-center w-full">
        <h3 className="text-lg font-medium text-amber-400 mb-2">Unexpected Data Format</h3>
        <p className="text-amber-400/80 mb-4 text-sm break-words">The server returned evidence data in an unexpected format.</p>
        <button 
          onClick={() => refetch()}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500"
        >
          Retry
        </button>
      </div>
    );
  }

  const hasPendingFiles = selectedFiles.some(f => f.status === 'pending' || f.status === 'failed');

  return (
    <div className="space-y-6 w-full max-w-full overflow-hidden">
      {/* Upload Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 sm:p-6 w-full">
        <h3 className="text-base font-medium text-slate-200 mb-4">Attach Evidence</h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="evidence-upload" className="sr-only">Select evidence files to upload</label>
            <input
              type="file"
              id="evidence-upload"
              multiple
              ref={fileInputRef}
              onChange={handleFileChange}
              disabled={isUploading}
              className="block w-full text-sm text-slate-400
                file:mr-4 file:py-2 file:px-4
                file:rounded file:border-0
                file:text-sm file:font-semibold
                file:bg-indigo-600/10 file:text-indigo-400
                hover:file:bg-indigo-600/20
                focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            />
          </div>

          {selectedFiles.length > 0 && (
            <div className="bg-slate-950 rounded border border-slate-800 p-3 max-h-60 overflow-y-auto">
              <h4 className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Upload Queue</h4>
              <ul className="space-y-2">
                {selectedFiles.map((item) => (
                  <li key={item.id} className="flex flex-col sm:flex-row sm:items-center justify-between text-sm gap-1 sm:gap-4 p-2 rounded bg-slate-900/50 border border-slate-800/50">
                    <div className="flex items-center min-w-0 flex-1">
                      <span className="text-slate-300 truncate mr-2 font-medium" title={item.file.name}>{item.file.name}</span>
                      <span className="text-slate-500 text-xs whitespace-nowrap flex-shrink-0">{formatBytes(item.file.size)}</span>
                    </div>
                    
                    <div className="flex-shrink-0 flex items-center">
                      {item.status === 'pending' && <span className="text-slate-500 text-xs font-medium px-2 py-1 bg-slate-800 rounded">Pending</span>}
                      {item.status === 'uploading' && <span className="text-blue-400 text-xs font-medium px-2 py-1 bg-blue-500/10 rounded flex items-center"><svg className="animate-spin -ml-1 mr-1.5 h-3 w-3 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Uploading</span>}
                      {item.status === 'uploaded' && <span className="text-emerald-400 text-xs font-medium px-2 py-1 bg-emerald-500/10 rounded">Uploaded</span>}
                      {item.status === 'failed' && (
                        <div className="flex flex-col items-end">
                          <span className="text-red-400 text-xs font-medium px-2 py-1 bg-red-500/10 rounded">Failed</span>
                          {item.error && <span className="text-red-400/80 text-[10px] mt-0.5 max-w-[120px] truncate" title={item.error}>{item.error}</span>}
                        </div>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex gap-2 justify-end">
            {selectedFiles.length > 0 && (
              <button
                type="button"
                onClick={clearSelectedFiles}
                disabled={isUploading}
                className="px-3 py-1.5 bg-transparent border border-slate-700 text-slate-300 rounded text-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50 transition-colors cursor-pointer"
              >
                Clear Queue
              </button>
            )}
            <button
              type="button"
              onClick={handleUpload}
              disabled={!hasPendingFiles || isUploading}
              aria-busy={isUploading}
              className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center cursor-pointer"
            >
              {isUploading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Uploading...
                </>
              ) : (
                'Upload Evidence'
              )}
            </button>
          </div>
        </div>
      </div>

      {deleteError && (
        <div role="alert" className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded p-3">
          {deleteError}
        </div>
      )}

      {/* List Section */}
      <div className="w-full">
        {isLoading ? (
          <div className="animate-pulse space-y-3" aria-busy="true">
            {[1, 2].map(i => (
              <div key={i} className="h-16 bg-slate-800 rounded w-full"></div>
            ))}
          </div>
        ) : !evidenceList || evidenceList.length === 0 ? (
          <div className="border border-slate-800 border-dashed rounded p-8 text-center w-full">
            <p className="text-slate-500 text-sm">No evidence attached to this incident yet.</p>
          </div>
        ) : (
          <>
            <ul className="space-y-3">
              {(showAllEvidence ? evidenceList : evidenceList.slice(0, 3)).map((evidence) => (
                <li key={evidence.id} className="bg-slate-900/50 border border-slate-800 rounded p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-200 truncate" title={evidence.filename}>
                      {evidence.filename}
                    </p>
                    <div className="mt-1 flex flex-wrap items-center gap-2 sm:gap-4 text-xs text-slate-500">
                      <span className="truncate">{evidence.content_type}</span>
                      <span className="hidden sm:inline">&bull;</span>
                      <span>{formatBytes(evidence.file_size)}</span>
                      <span className="hidden sm:inline">&bull;</span>
                      <span>{new Date(evidence.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0 flex justify-end">
                    <AlertDialog>
                      <AlertDialogTrigger
                        disabled={deletingId === evidence.id}
                        className="text-red-400 hover:text-red-300 hover:underline text-sm font-medium focus:outline-none focus:ring-2 focus:ring-red-500 rounded px-2 py-1 disabled:opacity-50 transition-colors cursor-pointer"
                        aria-label={`Delete ${evidence.filename}`}
                      >
                        {deletingId === evidence.id ? 'Deleting...' : 'Delete'}
                      </AlertDialogTrigger>
                      <AlertDialogContent className="bg-slate-900 border-slate-800">
                        <AlertDialogHeader>
                          <AlertDialogTitle className="text-slate-100">Delete Evidence</AlertDialogTitle>
                          <AlertDialogDescription className="text-slate-400">
                            Are you sure you want to delete {evidence.filename}? This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel className="bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700 hover:text-white focus:ring-slate-500">Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDelete(evidence.id)} className="bg-red-600 text-white hover:bg-red-700 focus:ring-red-500">Delete Evidence</AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </li>
              ))}
            </ul>
            {evidenceList.length > 3 && !showAllEvidence && (
              <button
                onClick={() => setShowAllEvidence(true)}
                className="mt-3 text-sm text-slate-300 hover:text-slate-200 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 rounded px-4 py-2 cursor-pointer w-full text-center border border-dashed border-slate-700 hover:bg-slate-800 bg-slate-900/50"
              >
                See all evidences
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
