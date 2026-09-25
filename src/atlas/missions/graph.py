from atlas.domain.models import Mission, MissionTask


class MissionGraphError(ValueError):
    pass


class MissionGraph:
    def __init__(self, mission: Mission) -> None:
        self.mission = mission
        self.nodes = {task.task_id: task for task in mission.tasks}
        self.validate()

    def validate(self) -> None:
        for task in self.nodes.values():
            missing = set(task.dependencies) - self.nodes.keys()
            if missing:
                raise MissionGraphError(f"unknown dependencies: {sorted(missing)}")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise MissionGraphError("mission graph contains a cycle")
            if node in visited:
                return
            visiting.add(node)
            for dep in self.nodes[node].dependencies:
                visit(dep)
            visiting.remove(node)
            visited.add(node)

        for node in self.nodes:
            visit(node)

    def serialize(self) -> dict[str, object]:
        return self.mission.model_dump(mode="json")

    def task(self, task_id: str) -> MissionTask:
        return self.nodes[task_id]
