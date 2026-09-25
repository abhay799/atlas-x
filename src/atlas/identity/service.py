from atlas.domain.models import AgentIdentity


class DuplicateAgentError(ValueError):
    pass


class AgentRegistry:
    """In-memory adapter for bootstrap/tests; replaceable behind this application boundary."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentIdentity] = {}

    def register(self, agent: AgentIdentity) -> AgentIdentity:
        if agent.agent_id in self._agents:
            raise DuplicateAgentError(agent.agent_id)
        self._agents[agent.agent_id] = agent
        return agent

    def get(self, agent_id: str) -> AgentIdentity | None:
        return self._agents.get(agent_id)
