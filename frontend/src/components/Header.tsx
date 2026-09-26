'use client';

export default function Header() {
  return (
    <header className="mb-6">
      <div className="flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-950/45 px-5 py-4 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 shadow-[0_0_24px_rgba(56,189,248,0.12)]">
            <span className="text-sm font-bold tracking-[0.2em] text-cyan-300">
              AX
            </span>
          </div>

          <div>
            <p className="text-sm font-semibold tracking-wide text-white">
              ATLAS X
            </p>

            <p className="text-xs text-slate-500">
              Governance & Mission Control Fabric
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-medium text-emerald-300">
            <span className="atlas-status-dot" />
            System Online
          </div>

          <div className="rounded-full border border-slate-700/70 bg-slate-900/70 px-3 py-1.5 text-xs text-slate-400">
            Human Authority Final
          </div>
        </div>
      </div>
    </header>
  );
}