from collections.abc import Iterable
import json
from math import inf
import random

from genealogy.person import Person
from genealogy.utils import Rel


class FamilyTree:
    @classmethod
    def from_json(cls, json_data: str) -> "FamilyTree":
        data = json.loads(json_data)
        people_dict = {}
        
        # Create all Person objects
        for id_, name in data["people"].items():
            person = Person(id_, name)
            people_dict[id_] = person
            
        # Set up relationships
        for child_id, parents in data["relationships"].items():
            child = people_dict[child_id]
            for rel, parent_id in parents.items():
                parent = people_dict[parent_id]
                child.parents[Rel[rel]] = parent
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

    def __repr__(self):
        people_str = ",\n    ".join([repr(person) for person in self.people])
        return f"FamilyTree([\n    {people_str}\n])"

    def _perform_augmented_top_sort(self, n_iterations=64):
        visited = []
        sorted_nodes = []
        while True:
            for node in self.people:
                if node not in visited:
                    break

            else:
                break

            self._p_dfs(node, visited, sorted_nodes)
            sorted_nodes.append(node)

        sorted_nodes.reverse()
        self.people[:] = sorted_nodes

        for i in range(n_iterations):
            self._pull_children_down(p_skip=0.0, skip_if_not_found=True)
            self._pull_parents_up(p_skip=0.0, skip_if_not_found=True)

    @staticmethod
    def _p_dfs(person, visited, sorted_nodes):
        if person in visited: return False
        visited.append(person)

        for parent in person.parents.values():
            r = FamilyTree._p_dfs(parent, visited, sorted_nodes)
            if not r: continue
            sorted_nodes.append(parent)
        return True

    @staticmethod
    def _c_dfs(person, visited, sorted_nodes):
        if person in visited: return False
        visited.append(person)

        for child in person.children:
            r = FamilyTree._c_dfs(child, visited)
            if not r: continue
            sorted_nodes.append(child)
            return True

    def _pull_parents_up(self, *, force=1.0, p_skip=0.0, skip_if_not_found=False):
        for i, person in enumerate(self.people):
            if random.random() < p_skip:
                continue
            for j, pot_child in zip(range(len(self.people[:i]) - 1, -1, -1), reversed(self.people[:i])):
                if pot_child in person.children:
                    break
            else:
                if skip_if_not_found:
                    continue
                j = 0

            j = round(i + (j + 1 - i) * force)
            self.people.insert(j, self.people.pop(i))

    def _pull_children_down(self, *, force=1.0, p_skip=0.0, skip_if_not_found=False):
        for i, person in enumerate(self.people):
            if random.random() < p_skip:
                continue
            for j, pot_parent in enumerate(self.people[i + 1:], start=i + 1):
                if pot_parent in person.parents.values():
                    break
            else:
                if skip_if_not_found:
                    continue
                j = len(self.people)

            j = round(i + (j - 1 - i) * force)
            self.people.insert(j, self.people.pop(i))

    def _compute_generations(self):
        for i, person in enumerate(self.people):
            for child in person.children:
                for pot_child in self.people[:i]:
                    if pot_child == child:
                        person.generation = max(person.generation, pot_child.generation + 1)
                else:
                    continue

        for i, person in zip(range(len(self.people) - 1, -1, -1), reversed(self.people)):
            min_gen = inf
            for parent in person.parents.values():
                for pot_parent in self.people[i:]:
                    if pot_parent == parent:
                        min_gen = min(min_gen, pot_parent.generation)
            if min_gen != inf:
                person.generation = min_gen - 1
