from __future__ import annotations

from collections.abc import Callable

from .utils import Relationship


class Person:
    """Represents a person in the family tree with their relationships and positioning info."""

    NEE: str = " ne.e "  # Class constant for maiden name separator

    def __init__(
            self,
            id_: str,
            name: str = "",
            parents: dict[Relationship, Person] | None = None,
            children: list[Person] | None = None,
            generation: int = 0,
            relax_position: float = 0.0,
    ):
        """Initialize a person with their ID, name, relationships and positioning.
        
        :param id_: Unique identifier for the person.
        :param name: Full name, optionally including maiden name after "ne.e".
        :param parents: Dictionary mapping relationship type to parent Person.
        :param children: List of child Person objects.
        :param generation: Generation number, starting with 0 for the current generation offsprings.
            Typically calculated by FamilyTree.
        :param relax_position: Vertical position in the family tree, used to optimize the layout.
            Typically calculated by FamilyTree.
        """
        self.id: str = id_
        self.first_name: str = ""
        self.last_name: str = ""
        self.middle_name: str = ""
        self.maiden_name: str = ""
        if name:
            self.name = name
        self.parents: dict[Relationship, Person] = parents if parents is not None else {}
        self.children: list[Person] = children if children is not None else []
        self.generation: int = generation
        self.relax_position: float = relax_position

    def __repr__(self) -> str:
        parents_repr = {rel.value: parent.id for rel, parent in self.parents.items()}
        children_repr = [child.id for child in self.children]
        return (
            f"Person(id={self.id!r}"
            f", name={self.name!r}"
            f", parents={parents_repr!r}"
            f", children={children_repr!r}"
            f", generation={self.generation!r}"
            f", relax_position={self.relax_position!r})"
        )

    @property
    def name(self) -> str:
        """Get the full formatted name including first, middle, last and maiden names."""
        return (
            f"{self.first_name}"
            f"{' ' + self.middle_name if self.middle_name else ''}"
            f" {self.last_name}"
            f"{f'{self.NEE}{self.maiden_name}' if self.maiden_name else ''}"
        )

    @name.setter
    def name(self, value: str) -> None:
        """Set the person's name, parsing first, middle, last, and maiden names.

        :param value: The full name, optionally including maiden name after 'ne.e'.
        """
        if self.NEE in value:
            name_part, maiden_name = value.split(self.NEE, 1)
            self.maiden_name = maiden_name.strip()
        else:
            name_part = value
            self.maiden_name = ''
        names = name_part.strip().split()
        self.first_name = names[0] if names else ''
        self.last_name = names[-1] if len(names) > 1 else ''
        self.middle_name = ' '.join(names[1:-1]) if len(names) > 2 else ''

    def __eq__(self, other: object) -> bool:
        """Check if two Person objects are equal based on their IDs.

        :param other: The other person to compare.
        :return: True if the IDs are equal, False otherwise.
        """
        if not isinstance(other, Person):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: object) -> bool:
        """Compare two Person objects for sorting purposes.

        :param other: The other person to compare.
        :return: True if self is less than other, based on the names.
        """
        if not isinstance(other, Person):
            return NotImplemented
        return (
            (self.last_name, self.maiden_name, self.first_name, self.middle_name)
            < (other.last_name, other.maiden_name, other.first_name, other.middle_name)
        )

    def traverse_parents_depth_first(
            self,
            visited: list[Person],
            func: Callable[[Person], None],
    ) -> bool:
        """Traverse the family tree depth-first through parents.

        :param visited: List of already visited Person objects.
        :param func: Function to apply to each Person.
        :return: True if the Person was not visited, False otherwise.
        """
        if self in visited:
            return False
        visited.append(self)

        for parent in self.parents.values():
            rtn = parent.traverse_parents_depth_first(visited, func)
            if rtn:
                func(parent)
        return True

    def traverse_children_depth_first(
            self,
            visited: list[Person],
            func: Callable[[Person], None],
    ) -> bool:
        """Traverse the family tree depth-first through children.

        :param visited: List of already visited Person objects.
        :param func: Function to apply to each Person.
        :return: True if the Person was not visited, False otherwise.
        """
        if self in visited:
            return False
        visited.append(self)

        for child in self.children:
            rtn = child.traverse_children_depth_first(visited, func)
            if rtn:
                func(child)
        return True
