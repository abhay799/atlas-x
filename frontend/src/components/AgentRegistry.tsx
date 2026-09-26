'use client';

import { useEffect, useState } from 'react';
import { AtlasApiClient } from '@/lib/api';
import {
  AgentIdentity,
  AgentStatus,
  Capability,
} from '@/types';

export default function AgentRegistry() {
  const [loading, setLoading] = useState(false);
  const [agents, setAgents] = useState<AgentIdentity[]>([]);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);

  const [newAgent, setNewAgent] = useState<
    Omit<
      AgentIdentity,
      | 'agent_id'
      | 'created_at'
      | 'status'
      | 'declared_capabilities'
      | 'allowed_actions'
      | 'forbidden_actions'
      | 'identity_provenance'
      | 'expires_at'
      | 'revoked_at'
    >
  >({
    role: '',
    authority: 0,
  });

  const [newCapability, setNewCapability] = useState<
    Omit<Capability, 'version' | 'provenance'>
  >({
    name: '',
    scope: 'global',
    restrictions: [],
  });

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);

      try {
        // Backend currently does not expose list endpoints for
        // agents/capabilities, so this public demo keeps registrations
        // in local component state for the active browser session.
        setAgents([]);
        setCapabilities([]);
      } catch (error) {
        console.error('Failed to load agents/capabilities:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleRegisterAgent = async () => {
    setLoading(true);
    const api = new AtlasApiClient();

    try {
      const agent: AgentIdentity = {
        agent_id: Math.random().toString(36).substring(2, 10),
        role: newAgent.role,
        authority: newAgent.authority,
        status: AgentStatus.ACTIVE,
        declared_capabilities: [],
        allowed_actions: [],
        forbidden_actions: [],
        created_at: new Date().toISOString(),
        identity_provenance: 'demo',
        expires_at: null,
        revoked_at: null,
      };

      const registeredAgent = await api.registerAgent(agent);

      setAgents((prev) => [registeredAgent, ...prev]);

      setNewAgent({
        role: '',
        authority: 0,
      });
    } catch (error) {
      console.error('Failed to register agent:', error);

      alert(
        'Failed to register agent: ' +
          (error instanceof Error ? error.message : String(error)),
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterCapability = async () => {
    setLoading(true);
    const api = new AtlasApiClient();

    try {
      const capability: Capability = {
        name: newCapability.name,
        scope: newCapability.scope,
        restrictions: newCapability.restrictions,
        version: '1.0',
        provenance: 'declared',
      };

      const registeredCapability =
        await api.registerCapability(capability);

      setCapabilities((prev) => [
        registeredCapability,
        ...prev,
      ]);

      setNewCapability({
        name: '',
        scope: 'global',
        restrictions: [],
      });
    } catch (error) {
      console.error('Failed to register capability:', error);

      alert(
        'Failed to register capability: ' +
          (error instanceof Error ? error.message : String(error)),
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGrantCapability = async (
    agentId: string,
    capabilityName: string,
  ) => {
    setLoading(true);
    const api = new AtlasApiClient();

    try {
      await api.grantCapability(
        agentId,
        capabilityName,
      );

      alert(
        `Granted capability ${capabilityName} to agent ${agentId}`,
      );
    } catch (error) {
      console.error(
        'Failed to grant capability:',
        error,
      );

      alert(
        'Failed to grant capability: ' +
          (error instanceof Error ? error.message : String(error)),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mb-8">
      <h2 className="mb-4 text-2xl font-semibold">
        Agent Registry
      </h2>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
          <h3 className="mb-2 text-lg font-medium">
            Register Agent
          </h3>

          <form
            onSubmit={(event) => {
              event.preventDefault();
              void handleRegisterAgent();
            }}
            className="space-y-3"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Role
              </label>

              <input
                value={newAgent.role}
                onChange={(event) =>
                  setNewAgent({
                    ...newAgent,
                    role: event.target.value,
                  })
                }
                type="text"
                required
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Authority Level
              </label>

              <select
                value={newAgent.authority}
                onChange={(event) =>
                  setNewAgent({
                    ...newAgent,
                    authority: Number(event.target.value),
                  })
                }
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              >
                {[0, 1, 2, 3, 4, 5].map(
                  (level) => (
                    <option
                      key={level}
                      value={level}
                    >
                      L{level}
                    </option>
                  ),
                )}
              </select>
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
                ? 'Registering...'
                : 'Register Agent'}
            </button>
          </form>
        </div>

        <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
          <h3 className="mb-2 text-lg font-medium">
            Register Capability
          </h3>

          <form
            onSubmit={(event) => {
              event.preventDefault();
              void handleRegisterCapability();
            }}
            className="space-y-3"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Capability Name
              </label>

              <input
                value={newCapability.name}
                onChange={(event) =>
                  setNewCapability({
                    ...newCapability,
                    name: event.target.value,
                  })
                }
                type="text"
                required
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Scope
              </label>

              <select
                value={newCapability.scope}
                onChange={(event) =>
                  setNewCapability({
                    ...newCapability,
                    scope: event.target.value,
                  })
                }
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              >
                <option value="global">
                  global
                </option>
                <option value="mission">
                  mission
                </option>
                <option value="agent">
                  agent
                </option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-300">
                Restrictions (comma-separated)
              </label>

              <input
                value={newCapability.restrictions.join(
                  ',',
                )}
                onChange={(event) =>
                  setNewCapability({
                    ...newCapability,
                    restrictions:
                      event.target.value
                        .split(',')
                        .map((value) =>
                          value.trim(),
                        )
                        .filter(Boolean),
                  })
                }
                type="text"
                className="w-full rounded border border-gray-600 bg-gray-700/50 px-3 py-2 text-white"
              />
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
                ? 'Registering...'
                : 'Register Capability'}
            </button>
          </form>
        </div>
      </div>

      {agents.length > 0 && (
        <div className="mt-6">
          <h3 className="mb-2 text-lg font-medium">
            Registered Agents
          </h3>

          <div className="space-y-3">
            {agents.map((agent) => (
              <div
                key={agent.agent_id}
                className="rounded border border-gray-700 bg-gray-900/50 p-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-white">
                      Agent ID: {agent.agent_id}
                    </p>

                    <p className="text-sm text-gray-300">
                      Role: {agent.role}
                    </p>

                    <p className="text-sm text-gray-300">
                      Authority: L
                      {agent.authority}
                    </p>

                    <p className="text-sm text-gray-300">
                      Status: {agent.status}
                    </p>
                  </div>

                  <div className="space-x-2">
                    {capabilities.length >
                      0 && (
                      <button
                        onClick={() =>
                          void handleGrantCapability(
                            agent.agent_id,
                            capabilities[0]
                              .name,
                          )
                        }
                        disabled={loading}
                        className={`rounded bg-green-600 px-2 py-1 text-xs hover:bg-green-700 ${
                          loading
                            ? 'cursor-not-allowed opacity-50'
                            : ''
                        }`}
                      >
                        Grant{' '}
                        {
                          capabilities[0]
                            .name
                        }
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {capabilities.length > 0 && (
        <div className="mt-6">
          <h3 className="mb-2 text-lg font-medium">
            Registered Capabilities
          </h3>

          <div className="space-y-2">
            {capabilities.map(
              (capability) => (
                <div
                  key={capability.name}
                  className="rounded border border-gray-700 bg-gray-900/50 p-3"
                >
                  <p className="font-medium text-white">
                    Capability:{' '}
                    {capability.name}
                  </p>

                  <p className="text-sm text-gray-300">
                    Scope: {capability.scope}
                  </p>

                  {capability.restrictions
                    .length > 0 && (
                    <p className="text-sm text-gray-300">
                      Restrictions:{' '}
                      {capability.restrictions.join(
                        ', ',
                      )}
                    </p>
                  )}
                </div>
              ),
            )}
          </div>
        </div>
      )}
    </section>
  );
}