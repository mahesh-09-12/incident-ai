"use client";

import React, { useState, useRef } from 'react';
import { useEvidenceList, useUploadEvidence, useDeleteEvidence } from '../hooks';

function formatBytes(bytes: number, decimals = 2) {
  if (!+bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export function EvidenceList({ incidentId }: { incidentId: string }) {
  const { data: evidenceList, isLoading, isError, error, refetch, isFetching } = useEvidenceList(incidentId);
  const uploadMutation = useUploadEvidence();
  const deleteMutation = useDeleteEvidence();
  
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadErrors, setUploadErrors] = useState<{ filename: string; error: string }[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
      setUploadErrors([]);
    }
  };

  const clearSelectedFiles = () => {
    setSelectedFiles([]);
    setUploadErrors([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0 || isUploading) return;
    
    setIsUploading(true);
    setUploadErrors([]);
    
    const results = await Promise.allSettled(
      selectedFiles.map(file => uploadMutation.mutateAsync({ incidentId, file }))
    );
    
    const errors: { filename: string; error: string }[] = [];
    const successfulFiles: string[] = [];
    
    results.forEach((result, index) => {
      const file = selectedFiles[index];
      if (result.status === 'rejected') {
        let errorMsg = 'Failed to upload';
        if (result.reason instanceof Error) {
          if (result.reason.message.includes('Failed to fetch') || result.reason.message.includes('NetworkError')) {
            errorMsg = 'Network error';
          } else {
            errorMsg = result.reason.message;
          }
        }
        errors.push({ filename: file.name, error: errorMsg });
      } else {
        successfulFiles.push(file.name);
      }
    });
    
    if (errors.length > 0) {
      setUploadErrors(errors);
      // Retain only the files that failed
      const remainingFiles = selectedFiles.filter(f => !successfulFiles.includes(f.name));
      setSelectedFiles(remainingFiles);
      
      // Update file input if possible (security restrictions prevent setting FileList directly, so we just clear it)
      if (remainingFiles.length === 0 && fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } else {
      clearSelectedFiles();
    }
    
    setIsUploading(false);
  };

  const handleDelete = async (evidenceId: string) => {
    if (confirm('Are you sure you want to delete this evidence?')) {
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
            <div className="bg-slate-950 rounded border border-slate-800 p-3 max-h-48 overflow-y-auto">
              <h4 className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Files to Upload</h4>
              <ul className="space-y-2">
                {selectedFiles.map((file, idx) => (
                  <li key={`${file.name}-${idx}`} className="flex justify-between items-center text-sm">
                    <span className="text-slate-300 truncate mr-2" title={file.name}>{file.name}</span>
                    <span className="text-slate-500 text-xs whitespace-nowrap flex-shrink-0">{formatBytes(file.size)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {uploadErrors.length > 0 && (
            <div role="alert" aria-live="assertive" className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded p-3">
              <p className="font-medium mb-1">Upload failed for some files:</p>
              <ul className="list-disc pl-5 space-y-1">
                {uploadErrors.map((err, idx) => (
                  <li key={idx} className="break-words">
                    <span className="font-semibold">{err.filename}</span>: {err.error}
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
                className="px-3 py-1.5 bg-transparent border border-slate-700 text-slate-300 rounded text-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50 transition-colors"
              >
                Clear
              </button>
            )}
            <button
              type="button"
              onClick={handleUpload}
              disabled={selectedFiles.length === 0 || isUploading}
              aria-busy={isUploading}
              className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
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
          <ul className="space-y-3">
            {evidenceList.map((evidence) => (
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
                  <button
                    onClick={() => handleDelete(evidence.id)}
                    disabled={deletingId === evidence.id}
                    className="text-red-400 hover:text-red-300 hover:underline text-sm font-medium focus:outline-none focus:ring-2 focus:ring-red-500 rounded px-2 py-1 disabled:opacity-50 transition-colors"
                    aria-label={`Delete ${evidence.filename}`}
                  >
                    {deletingId === evidence.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
