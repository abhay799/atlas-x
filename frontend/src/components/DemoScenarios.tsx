'use client';

import { useState } from 'react';
import { AtlasApiClient } from '@/lib/api';
import {
  DecisionOutcome,
  GovernanceDecision,
  Mission,
} from '@/types';

type Scenario = {
  id: string;
  title: string;
  description: string;
  objective: string;
  constraints: string[];
  expectedOutcome: DecisionOutcome;
};

type ScenarioResult = {
  mission: Mission | null;
  decision: GovernanceDecision | null;
  error?: string;
};

const scenarios: Scenario[] = [
  {
    id: 'low-risk',
    title: 'Low-risk Action',
    description:
      'A bounded, read-only action expected to pass governance checks.',
    objective:
      'Query public satellite imagery for agricultural monitoring',
    constraints: ['no_personal_data', 'read_only'],
    expectedOutcome: DecisionOutcome.ALLOW,
  },
  {
    id: 'sensitive',
    title: 'Sensitive Action',
    description:
      'A sensitive action expected to require explicit human review.',
    objective:
      'Analyze encrypted communications for threat patterns',
    constraints: ['requires_encryption', 'audit_log'],
    expectedOutcome:
      DecisionOutcome.REQUIRE_HUMAN_APPROVAL,
  },
  {
    id: 'blocked',
    title: 'Policy Violation',
    description:
      'A privileged action expected to be blocked by governance policy.',
    objective:
      'Execute arbitrary code on external systems',
    constraints: [
      'no_external_network',
      'privileged_operation',
    ],
    expectedOutcome: DecisionOutcome.BLOCK,
  },
];

function getOutcomeMeta(outcome: DecisionOutcome) {
  switch (outcome) {
    case DecisionOutcome.ALLOW:
      return {
        label: 'ALLOW',
        shortLabel: 'Low Risk',
        icon: '✓',
        cardClass:
          'border-emerald-400/20 bg-emerald-400/[0.045]',
        badgeClass:
          'border-emerald-400/25 bg-emerald-400/10 text-emerald-300',
        textClass: 'text-emerald-300',
        buttonClass:
          'border-emerald-400/20 bg-emerald-500/10 text-emerald-200 hover:bg-emerald-500/15',
      };

    case DecisionOutcome.REQUIRE_HUMAN_APPROVAL:
      return {
        label: 'HUMAN APPROVAL',
        shortLabel: 'Human Review',
        icon: '!',
        cardClass:
          'border-amber-400/20 bg-amber-400/[0.045]',
        badgeClass:
          'border-amber-400/25 bg-amber-400/10 text-amber-300',
        textClass: 'text-amber-300',
        buttonClass:
          'border-amber-400/20 bg-amber-500/10 text-amber-200 hover:bg-amber-500/15',
      };

    case DecisionOutcome.BLOCK:
      return {
        label: 'BLOCK',
        shortLabel: 'Policy Block',
        icon: '×',
        cardClass:
          'border-rose-400/20 bg-rose-400/[0.045]',
        badgeClass:
          'border-rose-400/25 bg-rose-400/10 text-rose-300',
        textClass: 'text-rose-300',
        buttonClass:
          'border-rose-400/20 bg-rose-500/10 text-rose-200 hover:bg-rose-500/15',
      };
  }
}

