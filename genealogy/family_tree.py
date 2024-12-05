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
        self._perform_augmented_top_sort()
        self._compute_generations()

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

    def _perform_augmented_top_sort(self, n_iterations: int = 64) -> None:
        visited: list[Person] = []
        sorted_nodes: list[Person] = []
        while True:
            for node in self.people:
                if node not in visited:
                    break

            else:
                break

            def append(n: Person) -> None:
                sorted_nodes.append(n)
            node.traverse_children_depth_first(visited, append)
            append(node)

        sorted_nodes.reverse()
        self.people[:] = sorted_nodes

        for i in range(n_iterations):
            self._pull_children_down(p_skip=0.0, skip_if_not_found=True)
            self._pull_parents_up(p_skip=0.0, skip_if_not_found=True)

    def _pull_parents_up(
        self, 
        *, 
        force: float = 1.0, 
        p_skip: float = 0.0, 
        skip_if_not_found: bool = False,
    ) -> None:
        for i, person in enumerate(self.people):
            if random.random() < p_skip:
                continue
            for j, potential_child in zip(range(len(self.people[:i]) - 1, -1, -1), reversed(self.people[:i])):
                if potential_child in person.children:
                    break
            else:
                if skip_if_not_found:
                    continue
                j = 0

            j = round(i + (j + 1 - i) * force)
            self.people.insert(j, self.people.pop(i))

    def _pull_children_down(
        self, 
        *, 
        force: float = 1.0, 
        p_skip: float = 0.0, 
        skip_if_not_found: bool = False,
    ) -> None:
        for i, person in enumerate(self.people):
            if random.random() < p_skip:
                continue
            for j, potential_parent in enumerate(self.people[i + 1:], start=i + 1):
                if potential_parent in person.parents.values():
                    break
            else:
                if skip_if_not_found:
                    continue
                j = len(self.people)

            j = round(i + (j - 1 - i) * force)
            self.people.insert(j, self.people.pop(i))

    def _compute_generations(self) -> None:
        for i, person in enumerate(self.people):
            for child in person.children:
                for potential_child in self.people[:i]:
                    if potential_child == child:
                        person.generation = max(person.generation, child.generation + 1)
                else:
                    continue

        for i, person in zip(range(len(self.people) - 1, -1, -1), reversed(self.people)):
            min_generation: int | None = None
            for parent in person.parents.values():
                for potential_parent in self.people[i:]:
                    if potential_parent == parent:
                        if min_generation is None or parent.generation < min_generation:
                            min_generation = parent.generation
            if min_generation is not None:
                person.generation = min_generation - 1
