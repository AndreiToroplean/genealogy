from __future__ import annotations

from collections.abc import Iterable
import json
import random
import yaml

from genealogy.person import Person
from genealogy.utils import Relationship


class FamilyTree:
    """Manages a collection of Person objects and their relationships.

    Has methods to compute the generations of people and optimize the layout of the family tree, as
    well as methods to serialize and deserialize the data to and from JSON.
    """

    @classmethod
    def from_json(cls, json_data: str) -> FamilyTree:
        """Create a FamilyTree from a JSON string containing people and relationships.

        The JSON should have "people" mapping IDs to full names and "relationships" mapping
        child IDs to relationship types to parent IDs.

        :param json_data: The JSON string containing the family data.
        :return: A new `FamilyTree` instance created from the JSON data.
        """
        return cls._deserialize_data(json.loads(json_data))

    @classmethod
    def from_yaml(cls, yaml_data: str) -> FamilyTree:
        """Create a FamilyTree from a YAML string containing people and relationships.

        The YAML should have "people" mapping IDs to full names and "relationships" mapping
        child IDs to relationship types to parent IDs.

        :param yaml_data: The YAML string containing the family data.
        :return: A new `FamilyTree` instance created from the YAML data.
        """
        return cls._deserialize_data(yaml.safe_load(yaml_data))

    def __init__(self, people: Iterable[Person]):
        """Initialize the FamilyTree with a list of Person objects.

        :param people: An iterable of `Person` objects.
        """
        random.seed(0)

        self.people: list[Person] = sorted(people)
        self._compute_generations()
        self._relax()

    def to_json(self) -> str:
        """Serialize the FamilyTree to a JSON string.

        :return: The JSON representation of the FamilyTree.
        """
        return json.dumps(self._serialize_data(), indent=2)

    def to_yaml(self) -> str:
        """Serialize the FamilyTree to a YAML string.

        :return: The YAML representation of the FamilyTree.
        """
        return yaml.dump(self._serialize_data(), indent=2)

    def __repr__(self) -> str:
        people_str = ",\n    ".join([repr(person) for person in self.people])
        return f"FamilyTree([\n    {people_str}\n])"

    @classmethod
    def _deserialize_data(cls, data: dict) -> FamilyTree:
        """Helper method to create a FamilyTree from deserialized data.

        :param data: Dict containing people and relationships data.
        :return: A new FamilyTree instance.
        """
        people_dict: dict[str, Person] = {}

        # Create Person objects from people data
        for id_, name in data["people"].items():
            person = Person(id_, name)
            people_dict[id_] = person

        # Set up relationships and add any additional people mentioned in relationships
        for child_id, parents in data["relationships"].items():
            child = people_dict.setdefault(child_id, Person(child_id, child_id))
            for relationship, parent_id in parents.items():
                parent = people_dict.setdefault(parent_id, Person(parent_id, parent_id))
                child.parents[Relationship[relationship]] = parent
                parent.children.append(child)

        return cls(people_dict.values())

    def _serialize_data(self) -> dict:
        """Helper method to prepare data for serialization.

        :return: Dict containing people and relationships data.
        """
        return {
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

    def _compute_generations(self) -> None:
        """Compute the generation number for each person in the family tree.

        Start with 0 for the current generation offsprings. Modify the generation attribute of each
        Person based on their relationships.
        """
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
        """Sort the people in the family tree topologically."""
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
        """Optimize the ordering of people to reduce distance between people in the same parental cluster.

        :param n_iterations: Number of optimization iterations.
        :param force: Overall force scaling factor.
        :param children_force: Attractive force between parent and children.
        :param parents_force: Attractive force between child and parents.
        :param others_force: Attractive force between unrelated people. Would typically be negative.
        """
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
