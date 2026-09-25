import json
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError


class ConstitutionError(RuntimeError):
    pass


class AtlasConstitution(BaseModel):
    schema_version: str = Field(pattern=r"^1\.")
    constitution_version: str = Field(min_length=1)
    require_agent_identity: bool = True
    max_autonomous_authority: int = Field(ge=0, le=5)
    human_authority_level: int = Field(ge=1, le=5)
    undeclared_capabilities_denied: bool = True
    tools_default_deny: bool = True
    resources_default_deny: bool = True
    data_default_deny: bool = True
    require_escalation_above_authority: bool = True
    irreversible_actions_require_human: bool = True
    financial_autonomous_limit: float = Field(ge=0)
    privacy_constraints: tuple[str, ...]
    inter_agent_communication_default_deny: bool = True
    rollback_required_for_mutating_actions: bool = True
    emergency_shutdown_enabled: bool = True
    evidence_required_for_governed_actions: bool = True
    audit_required: bool = True


def load_constitution(path: str | Path) -> AtlasConstitution:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        constitution = AtlasConstitution.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise ConstitutionError(f"ATLAS constitution is invalid: {exc}") from exc
    safety_flags = (
        constitution.require_agent_identity,
        constitution.undeclared_capabilities_denied,
        constitution.tools_default_deny,
        constitution.audit_required,
        constitution.emergency_shutdown_enabled,
    )
    if not all(safety_flags):
        raise ConstitutionError("constitution weakens mandatory fail-closed invariants")
    return constitution
