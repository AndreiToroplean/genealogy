import random
from enum import Enum
from itertools import zip_longest

from person import Person
from surface import Surface, SurfPos, ArrowsSurface, arrs


class FamilyTree:
    def __init__(self):
        self.real_names = {}
        self.people = {}
        self.order = []
        self.gens = []
        self.coords = {}

        self._cxs = []
        self.names_surf = Surface()
        self.arrows_surf = ArrowsSurface()
        self.surf = Surface()

        data = self._read_data()
        self._generate_people(data)

    def draw(self):
        self._top_sort()
        self._generate_gens()
        self._draw_names_surf()
        self._draw_arrows_surf()
        self._compress_surfs_vertically()
        self.surf = self.names_surf + self.arrows_surf
        print(self.surf.as_str)

    def _read_data(self):
        data = []
        is_data = False
        with open("data.txt") as f:
            for line in f:
                if line.strip().startswith("#"):
                    continue

                if not line.strip():
                    is_data = True
                    continue

                if not is_data:
                    id_, name = [s.strip() for s in line.split(":")]
                    if id_ in self.real_names:
                        raise Exception(f"IDs must be unique. '{id_}' is repeated at least twice. ")

                    self.real_names[id_] = name
                    continue

                key, parent_id = line.split(":")
                child_id, rel = key.split(",")
                data.append((child_id.strip(), rel.strip(), parent_id.strip()))
        data.sort()
        return data

    def _generate_people(self, data):
        for child_id, rel, parent_id in data:
            if child_id not in self.people:
                child = Person(child_id)
                self.people[child_id] = child
                name = self.real_names[child_id]
                child.name = name
            else:
                child = self.people[child_id]
            if parent_id not in self.people:
                parent = Person(parent_id)
                self.people[parent_id] = parent
                name = self.real_names[parent_id]
                parent.name = name
            else:
                parent = self.people[parent_id]

            child.parents.append(parent)
            child.rels.append(Rel[rel])

            parent.children.append(child)

    def _p_dfs(self, person, visited):
        if person in visited: return False
        visited.append(person)

        for parent in person.parents:
            r = self._p_dfs(parent, visited)
            if not r: continue
            self.order.append(parent)
        return True

    def _c_dfs(self, person, visited):
        if person in visited: return False
        visited.append(person)

        for child in person.children:
            r = self._c_dfs(child, visited)
            if not r: continue
            self.order.append(child)
            return True

    def _top_sort(self):
        visited = []
        while True:
            for node in self.people.values():
                if node not in visited:
                    break

            else:
                break

            self._p_dfs(node, visited)
            self.order.append(node)

        self.order.reverse()

        for i, person in enumerate(self.order):
            for j, pot_child in reversed(list(enumerate(self.order[:i]))):
                if pot_child in person.children:
                    break
            else:
                j = -1

            self.order.insert(j + 1, self.order.pop(i))

    def _generate_gens(self):
        self.gens = [0 for p in self.order]
        for i, person in enumerate(self.order):
            for child in person.children:
                for j, pot_child in enumerate(self.order[:i]):
                    if pot_child == child:
                        break
                else:
                    continue
                self.gens[i] = max(self.gens[i], self.gens[j] + 1)

    def _draw_names_surf(self):
        prev_gen = -1
        line = 0
        for person, gen in zip(self.order, self.gens):
            line += 1 if gen > prev_gen else 2
            prev_gen = gen
            self.names_surf.draw(SurfPos.from_gen(line, gen), person.name + " ")
            self.coords[person.id] = SurfPos.from_gen(line, gen)

    def _draw_arrows_surf(self):
        cxs = self._generate_cxs()
        cxs = self._allocate_channels(cxs)
        self.arrows_surf.draw_connections(cxs, self.names_surf)

    @staticmethod
    def _allocate_channels(cxs):
        for gen, gen_cxs in enumerate(cxs):
            gen_cxs = list(gen_cxs.values())
            for cx in gen_cxs:
                cx_lines = list(zip(*cx[0], *cx[1]))[0]
                cx.extend([min(cx_lines), max(cx_lines), None])
            gen_cxs.sort(key=lambda a: a[3] - a[2])

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
        cxs = [{} for _ in set(self.gens)]
        for person, gen in zip(self.order, self.gens):
            parents = person.parents
            if not parents:
                continue

            c_coords = self.coords[person.id] + [1, 0]
            p_coords = [self.coords[parent.id] for parent in parents]

            gen_cxs = cxs[gen]
            couple_id = tuple(sorted([parent.id for parent in parents]))
            try:
                cx = gen_cxs[couple_id]
            except KeyError:
                gen_cxs[couple_id] = [p_coords, [c_coords]]
            else:
                cx[1].append(c_coords)

        return cxs

    def _compress_surfs_vertically(self):
        for i, (names_line, arrows_line) in enumerate(zip_longest(self.names_surf, self.arrows_surf, fillvalue=[])):
            if not set(arrows_line).issubset([arrs["middle"], None]):
                continue

            while True:
                if not names_line:
                    del self.names_surf[i]
                    del self.arrows_surf[i]
                    names_line = self.names_surf[i]
                    arrows_line = self.arrows_surf[i]
                    continue

                try:
                    prev_arrows_line = self.arrows_surf[i-1]
                    prev_names_line = self.names_surf[i-1]
                except IndexError:
                    break

                for nam_c, prev_nam_c, prev_arr_c in zip_longest(names_line, prev_names_line, prev_arrows_line, fillvalue=None):
                    p, q, r = nam_c is not None, prev_nam_c is not None, prev_arr_c is not None
                    if p and q or p and r or q and p:
                        break

                else:
                    del self.arrows_surf[i]
                    self.names_surf[i-1] = self.names_surf[i-1] + names_line
                    del self.names_surf[i]
                    names_line = self.names_surf[i]
                    arrows_line = self.arrows_surf[i]
                    continue

                break


class Rel(Enum):
    F = "father"
    M = "mother"
    AF = "adoptive father"
    AM = "adoptive mother"
