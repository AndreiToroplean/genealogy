from __future__ import annotations

from collections.abc import Iterable
import json
import random

from genealogy.person import Person
from genealogy.utils import Relationship


class FamilyTree:
    @classmethod
    def from_json(cls, json_data: str) -> FamilyTree:
        data = json.loads(json_data)
        people_dict: dict[str, Person] = {}

        # Create all Person objects
        for id_, name in data["people"].items():
            person = Person(id_, name)
            people_dict[id_] = person

        # Set up relationships
        for child_id, parents in data["relationships"].items():
            child = people_dict[child_id]
            for relationship, parent_id in parents.items():
                parent = people_dict[parent_id]
                child.parents[Relationship[relationship]] = parent
                parent.children.append(child)

        return cls(people_dict.values())

    def __init__(self, people: Iterable[Person]):
        random.seed(0)

        self.people: list[Person] = sorted(people)
        self._compute_generations()
        self._relax()

    def to_json(self) -> str:
        data = {
            "people": {
                person.id: person.name for person in self.people
            },
            "relationships": {
                person.id: {
                    rel.name: parent.id
                    for rel, parent in person.parents.items()
                }
                for person in self.people
                if person.parents
            }
        }
        return json.dumps(data, indent=2)

    def __repr__(self) -> str:
        people_str = ",\n    ".join([repr(person) for person in self.people])
        return f"FamilyTree([\n    {people_str}\n])"

    def _compute_generations(self) -> None:
        self._sort_topologically()

        for i, person in enumerate(self.people):
            for child in person.children:
                person.generation = max(person.generation, child.generation + 1)

        for i, person in zip(range(len(self.people) - 1, -1, -1), reversed(self.people)):
            min_generation: int | None = None
            for parent in person.parents.values():
                if min_generation is None or parent.generation < min_generation:
                    min_generation = parent.generation
            if min_generation is not None:
                person.generation = min_generation - 1

    def _sort_topologically(self) -> None:
        def append(n: Person) -> None:
            sorted_nodes.append(n)

        visited: list[Person] = []
        sorted_nodes: list[Person] = []
        while True:
            for node in self.people:
                if node not in visited:
                    node.traverse_children_depth_first(visited, append)
                    append(node)
            else:
                break

        self.people[:] = reversed(sorted_nodes)

    def _relax(
            self,
            n_iterations: int = 128,
            force: float = 0.05,
            children_force: float = 1.0,
            parents_force: float = 1.0,
            others_force: float = -0.1,
    ) -> None:
        for i, person in enumerate(self.people):
            person.relax_position = -float(i)

        for _ in range(n_iterations):
            for person in self.people:
                acceleration: float = 0.0
                for other_person in self.people:
                    if other_person in person.children:
                        acceleration += (other_person.relax_position - person.relax_position) * children_force
                    elif other_person in person.parents.values():
                        acceleration += (other_person.relax_position - person.relax_position) * parents_force
                    else:
                        acceleration += (other_person.relax_position - person.relax_position) * others_force
                person.relax_position += acceleration * force

        self.people.sort(key=lambda p: -p.relax_position)
