export enum AuthorityLevel {
  L0 = 0,
  L1 = 1,
  L2 = 2,
  L3 = 3,
  L4 = 4,
  L5 = 5,
}

export enum AgentStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  REVOKED = 'revoked',
}

export enum TaskStatus {
  PENDING = 'pending',
  ASSIGNED = 'assigned',
  COMPLETE = 'complete',
  BLOCKED = 'blocked',
}

export enum MissionStatus {
  COMPILED = 'compiled',
  READY = 'ready',
  BLOCKED = 'blocked',
  COMPLETE = 'complete',
}

export enum DecisionOutcome {
  ALLOW = 'ALLOW',
  REQUIRE_HUMAN_APPROVAL = 'REQUIRE_HUMAN_APPROVAL',
  BLOCK = 'BLOCK',
}

export interface Capability {
  name: string;
  scope: string;
  restrictions: string[];
  version: string;
  provenance: string;
}

export interface AgentIdentity {
  agent_id: string;
  role: string;
  authority: AuthorityLevel;
  status: AgentStatus;
  declared_capabilities: string[];
  allowed_actions: string[];
  forbidden_actions: string[];
  created_at: string; // ISO string
  identity_provenance: string;
  expires_at: string | null; // ISO string or null
  revoked_at: string | null; // ISO string or null
}

export interface MissionTask {
  task_id: string;
  title: string;
  dependencies: string[];
  required_capabilities: string[];
  authority_required: AuthorityLevel;
  evidence_requirements: string[];
  assigned_agent_id: string | null;
  status: TaskStatus;
}

export interface Mission {
  mission_id: string;
  objective: string;
  constraints: string[];
  tasks: MissionTask[];
  authority_ceiling: AuthorityLevel;
  execution_restrictions: string[];
  human_approval_required: boolean;
  status: MissionStatus;
  constitution_version: string;
  created_at: string; // ISO string
  created_by: string;
}

export interface GovernanceDecision {
  decision_id: string;
  outcome: DecisionOutcome;
  reasons: string[];
  mission_id: string | null;
  agent_id: string | null;
  constitution_version: string;
  timestamp: string; // ISO string
}