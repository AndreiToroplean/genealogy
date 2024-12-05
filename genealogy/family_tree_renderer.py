from itertools import zip_longest

from genealogy.family_tree import FamilyTree
from genealogy.surface import Surface, ArrowsSurface, SurfacePosition
from genealogy.utils import ARROWS


class FamilyTreeRenderer:
    @classmethod
    def from_json(cls, family_tree_json: str) -> "FamilyTreeRenderer":
        return cls(FamilyTree.from_json(family_tree_json))

    def __init__(self, family_tree: FamilyTree):
        self.family_tree = family_tree

        self._coords = None
        self._connections = None
        self._names_surface = None
        self._arrows_surface = None
        self._surface = None

    def render(self) -> str:
        self._draw_surf()
        return self._surface.as_str

    def _draw_surf(self):
        self._coords = {}
        self._connections = []
        self._names_surface = Surface()
        self._arrows_surface = ArrowsSurface()
        self._surface = Surface()

        self._draw_names_surface()
        self._draw_arrows_surface()
        self._compress_surfaces_vertically()
        self._surface = self._names_surface + self._arrows_surface
        self._surface.add_line()

    def _draw_names_surface(self):
        prev_generation = -1
        line = 0
        for person in self.family_tree.people:
            line += 1 if person.generation > prev_generation else 2
            prev_generation = person.generation
            self._names_surface.draw(SurfacePosition.from_generation(line, person.generation), person.name)
            self._coords[person.id] = SurfacePosition.from_generation(line, person.generation)

    def _draw_arrows_surface(self):
        connections = self._generate_connections()
        connections = self._allocate_channels(connections)
        self._arrows_surface.draw_connections(connections)

    @staticmethod
    def _allocate_channels(connections):
        for generation, generation_connections in enumerate(connections):
            generation_connections = list(generation_connections.values())
            for connection in generation_connections:
                connection_lines = list(zip(*connection[0], *connection[1]))[0]
                connection.extend([min(connection_lines), max(connection_lines), None])

            channel_usages = [[] for _ in generation_connections]
            for connection in generation_connections:
                _, _, connection_min, connection_max, channel = connection
                if channel is not None:
                    continue

                for potential_channel, usage_ranges in enumerate(channel_usages):
                    for usage_range in usage_ranges:
                        usage_min, usage_max = usage_range
                        if not (connection_max < usage_min or usage_max < connection_min):
                            break

                    else:
                        connection[4] = potential_channel
                        usage_ranges.append((connection_min, connection_max))
                        break
        return connections

    def _generate_connections(self):
        connections = [{} for _ in set(person.generation for person in self.family_tree.people)]
        for person in self.family_tree.people:
            if not person.parents.values():
                continue

            child_coords = self._coords[person.id] + [1, 0]
            parent_coords = [self._coords[parent.id] for parent in person.parents.values()]

            generation_connections = connections[person.generation]
            couple_id = tuple(sorted([parent.id for parent in person.parents.values()]))
            try:
                connection = generation_connections[couple_id]
            except KeyError:
                generation_connections[couple_id] = [parent_coords, [child_coords]]
            else:
                connection[1].append(child_coords)

        return connections

    def _compress_surfaces_vertically(self):
        i = 0
        names_ended = False
        arrows_ended = False
        while True:
            try:
                names_line = self._names_surface[i]
            except IndexError:
                names_line = []
                names_ended = True
            try:
                arrows_line = self._arrows_surface[i]
            except IndexError:
                arrows_line = []
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