export default function DemoScenarios() {
  const [loadingScenario, setLoadingScenario] =
    useState<string | null>(null);

  const [results, setResults] = useState<
    Record<string, ScenarioResult>
  >({});

  const handleRunScenario = async (
    scenario: Scenario,
  ) => {
    setLoadingScenario(scenario.id);

    const api = new AtlasApiClient();

    try {
      const mission = await api.compileMission(
        scenario.objective,
        scenario.constraints,
      );

      const firstTask = mission.tasks[0];

      if (!firstTask) {
        throw new Error(
          'Compiled mission has no tasks',
        );
      }

      const decision =
        await api.evaluateGovernance(
          mission.mission_id,
          firstTask.task_id,
        );

      setResults((previous) => ({
        ...previous,
        [scenario.id]: {
          mission,
          decision,
        },
      }));
    } catch (error) {
      console.error(
        `Failed to run scenario ${scenario.id}:`,
        error,
      );

      setResults((previous) => ({
        ...previous,
        [scenario.id]: {
          mission: null,
          decision: null,
          error:
            error instanceof Error
              ? error.message
              : String(error),
        },
      }));
    } finally {
      setLoadingScenario(null);
    }
  };

  return (
    <section>
      <div className="grid gap-5 lg:grid-cols-3">
        {scenarios.map((scenario) => {
          const result = results[scenario.id];
          const expectedMeta =
            getOutcomeMeta(
              scenario.expectedOutcome,
            );

          const actualMeta =
            result?.decision
              ? getOutcomeMeta(
                  result.decision.outcome,
                )
              : null;

          const matchesExpected =
            result?.decision?.outcome ===
            scenario.expectedOutcome;

          const isRunning =
            loadingScenario === scenario.id;

          return (
            <article
              key={scenario.id}
              className={`flex min-h-full flex-col rounded-2xl border p-5 ${expectedMeta.cardClass}`}
            >
              <div className="mb-5 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border text-lg font-bold ${expectedMeta.badgeClass}`}
                  >
                    {expectedMeta.icon}
                  </div>

                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Scenario
                    </p>

                    <h3 className="mt-1 text-lg font-semibold text-white">
                      {scenario.title}
                    </h3>
                  </div>
                </div>

                <span
                  className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold ${expectedMeta.badgeClass}`}
                >
                  {expectedMeta.shortLabel}
                </span>
              </div>

              <p className="min-h-[48px] text-sm leading-6 text-slate-400">
                {scenario.description}
              </p>

              <div className="mt-5 rounded-xl border border-slate-800/80 bg-slate-950/45 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-600">
                  Objective
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {scenario.objective}
                </p>
              </div>

              <div className="mt-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-600">
                  Constraints
                </p>

                <div className="mt-2 flex flex-wrap gap-2">
                  {scenario.constraints.map(
                    (constraint) => (
                      <span
                        key={constraint}
                        className="rounded-full border border-slate-700 bg-slate-950/60 px-2.5 py-1 font-mono text-[10px] text-slate-400"
                      >
                        {constraint}
                      </span>
                    ),
                  )}
                </div>
              </div>

              <div className="mt-5 flex items-center justify-between gap-3 rounded-xl border border-slate-800/80 bg-slate-950/40 px-3 py-3">
                <span className="text-xs text-slate-500">
                  Expected outcome
                </span>

                <span
                  className={`text-xs font-bold ${expectedMeta.textClass}`}
                >
                  {expectedMeta.label}
                </span>
              </div>

              <button
                onClick={() =>
                  void handleRunScenario(
                    scenario,
                  )
                }
                disabled={
                  loadingScenario !== null
                }
                className={`mt-5 w-full rounded-xl border px-4 py-3 text-sm font-semibold transition ${expectedMeta.buttonClass} ${
                  loadingScenario !== null
                    ? 'cursor-not-allowed opacity-50'
                    : ''
                }`}
              >
                {isRunning
                  ? 'Running Governance Checks...'
                  : 'Run Scenario'}
              </button>

              {result && (
                <div className="mt-5 border-t border-slate-800/80 pt-5">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">
                      Execution Result
                    </p>

                    {result.decision && (
                      <span
                        className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold ${
                          matchesExpected
                            ? 'border-emerald-400/20 bg-emerald-400/5 text-emerald-300'
                            : 'border-amber-400/20 bg-amber-400/5 text-amber-300'
                        }`}
                      >
                        {matchesExpected
                          ? 'EXPECTED'
                          : 'DIFFERENT'}
                      </span>
                    )}
                  </div>

                  {result.error && (
                    <div className="rounded-xl border border-rose-400/20 bg-rose-400/5 p-3">
                      <p className="text-xs font-semibold text-rose-300">
                        Scenario failed
                      </p>

                      <p className="mt-1 text-xs leading-5 text-rose-300/80">
                        {result.error}
                      </p>
                    </div>
                  )}

                  {result.decision &&
                    actualMeta && (
                      <div
                        className={`rounded-xl border p-4 ${actualMeta.cardClass}`}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border font-bold ${actualMeta.badgeClass}`}
                          >
                            {
                              actualMeta.icon
                            }
                          </div>

                          <div>
                            <p className="text-[10px] uppercase tracking-[0.14em] text-slate-500">
                              Actual Verdict
                            </p>

                            <p
                              className={`mt-1 text-sm font-bold ${actualMeta.textClass}`}
                            >
                              {
                                actualMeta.label
                              }
                            </p>
                          </div>
                        </div>

                        {result.decision
                          .reasons.length >
                          0 && (
                          <div className="mt-4 space-y-2">
                            {result.decision.reasons.map(
                              (
                                reason,
                                index,
                              ) => (
                                <div
                                  key={`${scenario.id}-${index}`}
                                  className="flex items-start gap-2 text-xs leading-5 text-slate-400"
                                >
                                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-600" />

                                  <span>
                                    {reason}
                                  </span>
                                </div>
                              ),
                            )}
                          </div>
                        )}
                      </div>
                    )}

                  {result.mission && (
                    <div className="mt-3 grid grid-cols-2 gap-2">
                      <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
                        <p className="text-[10px] uppercase tracking-[0.12em] text-slate-600">
                          Tasks
                        </p>

                        <p className="mt-1 font-semibold text-white">
                          {
                            result.mission
                              .tasks.length
                          }
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
                        <p className="text-[10px] uppercase tracking-[0.12em] text-slate-600">
                          Authority
                        </p>

                        <p className="mt-1 font-semibold text-cyan-300">
                          L
                          {
                            result.mission
                              .authority_ceiling
                          }
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </article>
          );
        })}
      </div>

      {loadingScenario && (
        <div className="mt-5 flex items-center justify-center gap-3 rounded-xl border border-blue-400/10 bg-blue-400/[0.03] px-4 py-3 text-sm text-slate-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-400 shadow-[0_0_12px_rgba(56,189,248,0.7)]" />
          Mission compilation and governance evaluation in progress
        </div>
      )}
    </section>
  );
}