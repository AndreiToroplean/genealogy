from itertools import zip_longest

from genealogy.utils import ARRS, ARRS_ARITHMETIC


class Surface(list):
    def draw(self, pos, iterable, *, up_to=False, no_overwrite=False):
        if pos.line < 0:
            raise DrawError("line must be positive. ")

        self._extend_to_line(pos.line)
        has_collided = self[pos.line].draw(pos.index, iterable, up_to=up_to, no_overwrite=no_overwrite)
        return has_collided

    def add_line(self):
        self.append(SurfLine())

    def _extend_to_line(self, line):
        if len(self) <= line:
            self.extend([SurfLine() for _ in range(line - len(self) + 1)])

    def __add__(self, other):
        rtn = Surface()
        for a_line, b_line in zip_longest(self, other, fillvalue=SurfLine()):
            rtn.append(a_line + b_line)
        return rtn

    @property
    def as_str(self):
        return "\n".join([line.as_str for line in self])


class SurfLine(list):
    @classmethod
    def drawn(cls, index, iterable):
        self = cls()
        self.draw(index, iterable)
        return self

    def draw(self, index, iterable, *, up_to=False, no_overwrite=False):
        if up_to:
            index -= len(iterable)

        if index < 0:
            raise DrawError("index must be positive. ")

        if len(self) < index:
            self.extend([None for _ in range(index - len(self))])
        if len(self) == index:
            self.extend(iterable)
            return False

        has_collided = False
        for i, char in enumerate(iterable):
            if len(self) == index + i:
                self.append(char)
                continue

            prev_char = self[index + i]
            if prev_char is not None:
                has_collided = True
                if no_overwrite and char == ARRS["co"]:
                    continue
            self[index + i] = char
        return has_collided

    def __add__(self, other):
        rtn = SurfLine()
        for char, other_char in zip_longest(self, other, fillvalue=None):
            if char is not None:
                rtn.append(char)
                continue

            rtn.append(other_char)
        return rtn

    @property
    def as_str(self):
        return "".join([char if char is not None else " " for char in self])


class ArrowsSurface(Surface):
    def draw_connections(self, cxs):
        for gen, gen_cxs in enumerate(cxs):
            for cx in gen_cxs.values():
                p_coords, c_coords, cx_min, cx_max, channel = cx
                self._draw_channel(gen, channel, cx_min, cx_max)
                for c_coord in c_coords:
                    self._draw_child_co(c_coord, channel)
                for p_coord in p_coords:
                    self._draw_parent_co(p_coord, gen, channel)

    def _draw_channel(self, gen, channel, start, end):
        for line in range(start, end + 1):
            pos = SurfPos.from_gen(line, gen).co_right(channel)
            if line == start:
                if line == end:
                    self.draw(pos, ARRS["co"])
                    continue
                self.draw(pos, ARRS["start"])
            elif line == end:
                self.draw(pos, ARRS["end"])
            else:
                self.draw(pos, ARRS["middle"])

    def _draw_child_co(self, pos, channel):
        co_start_pos = pos.co_tail
        co_end_pos = pos.co_right(channel)
        co_len = co_end_pos.index - co_start_pos.index - len(ARRS["tail"])
        arr = ARRS["tail"] + ARRS["co"] * co_len + self._co_char(co_end_pos, ARRS["left"])
        self.draw(co_start_pos, arr, no_overwrite=True)

    def _draw_parent_co(self, p_pos, c_gen, channel):
        co_start_pos = p_pos.co_left(channel, c_gen)
        co_end_pos = p_pos.co_head
        co_len = co_end_pos.index - co_start_pos.index - len(ARRS["head"])
        arr = self._co_char(co_start_pos, ARRS["right"]) + ARRS["co"] * (co_len - 1) + ARRS["head"]
        self.draw(co_start_pos, arr, no_overwrite=True)

    def _co_char(self, pos, co_char):
        try:
            prev_char = self[pos.line][pos.index]
        except IndexError:
            prev_char = None

        if prev_char is None:
            return co_char

        return ARRS_ARITHMETIC[(prev_char, co_char)]


class SurfPos(list):
    _gen_shift = 16
    _start_shift = 4
    _first_channel_shift = _start_shift + len(ARRS["tail"])
    _add_channel_shift = 2

    @classmethod
    def from_gen(cls, line, gen):
        return SurfPos([line, gen * cls._gen_shift])

    def __add__(self, other):
        return SurfPos([p_dim + p_dim_other for p_dim, p_dim_other in zip(self, other)])

    def __iadd__(self, other):
        for dim in range(len(self)):
            self[dim] += other[dim]
        return self

    def __sub__(self, other):
        return SurfPos([p_dim - p_dim_other for p_dim, p_dim_other in zip(self, other)])

    def __isub__(self, other):
        for dim in range(len(self)):
            self[dim] -= other[dim]
        return self

    def co_right(self, channel):
        return self + [0, self._first_channel_shift + channel * self._add_channel_shift]

    def co_left(self, channel, c_gen):
        return SurfPos([self.line, self._first_channel_shift + channel * self._add_channel_shift + self._gen_shift * c_gen])

    @property
    def co_tail(self):
        return self + [0, self._start_shift]

    @property
    def co_head(self):
        return self

    @property
    def line(self):
        return self[0]

    @property
    def index(self):
        return self[1]


class DrawError(Exception):
    pass
