from atlas.domain.models import Capability


class CapabilityRegistry:
    def __init__(self) -> None:
        self._catalog: dict[str, Capability] = {}
        self._agent_caps: dict[str, set[str]] = {}

    def register_capability(self, capability: Capability) -> Capability:
        self._catalog[capability.name] = capability
        return capability

    def is_registered(self, capability_name: str) -> bool:
        return capability_name in self._catalog

    def grant_declared(self, agent_id: str, capability_name: str) -> None:
        if capability_name not in self._catalog:
            raise ValueError("unknown capability")
        self._agent_caps.setdefault(agent_id, set()).add(capability_name)

    def has(self, agent_id: str, capability_name: str) -> bool:
        return capability_name in self._agent_caps.get(agent_id, set())

    def list_for_agent(self, agent_id: str) -> tuple[Capability, ...]:
        return tuple(self._catalog[name] for name in sorted(self._agent_caps.get(agent_id, set())))
