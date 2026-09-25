from atlas.domain.models import AuthorityLevel, Mission, MissionTask


class DeterministicMissionCompiler:
    """Conservative bootstrap compiler; AI planners can later implement the same boundary."""

    def compile(
        self, objective: str, constraints: tuple[str, ...], constitution_version: str
    ) -> Mission:
        text = objective.lower()
        no_prod = (
            any("without modifying production" in c.lower() for c in constraints)
            or "without modifying production" in text
        )
        tasks: list[MissionTask] = [
            MissionTask(
                task_id="investigate-data",
                title="Investigate relevant data",
                required_capabilities=frozenset({"data.analysis"}),
                evidence_requirements=("source_data",),
            ),
            MissionTask(
                task_id="analyze-system",
                title="Analyze system and operational context",
                required_capabilities=frozenset({"system.analysis"}),
                evidence_requirements=("system_observations",),
            ),
            MissionTask(
                task_id="synthesize",
                title="Synthesize hypotheses",
                dependencies=("investigate-data", "analyze-system"),
                required_capabilities=frozenset({"analysis.synthesis"}),
                evidence_requirements=("supporting_evidence",),
            ),
            MissionTask(
                task_id="recommend",
                title="Prepare recommendation",
                dependencies=("synthesize",),
                required_capabilities=frozenset({"recommendation.prepare"}),
                authority_required=AuthorityLevel.L1,
                evidence_requirements=("supported_hypothesis",),
            ),
        ]
        restrictions = ["no_direct_execution"]
        if no_prod:
            restrictions.append("no_production_mutation")
        return Mission(
            objective=objective,
            constraints=constraints,
            tasks=tuple(tasks),
            execution_restrictions=tuple(restrictions),
            constitution_version=constitution_version,
        )
