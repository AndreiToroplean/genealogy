from itertools import zip_longest
from math import inf
import random

from genealogy.person import Person
from genealogy.surface import ArrowsSurface, Surface, SurfPos
from genealogy.utils import ARRS, Rel


class FamilyTree:
    def __init__(self, data):
        random.seed(0)

        self._people: list[Person] = []
        self._order = []
        self._gens = []
        self._coords = {}

        self._cxs = []
        self._names_surf = Surface()
        self._arrows_surf = ArrowsSurface()
        self._surf = Surface()

        people_dict, relationships = self._parse_data(data)
        self._people = self._generate_people(people_dict, relationships)

        self._draw_surf()

    def draw(self):
        print(self._surf.as_str)

    @property
    def as_str(self):
        return self._surf.as_str

    def _draw_surf(self):
        self._augmented_top_sort()
        self._generate_gens()
        self._draw_names_surf()
        self._draw_arrows_surf()
        self._compress_surfs_vertically()
        self._surf = self._names_surf + self._arrows_surf
        self._surf.add_line()

    @staticmethod
    def _parse_data(data):
        people_dict = {}
        relationships = []
        is_data = False  # Whether the line represents relationship data, as opposed to IDs.
        for line in data.splitlines():
            line = line.strip()
            if line.startswith("#"):
                continue

            if not line:
                # After a line skip, we consider lines to be relationship data.
                is_data = True
                continue

            if not is_data:
                # Parse IDs and create Person objects
                id_, name = [s.strip() for s in line.split(":")]
                if id_ in people_dict:
                    raise Exception(f"IDs must be unique. '{id_}' is repeated.")
                person = Person(id_)
                person.set_names_from_str(name)
                people_dict[id_] = person
            else:
                # Parse relationships
                key, parent_id = line.split(":")
                child_id, rel = key.split(",")
                relationships.append((child_id.strip(), rel.strip(), parent_id.strip()))
        relationships.sort()
        return people_dict, relationships

    @staticmethod
    def _generate_people(people_dict, relationships):
        for child_id, rel, parent_id in relationships:
            # Get or create child
            child = people_dict.get(child_id)
            if not child:
                child = Person(child_id)
                child.set_names_from_str(child_id)
                people_dict[child_id] = child

            # Get or create parent
            parent = people_dict.get(parent_id)
            if not parent:
                parent = Person(parent_id)
                parent.set_names_from_str(parent_id)
                people_dict[parent_id] = parent

            # Add relationships
            child.parents[Rel[rel]] = parent
            parent.children.append(child)

        return sorted(people_dict.values(), key=lambda p: (p.last_name, p.maiden_name))

    def _p_dfs(self, person, visited):
        if person in visited: return False
        visited.append(person)

        for parent in person.parents.values():
            r = self._p_dfs(parent, visited)
            if not r: continue
            self._order.append(parent)
        return True

    def _c_dfs(self, person, visited):
        if person in visited: return False
        visited.append(person)

        for child in person.children:
            r = self._c_dfs(child, visited)
            if not r: continue
            self._order.append(child)
            return True

    def _augmented_top_sort(self, n_iterations=64):
        visited = []
        while True:
            for node in self._people:
                if node not in visited:
                    break

            else:
                break

            self._p_dfs(node, visited)
            self._order.append(node)

        self._order.reverse()

        for i in range(n_iterations):
            self._pull_children_down(p_skip=0.0, skip_if_not_found=True)
            self._pull_parents_up(p_skip=0.0, skip_if_not_found=True)

    def _pull_parents_up(self, *, force=1.0, p_skip=0.0, skip_if_not_found=False):
        for i, person in enumerate(self._order):
            if random.random() < p_skip:
                continue
            for j, pot_child in zip(range(len(self._order[:i]) - 1, -1, -1), reversed(self._order[:i])):
                if pot_child in person.children:
                    break
            else:
                if skip_if_not_found:
                    continue
                j = 0

            j = round(i + (j + 1 - i) * force)
            self._order.insert(j, self._order.pop(i))

    def _pull_children_down(self, *, force=1.0, p_skip=0.0, skip_if_not_found=False):
        for i, person in enumerate(self._order):
            if random.random() < p_skip:
                continue
            for j, pot_parent in enumerate(self._order[i + 1:], start=i + 1):
                if pot_parent in person.parents.values():
                    break
            else:
                if skip_if_not_found:
                    continue
                j = len(self._order)

            j = round(i + (j - 1 - i) * force)
            self._order.insert(j, self._order.pop(i))

    def _generate_gens(self):
        self._gens = [0 for _ in self._order]
        for i, person in enumerate(self._order):
            for child in person.children:
                for j, pot_child in enumerate(self._order[:i]):
                    if pot_child == child:
                        break
                else:
                    continue
                self._gens[i] = max(self._gens[i], self._gens[j] + 1)

        for i, person in zip(range(len(self._order) - 1, -1, -1), reversed(self._order)):
            min_gen = inf
            for parent in person.parents.values():
                for j, pot_parent in enumerate(self._order[i:], start=i):
                    if pot_parent == parent:
                        min_gen = min(min_gen, self._gens[j])
            if min_gen != inf:
                self._gens[i] = min_gen - 1

    def _draw_names_surf(self):
        prev_gen = -1
        line = 0
        for person, gen in zip(self._order, self._gens):
            line += 1 if gen > prev_gen else 2
            prev_gen = gen
            self._names_surf.draw(SurfPos.from_gen(line, gen), person.name)
            self._coords[person.id] = SurfPos.from_gen(line, gen)

    def _draw_arrows_surf(self):
        cxs = self._generate_cxs()
        cxs = self._allocate_channels(cxs)
        self._arrows_surf.draw_connections(cxs, self._names_surf)

    @staticmethod
    def _allocate_channels(cxs):
        for gen, gen_cxs in enumerate(cxs):
            gen_cxs = list(gen_cxs.values())
            for cx in gen_cxs:
                cx_lines = list(zip(*cx[0], *cx[1]))[0]
                cx.extend([min(cx_lines), max(cx_lines), None])

            chs_usages = [[] for _ in gen_cxs]
            for cx in gen_cxs:
                _, _, cx_min, cx_max, channel = cx
                if channel is not None:
                    continue

                for pot_ch, ch_usages in enumerate(chs_usages):
                    for usage in ch_usages:
                        us_min, us_max = usage
                        if not (cx_max < us_min or us_max < cx_min):
                            break

                    else:
                        cx[4] = pot_ch
                        ch_usages.append((cx_min, cx_max))
                        break
        return cxs

    def _generate_cxs(self):
        cxs = [{} for _ in set(self._gens)]
        for person, gen in zip(self._order, self._gens):
            if not person.parents.values():
                continue

            c_coords = self._coords[person.id] + [1, 0]
            p_coords = [self._coords[parent.id] for parent in person.parents.values()]

            gen_cxs = cxs[gen]
            couple_id = tuple(sorted([parent.id for parent in person.parents.values()]))
            try:
                cx = gen_cxs[couple_id]
            except KeyError:
                gen_cxs[couple_id] = [p_coords, [c_coords]]
            else:
                cx[1].append(c_coords)

        return cxs

    def _compress_surfs_vertically(self):
        i = 0
        names_ended = False
        arrows_ended = False
        while True:
            try:
                names_line = self._names_surf[i]
            except IndexError:
                names_line = []
                names_ended = True
            try:
                arrows_line = self._arrows_surf[i]
            except IndexError:
                arrows_line = []
                arrows_ended = True
            if names_ended and arrows_ended:
                break

            if not set(arrows_line).issubset([ARRS["middle"], None]):
                i += 1
                continue

            if not names_line:
                del self._names_surf[i]
                del self._arrows_surf[i]
                continue

            if i == 0:
                i += 1
                continue

            prev_arrows_line = self._arrows_surf[i - 1]
            prev_names_line = self._names_surf[i - 1]

            for nam_c, prev_nam_c, prev_arr_c in zip_longest(names_line, prev_names_line, prev_arrows_line, fillvalue=None):
                p, q, r = nam_c is not None, prev_nam_c is not None, prev_arr_c is not None
                if p and q or p and r or q and p:
                    break

            else:
                del self._arrows_surf[i]
                self._names_surf[i - 1] = self._names_surf[i - 1] + names_line
                del self._names_surf[i]
                continue

            i += 1
