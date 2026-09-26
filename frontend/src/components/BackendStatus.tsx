'use client';

import { useEffect, useState } from 'react';
import { AtlasApiClient } from '@/lib/api';

type BackendState = {
  health: string;
  readiness: string;
  constitutionVersion: string;
  error: string | null;
};

export default function BackendStatus() {
  const [state, setState] = useState<BackendState>({
    health: 'Checking',
    readiness: 'Checking',
    constitutionVersion: '--',
    error: null,
  });

  useEffect(() => {
    const loadStatus = async () => {
      const api = new AtlasApiClient();

      try {
        const [health, ready] = await Promise.all([
          api.health(),
          api.ready(),
        ]);

        setState({
          health: health.status,
          readiness: ready.status,
          constitutionVersion:
            ready.constitution_version,
          error: null,
        });
      } catch (error) {
        setState({
          health: 'Unavailable',
          readiness: 'Unavailable',
          constitutionVersion: '--',
          error:
            error instanceof Error
              ? error.message
              : String(error),
        });
      }
    };

    void loadStatus();
  }, []);

  const healthy =
    state.health.toLowerCase() === 'ok' &&
    state.readiness.toLowerCase() === 'ready';

  return (
    <div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-800 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Backend
          </p>

          <div className="mt-3 flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                healthy
                  ? 'bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.7)]'
                  : 'bg-rose-400 shadow-[0_0_12px_rgba(251,113,133,0.6)]'
              }`}
            />

            <span className="font-medium text-white">
              {state.health}
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Readiness
          </p>

          <p className="mt-3 font-medium text-white">
            {state.readiness}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Constitution
          </p>

          <p className="mt-3 font-medium text-cyan-300">
            {state.constitutionVersion}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/45 p-4">
          <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Authority Model
          </p>

          <p className="mt-3 font-medium text-emerald-300">
            Human Final
          </p>
        </div>
      </div>

      {state.error && (
        <div className="mt-3 rounded-xl border border-rose-400/20 bg-rose-400/5 px-4 py-3">
          <p className="text-xs text-rose-300">
            Backend connection error: {state.error}
          </p>
        </div>
      )}
    </div>
  );
}