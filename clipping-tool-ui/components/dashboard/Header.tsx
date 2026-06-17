import Link from "next/link";
import { Layers3, Server } from "lucide-react";
import { ClipAgentLogo } from "./ClipAgentLogo";
import { Button } from "@/components/ui/button";

const backendDocsUrl =
  process.env.MAIN_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
      <div className="container flex h-18 max-w-screen-2xl items-center justify-between gap-4 py-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="product-brand-shell">
            <ClipAgentLogo className="h-7 w-7" color="#2563eb" size={26} />
          </div>
          <div className="space-y-0.5">
            <span className="block text-lg font-semibold tracking-tight text-slate-950">
              ClipAgent
            </span>
            <span className="block text-xs uppercase tracking-[0.22em] text-slate-500">
              Clipping dashboard
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs uppercase tracking-[0.18em] text-slate-500 md:flex">
            <Layers3 className="h-3.5 w-3.5 text-sky-600" />
            Project based workflow
          </div>
          <Button
            asChild
            variant="outline"
            size="sm"
            className="rounded-full border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          >
            <a href={`${backendDocsUrl}/api/docs`} target="_blank" rel="noreferrer">
              <Server className="mr-2 h-4 w-4" />
              Backend API
            </a>
          </Button>
        </div>
      </div>
    </header>
  );
}
