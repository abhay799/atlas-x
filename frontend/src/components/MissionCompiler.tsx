'use client';

import { useState } from 'react';
import { AtlasApiClient } from '@/lib/api';
import { Mission } from '@/types';

export default function MissionCompiler() {
  const [loading, setLoading] = useState(false);
  const [mission, setMission] = useState<Mission | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [objective, setObjective] = useState('');
  const [constraints, setConstraints] = useState<string[]>([]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    setLoading(true);
    setError(null);
    setMission(null);

    const api = new AtlasApiClient();

    try {
      const compiledMission = await api.compileMission(
        objective,
        constraints,
      );

      setMission(compiledMission);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : String(err),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div className="grid gap-6 xl:grid-cols-[1fr_1.1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-5">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-400">
                Mission Definition
              </p>

              <h3 className="mt-2 text-lg font-semibold text-white">
                Define governed objective
              </h3>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                Provide the mission objective and operational constraints.
              </p>
            </div>

            <div className="rounded-xl border border-blue-400/15 bg-blue-400/5 px-3 py-2 text-xs text-blue-300">
              Compiler
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >
            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label className="text-sm font-medium text-slate-300">
                  Mission Objective
                </label>

                <span className="text-xs text-slate-600">
                  Required
                </span>
              </div>

              <textarea
                value={objective}
                onChange={(event) =>
                  setObjective(event.target.value)
                }
                rows={5}
                required
                minLength={5}
                placeholder="Example: Analyze public infrastructure telemetry and identify operational anomalies."
                className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm leading-6 text-white placeholder:text-slate-600"
              />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label className="text-sm font-medium text-slate-300">
                  Governance Constraints
                </label>

                <span className="text-xs text-slate-600">
                  One per line
                </span>
              </div>

              <textarea
                value={constraints.join('\n')}
                onChange={(event) =>
                  setConstraints(
                    event.target.value
                      .split('\n')
                      .map((value) =>
                        value.trim(),
                      )
                      .filter(Boolean),
                  )
                }
                rows={5}
                placeholder={`read_only\nno_personal_data\nhuman_approval_if_sensitive`}
                className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-3 font-mono text-sm leading-6 text-white placeholder:text-slate-700"
              />

              <div className="mt-3 flex flex-wrap gap-2">
                {constraints.length > 0 ? (
                  constraints.map((constraint) => (
                    <span
                      key={constraint}
                      className="rounded-full border border-slate-700 bg-slate-900/80 px-2.5 py-1 text-[11px] text-slate-400"
                    >
                      {constraint}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-600">
                    No constraints currently defined.
                  </span>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`atlas-primary-button w-full rounded-xl px-4 py-3 text-sm font-semibold ${
                loading
                  ? 'cursor-not-allowed opacity-50'
                  : ''
              }`}
            >
              {loading
                ? 'Compiling Mission...'
                : 'Compile Governed Mission'}
            </button>
          </form>

          {error && (
            <div className="mt-4 rounded-xl border border-rose-400/20 bg-rose-400/5 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-rose-400">
                Compilation Error
              </p>

              <p className="mt-2 text-sm text-rose-300">
                {error}
              </p>
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-5">
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-400">
                Compilation Output
              </p>

              <h3 className="mt-2 text-lg font-semibold text-white">
                Governed mission structure
              </h3>
            </div>

            <div
              className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${
                mission
                  ? 'border-emerald-400/20 bg-emerald-400/5 text-emerald-300'
                  : 'border-slate-700 bg-slate-900/70 text-slate-500'
              }`}
            >
              {mission ? 'COMPILED' : 'WAITING'}
            </div>
          </div>

          {!mission ? (
            <div className="flex min-h-[360px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 bg-slate-950/30 px-6 text-center">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-slate-700 bg-slate-900 text-lg text-slate-500">
                MX
              </div>

              <p className="font-medium text-slate-300">
                No mission compiled
              </p>

              <p className="mt-2 max-w-sm text-sm leading-6 text-slate-600">
                Define an objective and compile it to inspect mission identity,
                tasks, authority limits, constraints, and governance metadata.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/5 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
                      Mission ID
                    </p>

                    <p className="mt-1 break-all font-mono text-sm text-emerald-300">
                      {mission.mission_id}
                    </p>
                  </div>

                  <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                    {mission.status}
                  </span>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-600">
                    Tasks
                  </p>

                  <p className="mt-2 text-xl font-semibold text-white">
                    {mission.tasks.length}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-600">
                    Authority Ceiling
                  </p>

                  <p className="mt-2 text-xl font-semibold text-cyan-300">
                    L{mission.authority_ceiling}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-600">
                    Human Approval
                  </p>

                  <p
                    className={`mt-2 text-sm font-semibold ${
                      mission.human_approval_required
                        ? 'text-amber-300'
                        : 'text-emerald-300'
                    }`}
                  >
                    {mission.human_approval_required
                      ? 'Required'
                      : 'Not Required'}
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                  Objective
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {mission.objective}
                </p>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                  Constraints
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {mission.constraints.length > 0 ? (
                    mission.constraints.map(
                      (constraint) => (
                        <span
                          key={constraint}
                          className="rounded-full border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-400"
                        >
                          {constraint}
                        </span>
                      ),
                    )
                  ) : (
                    <span className="text-sm text-slate-600">
                      None
                    </span>
                  )}
                </div>
              </div>

              {mission.tasks.length > 0 && (
                <div>
                  <div className="mb-3 flex items-center justify-between">
                    <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                      Mission Tasks
                    </p>

                    <span className="text-xs text-slate-600">
                      {mission.tasks.length} total
                    </span>
                  </div>

                  <div className="space-y-3">
                    {mission.tasks.map(
                      (task, index) => (
                        <div
                          key={task.task_id}
                          className="rounded-xl border border-slate-800 bg-slate-950/50 p-4"
                        >
                          <div className="flex items-start gap-3">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-blue-400/15 bg-blue-400/5 text-xs font-semibold text-blue-300">
                              {index + 1}
                            </div>

                            <div className="min-w-0">
                              <p className="font-medium text-white">
                                {task.title}
                              </p>

                              <p className="mt-1 break-all font-mono text-xs text-slate-600">
                                {task.task_id}
                              </p>

                              <div className="mt-3 flex flex-wrap gap-2">
                                <span className="rounded-full border border-cyan-400/15 bg-cyan-400/5 px-2.5 py-1 text-[11px] text-cyan-300">
                                  Authority L
                                  {
                                    task.authority_required
                                  }
                                </span>

                                <span className="rounded-full border border-slate-700 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-400">
                                  {task.status}
                                </span>
                              </div>

                              {task.dependencies.length >
                                0 && (
                                <p className="mt-3 text-xs leading-5 text-slate-500">
                                  Depends on:{' '}
                                  {task.dependencies.join(
                                    ', ',
                                  )}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                </div>
              )}

              <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
                  <span className="text-slate-600">
                    Constitution
                  </span>

                  <span className="font-mono text-slate-400">
                    {mission.constitution_version}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}