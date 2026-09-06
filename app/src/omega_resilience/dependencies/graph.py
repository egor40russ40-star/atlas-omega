from __future__ import annotations
from omega_resilience.domain.models import ServiceDescriptor

class DependencyGraph:
    def __init__(self, descriptors: list[ServiceDescriptor]) -> None:
        self._d={x.service_id:x for x in descriptors}
        self._validate()

    def _validate(self):
        for s in self._d.values():
            for dep in s.dependencies:
                if dep not in self._d:
                    raise ValueError(f"unknown dependency: {s.service_id}->{dep}")
        # cycle check
        visiting=set(); visited=set()
        def dfs(node):
            if node in visiting:
                raise ValueError("dependency cycle")
            if node in visited:
                return
            visiting.add(node)
            for dep in self._d[node].dependencies:
                dfs(dep)
            visiting.remove(node); visited.add(node)
        for n in self._d:
            dfs(n)

    def descriptor(self, service_id: str) -> ServiceDescriptor:
        return self._d[service_id]

    def dependencies_of(self, service_id: str) -> tuple[str,...]:
        return self._d[service_id].dependencies

    def dependents_of(self, service_id: str) -> tuple[str,...]:
        return tuple(sorted(
            s.service_id for s in self._d.values() if service_id in s.dependencies
        ))
