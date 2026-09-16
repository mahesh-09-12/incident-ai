import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-xl font-bold text-slate-100 font-mono tracking-tight">
          IncidentAI Overview
        </h2>
        <p className="mt-1 text-sm text-slate-400 max-w-2xl">
          AI-assisted incident investigation system. Connects evidence files with Qwen3:4B via Ollama to generate structured root cause analysis and recommendations.
        </p>
      </div>

      {/* Quick Navigation Panel */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/30 p-5">
          <h3 className="text-sm font-semibold font-mono text-slate-200">
            Incidents Management
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            View active production incidents, create new incident records, and attach evidence.
          </p>
          <div className="mt-4">
            <Link
              href="/incidents"
              className="inline-flex items-center gap-2 text-xs font-mono font-medium text-blue-400 hover:text-blue-300 focus-visible:outline-2 focus-visible:outline-blue-500"
            >
              <span>Go to Incidents &rarr;</span>
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/30 p-5">
          <h3 className="text-sm font-semibold font-mono text-slate-200">
            System Workflow
          </h3>
          <ol className="mt-2 space-y-1 text-xs text-slate-400 list-decimal list-inside font-mono">
            <li>Create Incident record</li>
            <li>Upload log/trace evidence</li>
            <li>Trigger AI investigation</li>
            <li>Review root cause & recommendations</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
