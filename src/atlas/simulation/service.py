from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class SimulationResult:
    simulation_id: UUID
    seed: int
    success: bool
    events: tuple[str, ...]
    outputs: dict[str, Any]
    is_simulation: bool = True


class MissionDigitalTwin:
    def run(self, steps: list[dict[str, Any]], seed: int = 0) -> SimulationResult:
        events = []
        ok = True
        for s in steps:
            events.append(str(s.get("action", "unknown")))
            if s.get("forced_failure"):
                ok = False
                break
        return SimulationResult(uuid4(), seed, ok, tuple(events), {"steps_executed": len(events)})
