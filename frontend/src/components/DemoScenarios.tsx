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
      'A simple data query that should be allowed by the governance engine.',
    objective:
      'Query public satellite imagery for agricultural monitoring',
    constraints: ['no_personal_data', 'read_only'],
    expectedOutcome: DecisionOutcome.ALLOW,
  },
  {
    id: 'sensitive',
    title: 'Sensitive Action',
    description:
      'An action that accesses sensitive data and requires human approval.',
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
      'An action that violates a core policy and should be blocked.',
    objective:
      'Execute arbitrary code on external systems',
    constraints: [
      'no_external_network',
      'privileged_operation',
    ],
    expectedOutcome: DecisionOutcome.BLOCK,
  },
];

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
    <section className="mb-8">
      <h2 className="mb-4 text-2xl font-semibold">
        Demo Scenarios
      </h2>

      <div className="grid gap-4 md:grid-cols-3">
        {scenarios.map((scenario) => {
          const result = results[scenario.id];

          return (
            <div
              key={scenario.id}
              className="rounded-lg border border-gray-700 bg-gray-800/50 p-4"
            >
              <h3 className="mb-2 text-lg font-medium">
                {scenario.title}
              </h3>

              <p className="mb-3 text-sm text-gray-400">
                {scenario.description}
              </p>

              <button
                onClick={() =>
                  void handleRunScenario(
                    scenario,
                  )
                }
                disabled={
                  loadingScenario !== null
                }
                className={`mb-3 w-full rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 ${
                  loadingScenario !== null
                    ? 'cursor-not-allowed opacity-50'
                    : ''
                }`}
              >
                {loadingScenario ===
                scenario.id
                  ? 'Running...'
                  : 'Run Scenario'}
              </button>

              {result && (
                <div className="mt-3 rounded bg-gray-900/50 p-3">
                  <h4 className="mb-1 text-sm font-medium">
                    Result
                  </h4>

                  {result.error && (
                    <p className="mb-2 text-xs text-red-400">
                      {result.error}
                    </p>
                  )}

                  {result.mission ? (
                    <>
                      <p className="text-xs text-gray-300">
                        Mission ID:{' '}
                        {
                          result.mission
                            .mission_id
                        }
                      </p>

                      <p className="text-xs text-gray-300">
                        Tasks:{' '}
                        {
                          result.mission
                            .tasks.length
                        }
                      </p>
                    </>
                  ) : (
                    !result.error && (
                      <p className="text-xs text-red-400">
                        Mission compilation
                        failed
                      </p>
                    )
                  )}

                  {result.decision && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-300">
                        Decision:{' '}
                        {
                          result.decision
                            .outcome
                        }
                      </p>

                      {result.decision
                        .reasons.length >
                        0 && (
                        <p className="text-xs text-gray-300">
                          Reasons:{' '}
                          {result.decision.reasons.join(
                            ', ',
                          )}
                        </p>
                      )}
                    </div>
                  )}

                  <p className="mt-2 text-xs text-gray-500">
                    Expected scenario:{' '}
                    {scenario.expectedOutcome}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}