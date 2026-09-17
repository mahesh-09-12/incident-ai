import React from 'react';
import Link from 'next/link';
import { IncidentList } from '@/features/incidents/components/incident-list';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

export default function IncidentsPage() {
  return (
    <div className="w-full max-w-5xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link href="/">Home</Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Incidents</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </div>

      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight">Incidents</h1>
          <p className="text-sm sm:text-base text-slate-400 mt-1">
            Active incident investigation workspace
          </p>
        </div>
        <div className="flex-shrink-0">
          <Link 
            href="/incidents/new"
            className="inline-flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950 shadow-sm"
          >
            Create Incident
          </Link>
        </div>
      </header>
      
      <main>
        <IncidentList />
      </main>
    </div>
  );
}
