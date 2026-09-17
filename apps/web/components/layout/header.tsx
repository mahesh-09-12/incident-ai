"use client";

import { usePathname } from "next/navigation";

interface HeaderProps {
  isMobileOpen: boolean;
  onToggleMobile: () => void;
}

const ROUTE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/incidents": "Incidents",
  "/incidents/new": "Create Incident",
};

export function Header({ isMobileOpen, onToggleMobile }: HeaderProps) {
  const pathname = usePathname();

  // Compute title dynamically based on route prefix
  let pageTitle = ROUTE_TITLES[pathname] || "Incident Management";
  if (pathname.startsWith("/incidents/") && pathname !== "/incidents/new") {
    pageTitle = "Incident Details";
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-800 bg-slate-950/80 px-4 backdrop-blur-md sm:px-6">
      <div className="flex items-center gap-3">
        {/* Mobile menu toggle */}
        <button
          type="button"
          className="flex h-9 w-9 items-center justify-center rounded-md border border-slate-800 text-slate-400 hover:bg-slate-900 hover:text-slate-100 focus-visible:outline-2 focus-visible:outline-blue-500 md:hidden"
          onClick={onToggleMobile}
          aria-expanded={isMobileOpen}
          aria-controls="app-sidebar"
          aria-label="Toggle navigation menu"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <h1 className="text-lg font-semibold text-slate-100 tracking-tight">
          {pageTitle}
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Placeholder for future header actions */}
      </div>
    </header>
  );
}
