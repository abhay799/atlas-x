from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    evidence: dict[str, float]


class ConstitutionMonitor:
    def inspect(self, metrics: dict[str, float]) -> list[Finding]:
        f = []
        checks = [
            ("AUTHORITY_CREEP", "high", "authority_elevations", 5),
            ("PRIVILEGE_CONCENTRATION", "high", "max_agent_capability_share", 0.6),
            ("RISK_ACCUMULATION", "high", "risk_consumption_ratio", 0.9),
            ("HUMAN_OVERSIGHT_REDUCED", "critical", "human_review_ratio", 0.1),
            ("QUARANTINE_PATTERN", "medium", "quarantine_count", 3),
        ]
        for code, sev, k, t in checks:
            v = metrics.get(k, 0)
            if (k == "human_review_ratio" and v < t) or (k != "human_review_ratio" and v > t):
                f.append(Finding(code, sev, {k: v, "threshold": t}))
        return f
