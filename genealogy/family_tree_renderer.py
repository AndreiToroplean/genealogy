from __future__ import annotations

from itertools import zip_longest

from genealogy.family_tree import FamilyTree
from genealogy.surface import ArrowsSurface, ConnectionsType, CoupleConnection, Surface, SurfacePosition, SurfaceLine
from genealogy.utils import ARROWS


class FamilyTreeRenderer:
    @classmethod
    def from_json(cls, family_tree_json: str) -> FamilyTreeRenderer:
        return cls(FamilyTree.from_json(family_tree_json))

    def __init__(self, family_tree: FamilyTree):
        self.family_tree = family_tree

        self._coords: dict[str, SurfacePosition] = {}
        self._names_surface: Surface = Surface()
        self._arrows_surface: ArrowsSurface = ArrowsSurface()
        self._surface: Surface = Surface()

    def render(self) -> str:
        self._draw_surf()
        return self._surface.as_str

    def _draw_surf(self) -> None:
        self._coords.clear()
        self._names_surface.clear()
        self._arrows_surface.clear()
        self._surface.clear()

        self._draw_names_surface()
        self._draw_arrows_surface()
        self._compress_surfaces_vertically()
        self._surface = self._names_surface + self._arrows_surface
        self._surface.add_line()

    def _draw_names_surface(self) -> None:
        prev_generation = -1
        line = 0
        for person in self.family_tree.people:
            line += 1 if person.generation > prev_generation else 2
            prev_generation = person.generation
            self._names_surface.draw(SurfacePosition.from_generation(line, person.generation), person.name)
            self._coords[person.id] = SurfacePosition.from_generation(line, person.generation)

    def _draw_arrows_surface(self) -> None:
        connections = self._generate_connections()
        connections = self._allocate_channels(connections)
        self._arrows_surface.draw_connections(connections)

    @staticmethod
    def _allocate_channels(connections: ConnectionsType) -> ConnectionsType:
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

    def _compress_surfaces_vertically(self) -> None:
        i = 0
        names_ended = False
        arrows_ended = False
        while True:
            try:
                names_line = self._names_surface[i]
            except IndexError:
                names_line = SurfaceLine()
                names_ended = True
            try:
                arrows_line = self._arrows_surface[i]
            except IndexError:
                arrows_line = SurfaceLine()
                arrows_ended = True
            if names_ended and arrows_ended:
                break

            if not set(arrows_line).issubset([ARROWS["middle"], None]):
                i += 1
                continue

            if not names_line:
                del self._names_surface[i]
                del self._arrows_surface[i]
                continue

            if i == 0:
                i += 1
                continue

            prev_arrows_line = self._arrows_surface[i - 1]
            prev_names_line = self._names_surface[i - 1]

            for name_arrow, prev_name_arrow, prev_arrow_arrow in zip_longest(
                    names_line, prev_names_line, prev_arrows_line, fillvalue=None):
                p, q, r = name_arrow is not None, prev_name_arrow is not None, prev_arrow_arrow is not None
                if p and q or p and r or q and p:
                    break

            else:
                del self._arrows_surface[i]
                self._names_surface[i - 1] = self._names_surface[i - 1] + names_line
                del self._names_surface[i]
                continue

            i += 1
