"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface SidebarProps {
  isMobileOpen: boolean;
  onCloseMobile: () => void;
}

const NAV_ITEMS = [
  { label: "Dashboard", href: "/" },
  { label: "Incidents", href: "/incidents" },
];

export function Sidebar({ isMobileOpen, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs md:hidden"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        id="app-sidebar"
        className={`fixed top-0 bottom-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800 bg-slate-950 text-slate-100 transition-transform duration-200 ease-in-out md:static md:translate-x-0 ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Main Navigation"
      >
        {/* Branding */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-5">
          <Link
            href="/"
            className="flex items-center gap-2.5 font-semibold text-slate-50 focus-visible:outline-2 focus-visible:outline-blue-500"
            onClick={onCloseMobile}
          >
            <span className="flex h-7 w-7 items-center justify-center rounded bg-blue-600 text-xs font-bold text-white shadow-xs">
              AI
            </span>
            <span className="text-base tracking-tight font-mono">IncidentAI</span>
          </Link>
          <button
            type="button"
            className="flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-slate-900 hover:text-slate-100 md:hidden"
            onClick={onCloseMobile}
            aria-label="Close menu"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Sidebar Navigation">
          <div className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
            Navigation
          </div>
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);

              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={onCloseMobile}
                    aria-current={isActive ? "page" : undefined}
                    className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-blue-500 ${
                      isActive
                        ? "bg-blue-950/70 text-blue-400 border border-blue-800/50"
                        : "text-slate-400 hover:bg-slate-900 hover:text-slate-100"
                    }`}
                  >
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer info / environment */}
        <div className="border-t border-slate-800 p-4 font-mono text-xs text-slate-500">
          <div>Env: Production</div>
          <div>Version: v0.1.0</div>
        </div>
      </aside>
    </>
  );
}
