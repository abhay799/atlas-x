from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from atlas.application.service import AtlasService
from atlas.domain.models import (
    AgentIdentity,
    AuthorityLevel,
    Capability,
    DecisionOutcome,
    Mission,
    MissionTask,
)
from atlas.governance.constitution import ConstitutionError, load_constitution
from atlas.identity.service import DuplicateAgentError
from atlas.missions.graph import MissionGraph, MissionGraphError

ROOT = Path(__file__).parents[1]


def constitution():
    return load_constitution(ROOT / "config/constitution.json")


def test_constitution_validates_and_invalid_fails_closed(tmp_path):
    assert constitution().audit_required is True
    bad = tmp_path / "bad.json"
    bad.write_text('{"schema_version":"1.0"}', encoding="utf-8")
    with pytest.raises(ConstitutionError):
        load_constitution(bad)


def test_agent_identity_validation_duplicate_and_serialization():
    service = AtlasService(constitution())
    agent = AgentIdentity(
        agent_id="sre-agent-1",
        role="SRE",
        authority=AuthorityLevel.L2,
        identity_provenance="human-admin",
    )
    service.register_agent(agent)
    with pytest.raises(DuplicateAgentError):
        service.register_agent(agent)
    assert AgentIdentity.model_validate_json(agent.model_dump_json()) == agent
    with pytest.raises(ValidationError):
        AgentIdentity(
            agent_id="BAD ID", role="x", authority=AuthorityLevel.L2, identity_provenance="ok"
        )


def test_capability_declared_only_and_undeclared_rejected():
    service = AtlasService(constitution())
    service.register_capability(Capability(name="data.analysis"))
    agent = AgentIdentity(
        agent_id="data-agent-1",
        role="Data",
        authority=AuthorityLevel.L2,
        declared_capabilities=frozenset({"data.analysis"}),
        identity_provenance="human-admin",
    )
    service.register_agent(agent)
    service.grant_capability(agent.agent_id, "data.analysis")
    assert service.capabilities.has(agent.agent_id, "data.analysis")
    with pytest.raises(ValueError):
        service.grant_capability(agent.agent_id, "system.analysis")


def test_mission_compilation_preserves_constraint_and_dag():
    service = AtlasService(constitution())
    mission = service.compile_mission(
        "Investigate checkout conversion drop without modifying production",
        ("without modifying production",),
    )
    assert "without modifying production" in mission.constraints
    assert "no_production_mutation" in mission.execution_restrictions
    MissionGraph(mission)
    assert Mission.model_validate_json(mission.model_dump_json()).mission_id == mission.mission_id


def test_cycle_is_rejected():
    tasks = (
        MissionTask(task_id="a", title="A", dependencies=("b",)),
        MissionTask(task_id="b", title="B", dependencies=("a",)),
    )
    mission = Mission(objective="cycle test mission", tasks=tasks, constitution_version="1")
    with pytest.raises(MissionGraphError):
        MissionGraph(mission)


def test_gateway_blocks_missing_identity_capability_authority_and_allows_valid():
    service = AtlasService(constitution())
    mission = service.compile_mission("Investigate checkout conversion safely", ())
    blocked = service.evaluate(mission.mission_id, "investigate-data", None)
    assert blocked.outcome == DecisionOutcome.BLOCK
    service.register_capability(Capability(name="data.analysis"))
    weak = AgentIdentity(
        agent_id="data-agent-2",
        role="Data",
        authority=AuthorityLevel.L0,
        declared_capabilities=frozenset({"data.analysis"}),
        identity_provenance="admin",
    )
    service.register_agent(weak)
    service.grant_capability(weak.agent_id, "data.analysis")
    assert (
        service.evaluate(mission.mission_id, "investigate-data", weak.agent_id).outcome
        == DecisionOutcome.BLOCK
    )
    good = AgentIdentity(
        agent_id="data-agent-3",
        role="Data",
        authority=AuthorityLevel.L2,
        declared_capabilities=frozenset({"data.analysis"}),
        identity_provenance="admin",
    )
    service.register_agent(good)
    service.grant_capability(good.agent_id, "data.analysis")
    decision = service.evaluate(mission.mission_id, "investigate-data", good.agent_id, uuid4())
    assert decision.outcome == DecisionOutcome.ALLOW
    assert service.audit.events()[-1].decision_id == decision.decision_id


def test_missing_evidence_requirement_fails_closed():
    service = AtlasService(constitution())
    agent = AgentIdentity(
        agent_id="safe-agent-1",
        role="Safe",
        authority=AuthorityLevel.L2,
        identity_provenance="admin",
    )
    task = MissionTask(task_id="unsafe", title="Unsafe", evidence_requirements=())
    assert service.gateway.evaluate(agent, task).outcome == DecisionOutcome.BLOCK
