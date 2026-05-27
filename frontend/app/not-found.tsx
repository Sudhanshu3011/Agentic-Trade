"use client";

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-between bg-[var(--background)] px-6 py-12">
      {/* Spacer to push content down slightly, keeping it centered */}
      <div />

      <div className="max-w-md text-center">
        {/* Abstract design element / candlestick graphic representation */}
        <div className="mx-auto mb-8 flex h-16 w-20 items-end justify-center gap-1.5 opacity-80">
          <div className="relative w-1.5 h-12 bg-zinc-300 rounded-sm">
            <div className="absolute top-2 w-1.5 h-6 bg-[var(--foreground)] rounded-sm"></div>
          </div>
          <div className="relative w-1.5 h-16 bg-zinc-300 rounded-sm">
            <div className="absolute top-4 w-1.5 h-8 bg-[var(--foreground)] rounded-sm animate-pulse"></div>
          </div>
          <div className="relative w-1.5 h-10 bg-zinc-300 rounded-sm">
            <div className="absolute top-1 w-1.5 h-5 bg-[var(--foreground)] rounded-sm"></div>
          </div>
        </div>

        <p className="font-mono text-[12px] font-bold tracking-wider text-[var(--label)] uppercase">
          404 — PAGE NOT FOUND
        </p>
        
        <h1 className="mt-3 font-mono text-[24px] font-semibold tracking-tight text-[var(--foreground)]">
          Lost in the Data
        </h1>
        
        <p className="mt-4 text-[14px] leading-relaxed text-[var(--muted-foreground)]">
          The research path you requested does not exist or has been moved. Use the options below to return to safety.
        </p>

        <div className="mt-8 flex items-center justify-center gap-3">
          <Link
            href="/"
            className="inline-flex h-10 items-center justify-center border border-[var(--foreground)] bg-[var(--foreground)] px-5 font-mono text-[12px] text-white rounded-lg shadow-sm transition-all hover:bg-[#333330]"
          >
            ← Back to Home
          </Link>
          <Link
            href="/"
            className="inline-flex h-10 items-center justify-center border border-[var(--border)] bg-white px-5 font-mono text-[12px] text-[var(--foreground)] hover:border-[var(--foreground)] rounded-lg shadow-sm transition-all hover:bg-zinc-50"
          >
            New Analysis
          </Link>
        </div>
      </div>

      {/* Consistent Footer */}
      <div className="mt-12 flex flex-col items-center gap-3 w-full max-w-[240px]">
        <span className="font-mono text-[11px] tracking-wider text-[var(--muted-foreground)] opacity-75">
          MADE BY CONCEPTWORKSX
        </span>
        <div className="h-px w-full bg-[var(--border)]" />
        <a
          href="https://github.com/conceptworksx/Agentic-Trade-v2"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 font-mono text-[11px] tracking-wider text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
        >
          <svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
          <span>Contribute on Github</span>
        </a>
      </div>
    </div>
  );
}
