# ADR 0001: Modular monolith and fail-closed bootstrap
Status: Accepted

ATLAS X begins as a modular monolith with domain/application boundaries rather than microservices. External execution and heavyweight infrastructure are excluded. Constitution loading is a startup gate. In-memory repositories are explicit bootstrap adapters, not durable production persistence. This keeps Phases 0–4 testable while preserving extraction boundaries for later scale.
