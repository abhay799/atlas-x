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
  const [error, setError] = useState<string | null>(
    null,
  );

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

  const getOutcomeClass = (
    outcome: DecisionOutcome,
  ) => {
    switch (outcome) {
      case DecisionOutcome.ALLOW:
        return 'bg-green-900/50 text-green-400 border border-green-500';

      case DecisionOutcome.REQUIRE_HUMAN_APPROVAL:
        return 'bg-yellow-900/50 text-yellow-400 border border-yellow-500';

      case DecisionOutcome.BLOCK:
        return 'bg-red-900/50 text-red-400 border border-red-500';

      default:
        return 'bg-gray-900/50 text-gray-400 border border-gray-700';
    }
  };

  return (
    <section className="mb-8">
      <h2 className="mb-4 text-2xl font-semibold">
        Governance Decision Panel
      </h2>

      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <form
          onSubmit={handleEvaluate}
          className="space-y-4"
        >
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Mission ID
              </label>

              <input
                value={missionId}
                onChange={(event) =>
                  setMissionId(event.target.value)
                }
                type="text"
                placeholder="Enter mission ID"
                required
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Task ID
              </label>

              <input
                value={taskId}
                onChange={(event) =>
                  setTaskId(event.target.value)
                }
                type="text"
                placeholder="Enter task ID"
                required
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Agent ID (optional)
              </label>

              <input
                value={agentId}
                onChange={(event) =>
                  setAgentId(event.target.value)
                }
                type="text"
                placeholder="Enter agent ID"
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 ${
              loading
                ? 'cursor-not-allowed opacity-50'
                : ''
            }`}
          >
            {loading
              ? 'Evaluating...'
              : 'Evaluate Governance'}
          </button>
        </form>

        {error && (
          <div className="mt-3 rounded border border-red-500 bg-red-900/50 p-3">
            <p className="text-sm text-red-400">
              Error: {error}
            </p>
          </div>
        )}

        {decision && (
          <div
            className={`mt-4 rounded-lg p-4 ${getOutcomeClass(
              decision.outcome,
            )}`}
          >
            <h3 className="mb-2 text-lg font-medium">
              Governance Decision
            </h3>

            <p className="mb-2 text-xl font-bold">
              {decision.outcome}
            </p>

            <div className="space-y-2 text-sm">
              <p className="text-gray-300">
                <strong>Decision ID:</strong>{' '}
                {decision.decision_id}
              </p>

              {decision.mission_id && (
                <p className="text-gray-300">
                  <strong>Mission ID:</strong>{' '}
                  {decision.mission_id}
                </p>
              )}

              {decision.agent_id && (
                <p className="text-gray-300">
                  <strong>Agent ID:</strong>{' '}
                  {decision.agent_id}
                </p>
              )}

              <p className="text-gray-300">
                <strong>
                  Constitution Version:
                </strong>{' '}
                {decision.constitution_version}
              </p>

              <p className="text-gray-300">
                <strong>Timestamp:</strong>{' '}
                {new Date(
                  decision.timestamp,
                ).toLocaleString()}
              </p>

              {decision.reasons.length > 0 && (
                <>
                  <p className="mb-1 font-medium text-gray-200">
                    Reasons:
                  </p>

                  <ul className="list-inside list-disc text-gray-300">
                    {decision.reasons.map(
                      (reason, index) => (
                        <li key={index}>
                          {reason}
                        </li>
                      ),
                    )}
                  </ul>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}