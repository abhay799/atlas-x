# Security Model

ATLAS X applies deterministic, fail-closed governance before safe execution.
Unknown identity, missing declared capability, insufficient authority, hard
policy, emergency state, quarantine, risk-budget exhaustion, and red-team
failure prevent autonomous authorization.

## Implemented Mitigations

- **Privilege and authority escalation:** agent authority is typed; scoped,
  expiring grants are evaluated by the authority engine.
- **Undeclared capability:** capability registration and declared grants are
  checked before application authorization.
- **Policy bypass:** hard policy is a blocking reason and outranks trust and
  recorded approval.
- **Approval abuse:** approval resolves only a clean approval requirement;
  rejection dominates and hard blocks remain blocks.
- **Prompt injection:** external content is inspected and prompt-injection
  signals feed red-team blocking.
- **Correlated agents:** consensus reports correlated evidence rather than
  treating identical sources as independent.
- **Replay and expiry:** the executor rejects expired envelopes.
- **Parameter escalation:** the executor rejects parameters outside the
  envelope's allowed parameter map.
- **Wrong context:** when provided, agent, mission, action, and scope inputs
  are bound to the envelope and mismatches are rejected.
- **Emergency and quarantine bypass:** both are hard control-plane blocks.

## Audit and Provenance Assumptions

The local audit log, provenance graph, and SQL record store provide
reconstruction evidence for the tested process. They are not cryptographically
tamper-evident storage; external signing, retention controls, and independent
audit infrastructure remain future hardening.

## Future Hardening

PostgreSQL integration certification, durable audit storage, authentication and
credential brokering, production adapter controls, distributed emergency
propagation, and independent security review are not claimed as implemented.
