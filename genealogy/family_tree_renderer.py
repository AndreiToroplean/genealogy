from itertools import zip_longest

from genealogy.family_tree import FamilyTree
from genealogy.surface import Surface, ArrowsSurface, SurfPos
from genealogy.utils import ARRS


class FamilyTreeRenderer:
    @classmethod
    def from_data(cls, family_tree_data: str) -> "FamilyTreeRenderer":
        return cls(FamilyTree.from_data(family_tree_data))

    def __init__(self, family_tree: FamilyTree):
        self.family_tree = family_tree

        self._coords = {}
        self._cxs = []
        self._names_surf = Surface()
        self._arrows_surf = ArrowsSurface()
        self._surf = Surface()
        self._draw_surf()

    def render(self) -> str:
        return self._surf.as_str

    def _draw_surf(self):
        self._draw_names_surf()
        self._draw_arrows_surf()
        self._compress_surfs_vertically()
        self._surf = self._names_surf + self._arrows_surf
        self._surf.add_line()

    def _draw_names_surf(self):
        prev_gen = -1
        line = 0
        for person in self.family_tree.people:
            line += 1 if person.generation > prev_gen else 2
            prev_gen = person.generation
            self._names_surf.draw(SurfPos.from_gen(line, person.generation), person.name)
            self._coords[person.id] = SurfPos.from_gen(line, person.generation)

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
        cxs = [{} for _ in set(person.generation for person in self.family_tree.people)]
        for person in self.family_tree.people:
            if not person.parents.values():
                continue

            c_coords = self._coords[person.id] + [1, 0]
            p_coords = [self._coords[parent.id] for parent in person.parents.values()]

            gen_cxs = cxs[person.generation]
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
