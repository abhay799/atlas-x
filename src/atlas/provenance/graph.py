from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ProvenanceNode:
    node_id: UUID
    kind: str
    ref: str
    data: dict[str, Any]
    timestamp: datetime


@dataclass(frozen=True)
class ProvenanceEdge:
    source: UUID
    target: UUID
    relation: str


class ProvenanceGraph:
    def __init__(self) -> None:
        self.nodes: dict[UUID, ProvenanceNode] = {}
        self.edges: list[ProvenanceEdge] = []

    def add(self, kind: str, ref: str, data: dict[str, Any] | None = None) -> UUID:
        n = ProvenanceNode(uuid4(), kind, ref, data or {}, datetime.now(UTC))
        self.nodes[n.node_id] = n
        return n.node_id

    def link(self, a: UUID, b: UUID, relation: str) -> None:
        self.edges.append(ProvenanceEdge(a, b, relation))

    def reconstruct(self, node: UUID) -> dict[str, Any]:
        related = [e for e in self.edges if e.source == node or e.target == node]
        ids = {node} | {e.source for e in related} | {e.target for e in related}
        return {"nodes": [self.nodes[i] for i in ids if i in self.nodes], "edges": related}
