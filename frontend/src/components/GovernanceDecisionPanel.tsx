'use client';

import { useState } from 'react';
import { AtlasApiClient } from '@/lib/api';
import {
  DecisionOutcome,
  GovernanceDecision,
} from '@/types';

export default function GovernanceDecisionPanel() {
  const [loading, setLoading] = useState(false);
  const [decision, setDecision] =
    useState<GovernanceDecision | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [missionId, setMissionId] = useState('');
  const [taskId, setTaskId] = useState('');
  const [agentId, setAgentId] = useState('');

  const handleEvaluate = async (
    event: React.FormEvent,
  ) => {
    event.preventDefault();

    setLoading(true);
    setError(null);
    setDecision(null);

    const api = new AtlasApiClient();

    try {
      const governanceDecision =
        await api.evaluateGovernance(
          missionId,
          taskId,
          agentId || undefined,
        );

      setDecision(governanceDecision);
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

  const getOutcomeMeta = (
    outcome: DecisionOutcome,
  ) => {
    switch (outcome) {
      case DecisionOutcome.ALLOW:
        return {
          label: 'ALLOW',
          subtitle:
            'Governance checks passed for this action.',
          panelClass:
            'atlas-decision-allow',
          badgeClass:
            'border-emerald-400/25 bg-emerald-400/10 text-emerald-300',
          valueClass: 'text-emerald-300',
          icon: '✓',
        };

      case DecisionOutcome.REQUIRE_HUMAN_APPROVAL:
        return {
          label: 'REQUIRE HUMAN APPROVAL',
          subtitle:
            'Execution is paused pending authorized human review.',
          panelClass:
            'atlas-decision-approval',
          badgeClass:
            'border-amber-400/25 bg-amber-400/10 text-amber-300',
          valueClass: 'text-amber-300',
          icon: '!',
        };

      case DecisionOutcome.BLOCK:
        return {
          label: 'BLOCK',
          subtitle:
            'Governance policy prevents this action from proceeding.',
          panelClass:
            'atlas-decision-block',
          badgeClass:
            'border-rose-400/25 bg-rose-400/10 text-rose-300',
          valueClass: 'text-rose-300',
          icon: '×',
        };

      default:
        return {
          label: outcome,
          subtitle: 'Governance decision returned.',
          panelClass: '',
          badgeClass:
            'border-slate-600 bg-slate-800 text-slate-300',
          valueClass: 'text-slate-300',
          icon: '?',
        };
    }
  };

  const meta = decision
    ? getOutcomeMeta(decision.outcome)
    : null;

  return (
    <section>
      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-5">
          <div className="mb-5">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-400">
              Evaluation Request
            </p>

            <h3 className="mt-2 text-lg font-semibold text-white">
              Evaluate governed action
            </h3>

            <p className="mt-1 text-sm leading-6 text-slate-500">
              Submit mission, task, and optional agent identity to the
              governance gateway.
            </p>
          </div>

          <form
            onSubmit={handleEvaluate}
            className="space-y-5"
          >
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Mission ID
              </label>

              <input
                value={missionId}
                onChange={(event) =>
                  setMissionId(event.target.value)
                }
                type="text"
                placeholder="mission_..."
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-3 font-mono text-sm text-white placeholder:text-slate-700"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Task ID
              </label>

              <input
                value={taskId}
                onChange={(event) =>
                  setTaskId(event.target.value)
                }
                type="text"
                placeholder="task_..."
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-3 font-mono text-sm text-white placeholder:text-slate-700"
              />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label className="text-sm font-medium text-slate-300">
                  Agent ID
                </label>

                <span className="text-xs text-slate-600">
                  Optional
                </span>
              </div>

              <input
                value={agentId}
                onChange={(event) =>
                  setAgentId(event.target.value)
                }
                type="text"
                placeholder="agent_..."
                className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-3 font-mono text-sm text-white placeholder:text-slate-700"
              />
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
                ? 'Evaluating Governance...'
                : 'Run Governance Evaluation'}
            </button>
          </form>

          {error && (
            <div className="mt-4 rounded-xl border border-rose-400/20 bg-rose-400/5 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-rose-400">
                Evaluation Error
              </p>

              <p className="mt-2 text-sm leading-6 text-rose-300">
                {error}
              </p>
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-5">
          <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-400">
                Governance Verdict
              </p>

              <h3 className="mt-2 text-lg font-semibold text-white">
                Decision outcome
              </h3>
            </div>

            <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-500">
              Human authority remains final
            </span>
          </div>

          {!decision || !meta ? (
            <div className="flex min-h-[430px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 bg-slate-950/30 px-6 text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-blue-400/15 bg-blue-400/5 text-lg font-semibold text-blue-300">
                GX
              </div>

              <p className="font-medium text-slate-300">
                Awaiting governance evaluation
              </p>

              <p className="mt-2 max-w-sm text-sm leading-6 text-slate-600">
                Provide a mission and task identifier to evaluate policy,
                authority, and governance requirements.
              </p>

              <div className="mt-6 grid w-full max-w-md grid-cols-3 gap-2">
                <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/5 px-3 py-3">
                  <p className="text-[10px] uppercase tracking-[0.14em] text-emerald-400">
                    Allow
                  </p>
                </div>

                <div className="rounded-xl border border-amber-400/15 bg-amber-400/5 px-3 py-3">
                  <p className="text-[10px] uppercase tracking-[0.14em] text-amber-400">
                    Review
                  </p>
                </div>

                <div className="rounded-xl border border-rose-400/15 bg-rose-400/5 px-3 py-3">
                  <p className="text-[10px] uppercase tracking-[0.14em] text-rose-400">
                    Block
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div
                className={`rounded-2xl border p-5 ${meta.panelClass}`}
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border text-xl font-bold ${meta.badgeClass}`}
                    >
                      {meta.icon}
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                        Governance Decision
                      </p>

                      <h4
                        className={`mt-2 text-2xl font-bold ${meta.valueClass}`}
                      >
                        {meta.label}
                      </h4>

                      <p className="mt-2 max-w-xl text-sm leading-6 text-slate-300">
                        {meta.subtitle}
                      </p>
                    </div>
                  </div>

                  <span
                    className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${meta.badgeClass}`}
                  >
                    FINAL VERDICT
                  </span>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                    Decision ID
                  </p>

                  <p className="mt-2 break-all font-mono text-xs text-slate-300">
                    {decision.decision_id}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                    Constitution
                  </p>

                  <p className="mt-2 font-medium text-cyan-300">
                    {decision.constitution_version}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                    Mission
                  </p>

                  <p className="mt-2 break-all font-mono text-xs text-slate-300">
                    {decision.mission_id ?? 'Not provided'}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                    Agent
                  </p>

                  <p className="mt-2 break-all font-mono text-xs text-slate-300">
                    {decision.agent_id ?? 'Not specified'}
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-600">
                    Decision Timestamp
                  </p>

                  <p className="font-mono text-xs text-slate-400">
                    {new Date(
                      decision.timestamp,
                    ).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Governance Reasons
                  </p>

                  <span className="rounded-full border border-slate-700 bg-slate-900 px-2.5 py-1 text-[10px] text-slate-500">
                    {decision.reasons.length} checks
                  </span>
                </div>

                {decision.reasons.length > 0 ? (
                  <div className="space-y-2">
                    {decision.reasons.map(
                      (reason, index) => (
                        <div
                          key={`${reason}-${index}`}
                          className="flex items-start gap-3 rounded-lg border border-slate-800/80 bg-slate-950/60 px-3 py-2.5"
                        >
                          <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-blue-400/15 bg-blue-400/5 text-[10px] text-blue-300">
                            {index + 1}
                          </span>

                          <p className="text-sm leading-5 text-slate-300">
                            {reason}
                          </p>
                        </div>
                      ),
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-600">
                    No additional reasons returned.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}