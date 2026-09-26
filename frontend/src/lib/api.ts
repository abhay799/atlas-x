import {
  AgentIdentity,
  Capability,
  GovernanceDecision,
  Mission,
} from '@/types';

const DEFAULT_API_URL = 'http://localhost:8000';

export function resolveApiUrl(
  configuredUrl: string | undefined = process.env.NEXT_PUBLIC_ATLAS_API_URL,
  nodeEnv: string | undefined = process.env.NODE_ENV,
): string {
  const trimmedUrl = configuredUrl?.trim();

  if (trimmedUrl) {
    return trimmedUrl.replace(/\/+$/, '');
  }

  if (nodeEnv === 'production') {
    throw new Error(
      'NEXT_PUBLIC_ATLAS_API_URL must be set in production',
    );
  }

  return DEFAULT_API_URL;
}

export class AtlasApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl
      ? baseUrl.replace(/\/+$/, '')
      : resolveApiUrl();
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const response = await fetch(
      `${this.baseUrl}${endpoint}`,
      {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      },
    );

    if (!response.ok) {
      let message = 'Unknown error';

      try {
        const errorData = (await response.json()) as {
          detail?: string;
          message?: string;
        };

        message =
          errorData.detail ??
          errorData.message ??
          message;
      } catch {
        // Response did not contain JSON error details.
      }

      throw new Error(
        `API error: ${response.status} ${response.statusText} - ${message}`,
      );
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  }

  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>(
      '/health',
    );
  }

  async ready(): Promise<{
    status: string;
    constitution_version: string;
  }> {
    return this.request<{
      status: string;
      constitution_version: string;
    }>('/ready');
  }

  async registerAgent(
    agent: AgentIdentity,
  ): Promise<AgentIdentity> {
    return this.request<AgentIdentity>('/agents', {
      method: 'POST',
      body: JSON.stringify(agent),
    });
  }

  async getAgent(
    agentId: string,
  ): Promise<AgentIdentity> {
    return this.request<AgentIdentity>(
      `/agents/${agentId}`,
    );
  }

  async registerCapability(
    capability: Capability,
  ): Promise<Capability> {
    return this.request<Capability>(
      '/capabilities',
      {
        method: 'POST',
        body: JSON.stringify(capability),
      },
    );
  }

  async grantCapability(
    agentId: string,
    capabilityName: string,
  ): Promise<void> {
    await this.request<void>(
      `/agents/${agentId}/capabilities/${capabilityName}`,
      {
        method: 'POST',
      },
    );
  }

  async compileMission(
    objective: string,
    constraints: string[],
  ): Promise<Mission> {
    return this.request<Mission>(
      '/missions/compile',
      {
        method: 'POST',
        body: JSON.stringify({
          objective,
          constraints,
        }),
      },
    );
  }

  async getMission(
    missionId: string,
  ): Promise<Mission> {
    return this.request<Mission>(
      `/missions/${missionId}`,
    );
  }

  async evaluateGovernance(
    missionId: string,
    taskId: string,
    agentId?: string,
  ): Promise<GovernanceDecision> {
    return this.request<GovernanceDecision>(
      '/governance/evaluate',
      {
        method: 'POST',
        body: JSON.stringify({
          mission_id: missionId,
          task_id: taskId,
          agent_id: agentId,
        }),
      },
    );
  }

  async getAuditEvents(): Promise<unknown[]> {
    // Backend currently has no public audit endpoint.
    return [];
  }
}