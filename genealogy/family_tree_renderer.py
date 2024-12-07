from __future__ import annotations

from genealogy.family_tree import FamilyTree
from genealogy.surface import ArrowsSurface, ConnectionsType, CoupleConnection, Surface, SurfacePosition


class FamilyTreeRenderer:
    """Holds the data and methods to render a family tree.

    It uses FamilyTree objects to hold information about the people and their relationships, and
    Surface objects to render the different elements of the graphical representation as ASCII art.
    """

    @classmethod
    def from_json(cls, family_tree_json: str) -> FamilyTreeRenderer:
        """Create a FamilyTreeRenderer from a JSON string.

        :param family_tree_json: JSON string representing a family tree.
        :return: A new `FamilyTreeRenderer` object.
        """
        return cls(FamilyTree.from_json(family_tree_json))

    def __init__(self, family_tree: FamilyTree):
        """Initialize the FamilyTreeRenderer.

        :param family_tree: The `FamilyTree` object to render.
        """
        self.family_tree = family_tree

        self._coords: dict[str, SurfacePosition] = {}
        self._names_surface: Surface = Surface()
        self._arrows_surface: ArrowsSurface = ArrowsSurface()
        self._surface: Surface = Surface()

    def render(self) -> str:
        """Render the family tree using ASCII art.

        :return: The rendered family tree as a string.
        """
        self._coords.clear()
        self._names_surface.clear()
        self._arrows_surface.clear()
        self._surface.clear()

        self._draw_names_surface()
        self._draw_arrows_surface()
        self._surface = self._names_surface + self._arrows_surface
        self._surface.compress_vertically()
        self._surface.add_line()
        return self._surface.as_str

    def _draw_names_surface(self) -> None:
        """Render the surface containing the names of the people in the family tree.

        Position the names on the surface and record their coordinates.
        """
        line = 0
        for person in self.family_tree.people:
            self._names_surface.draw(SurfacePosition.from_generation(line, person.generation), person.name)
            self._coords[person.id] = SurfacePosition.from_generation(line, person.generation)
            line += 2

    def _draw_arrows_surface(self) -> None:
        """Render the surface containing the arrows connecting the people in the family tree."""
        connections = self._generate_connections()
        connections = self._allocate_channels(connections)
        self._arrows_surface.draw_connections(connections)

    @staticmethod
    def _allocate_channels(connections: ConnectionsType) -> ConnectionsType:
        """Allocate vertical channels to connect the children to their parents.

        A channel is a vertical line children connect to from the right and parents connect to from
        the left, for each parental cluster. Several channels can run in parallel to represent
        separate clusters with children from the same generation.

        :param connections: Connection objects per generation and parental couple.
        :return: The connection objects with the allocated channels.
        """
        for generation_connections in connections:
            channel_usages: list[list[tuple[int, int]]] = [[] for _ in generation_connections]
            for couple_connection in generation_connections.values():
                if couple_connection.allocated_channel is not None:
                    continue

                for potential_channel, usage_ranges in enumerate(channel_usages):
                    for usage_range in usage_ranges:
                        usage_min, usage_max = usage_range
                        if not (couple_connection.max < usage_min or usage_max < couple_connection.min):
                            break

                    else:
                        couple_connection.allocated_channel = potential_channel
                        usage_ranges.append((couple_connection.min, couple_connection.max))
                        break
        return connections

    def _generate_connections(self) -> ConnectionsType:
        """Generate the objects representing the connections in each parental cluster.
        
        :return: Connection objects per generation and parental couple.
        """
        connections: ConnectionsType = [{} for _ in {person.generation for person in self.family_tree.people}]
        for person in self.family_tree.people:
            if not person.parents.values():
                continue

            child_coords = self._coords[person.id] + [1, 0]
            parent_coords = [self._coords[parent.id] for parent in person.parents.values()]

            generation_connections = connections[person.generation]
            couple_id = tuple(sorted([parent.id for parent in person.parents.values()]))
            couple_connection = generation_connections.setdefault(couple_id, CoupleConnection(parent_coords))
            couple_connection.child_coords.append(child_coords)

        return connections
