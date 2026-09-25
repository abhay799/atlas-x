# Threat Model

ATLAS X models failures at the boundary between autonomous proposals and
bounded execution. It does not claim to solve every deployment or operational
security concern.

| Threat | Implemented mitigation | Remaining hardening |
| --- | --- | --- |
| Privilege escalation | Typed authority and scoped grants | External identity and credential integration |
| Undeclared capability | Declaration and registry checks | Durable capability administration |
| Policy bypass | Hard policy precedence | Signed/versioned policy distribution |
| Approval abuse | Approval is narrow; rejection/hard blocks dominate | Strong operator authentication and approval provenance |
| Prompt injection | Content-defense signal and red-team block | Broader model/tool isolation |
| Collusion/correlation | Consensus correlation detection | Independent source attestation |
| Expired authorization replay | Envelope expiry check | Durable replay protection |
| Parameter escalation | Allowed-parameter equality checks | Richer schema/range constraints |
| Wrong agent/mission/action/scope | Envelope context mismatch checks when supplied | Adapter-side identity enforcement |
| Emergency-stop bypass | Emergency brake blocks decision | Distributed emergency propagation |
| Quarantine bypass | Quarantine is a hard block | Durable cross-node quarantine state |
| Provenance tampering | Local reconstruction records | Cryptographic, append-only external audit storage |

The certified scope is deterministic local simulation. PostgreSQL, multi-node
deployment, destructive adapters, and production incident operations are not
validated here.
