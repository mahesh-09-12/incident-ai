import Link from 'next/link';
import { buttonVariants } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center px-4 space-y-8">
      <div className="space-y-4 max-w-2xl relative z-10">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-100 drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
          Incident<span className="neon-text">AI</span>
        </h1>
        <p className="text-lg sm:text-xl text-slate-400">
          AI-assisted incident investigation and root cause analysis platform. 
          Uncover insights from evidence instantly.
        </p>
      </div>

      <Link 
        href="/dashboard"
        className={buttonVariants({ size: "lg", variant: "default" }) + " cursor-pointer mt-8 relative z-10"}
      >
        Continue to Dashboard
        <ArrowRight className="ml-2 h-5 w-5" />
      </Link>
    </div>
  );
}
