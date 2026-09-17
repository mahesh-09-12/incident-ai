"use client";

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useUpdateIncident } from '../hooks';
import { Incident, IncidentUpdate } from '../types';

const incidentEditSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(255, 'Title must be 255 characters or less'),
  description: z.string().min(1, 'Description is required'),
  severity: z.string().min(1, 'Severity is required'),
  environment: z.string().min(1, 'Environment is required'),
  service: z
    .string()
    .min(1, 'Service is required')
    .max(100, 'Service must be 100 characters or less'),
  status: z.string().min(1, 'Status is required'),
});

type IncidentEditFormValues = z.infer<typeof incidentEditSchema>;

interface IncidentEditFormProps {
  incident: Incident;
  onCancel: () => void;
  onSuccess: () => void;
}

export function IncidentEditForm({ incident, onCancel, onSuccess }: IncidentEditFormProps) {
  const updateIncident = useUpdateIncident();
  const [globalError, setGlobalError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<IncidentEditFormValues>({
    resolver: zodResolver(incidentEditSchema),
    defaultValues: {
      title: incident.title,
      description: incident.description,
      severity: incident.severity,
      environment: incident.environment,
      service: incident.service,
      status: incident.status,
    },
  });

  const onSubmit = async (data: IncidentEditFormValues) => {
    setGlobalError(null);
    try {
      await updateIncident.mutateAsync({ id: incident.id, data: data as IncidentUpdate });
      onSuccess();
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          setGlobalError('Unable to connect to the server. Please check your internet connection and try again.');
        } else if (error.name === 'ApiError') {
          setGlobalError(error.message || 'An error occurred while updating the incident on the server.');
        } else {
          setGlobalError(error.message || 'An unexpected error occurred.');
        }
      } else {
        setGlobalError('An unexpected error occurred while updating the incident.');
      }
    }
  };

  const inputClasses = "w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:cursor-not-allowed disabled:opacity-50";
  const labelClasses = "block text-sm font-medium text-slate-300 mb-1.5";
  const errorClasses = "mt-1.5 text-sm text-red-400";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 w-full max-w-full" noValidate>
      {globalError && (
        <div 
          role="alert" 
          aria-live="assertive"
          className="rounded-md border border-red-500/20 bg-red-500/10 p-4"
        >
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-400">Update Error</h3>
              <div className="mt-1 text-sm text-red-400/80">
                {globalError}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label htmlFor="title" className={labelClasses}>
            Title
          </label>
          <input
            type="text"
            id="title"
            {...register('title')}
            disabled={isSubmitting}
            aria-invalid={!!errors.title}
            aria-describedby={errors.title ? "title-error" : undefined}
            className={inputClasses}
            placeholder="e.g., Database connection timeout in eu-west-1"
          />
          {errors.title && (
            <p id="title-error" className={errorClasses} role="alert">
              {errors.title.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="description" className={labelClasses}>
            Description
          </label>
          <textarea
            id="description"
            rows={4}
            {...register('description')}
            disabled={isSubmitting}
            aria-invalid={!!errors.description}
            aria-describedby={errors.description ? "description-error" : undefined}
            className={inputClasses}
            placeholder="Provide a detailed description of the incident..."
          />
          {errors.description && (
            <p id="description-error" className={errorClasses} role="alert">
              {errors.description.message}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="status" className={labelClasses}>
              Status
            </label>
            <select
              id="status"
              {...register('status')}
              disabled={isSubmitting}
              aria-invalid={!!errors.status}
              aria-describedby={errors.status ? "status-error" : undefined}
              className={inputClasses}
            >
              <option value="Open">Open</option>
              <option value="Investigating">Investigating</option>
              <option value="Identified">Identified</option>
              <option value="Monitoring">Monitoring</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>
            {errors.status && (
              <p id="status-error" className={errorClasses} role="alert">
                {errors.status.message}
              </p>
            )}
          </div>
          <div>
            <label htmlFor="severity" className={labelClasses}>
              Severity
            </label>
            <select
              id="severity"
              {...register('severity')}
              disabled={isSubmitting}
              aria-invalid={!!errors.severity}
              aria-describedby={errors.severity ? "severity-error" : undefined}
              className={inputClasses}
            >
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
            {errors.severity && (
              <p id="severity-error" className={errorClasses} role="alert">
                {errors.severity.message}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="environment" className={labelClasses}>
              Environment
            </label>
            <select
              id="environment"
              {...register('environment')}
              disabled={isSubmitting}
              aria-invalid={!!errors.environment}
              aria-describedby={errors.environment ? "environment-error" : undefined}
              className={inputClasses}
            >
              <option value="Production">Production</option>
              <option value="Staging">Staging</option>
              <option value="Development">Development</option>
            </select>
            {errors.environment && (
              <p id="environment-error" className={errorClasses} role="alert">
                {errors.environment.message}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="service" className={labelClasses}>
              Service
            </label>
            <input
              type="text"
              id="service"
              {...register('service')}
              disabled={isSubmitting}
              aria-invalid={!!errors.service}
              aria-describedby={errors.service ? "service-error" : undefined}
              className={inputClasses}
              placeholder="e.g., authentication-api"
            />
            {errors.service && (
              <p id="service-error" className={errorClasses} role="alert">
                {errors.service.message}
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end border-t border-slate-800 pt-5">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="inline-flex justify-center rounded-md border border-slate-700 bg-transparent px-4 py-2 text-sm font-medium text-slate-300 shadow-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-slate-950 transition-colors w-full sm:w-auto"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50 transition-colors w-full sm:w-auto items-center"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Updating...
            </>
          ) : (
            'Save Changes'
          )}
        </button>
      </div>
    </form>
  );
}
