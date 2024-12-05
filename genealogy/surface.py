from itertools import zip_longest

from genealogy.utils import ARROWS, ARROWS_ARITHMETIC


class Surface(list):
    def draw(self, pos, iterable, *, up_to=False, no_overwrite=False):
        if pos.line < 0:
            raise DrawError("line must be positive. ")

        self._extend_to_line(pos.line)
        has_collided = self[pos.line].draw(pos.index_, iterable, up_to=up_to, no_overwrite=no_overwrite)
        return has_collided

    def add_line(self):
        self.append(SurfaceLine())

    def _extend_to_line(self, line):
        if len(self) <= line:
            self.extend([SurfaceLine() for _ in range(line - len(self) + 1)])

    def __add__(self, other):
        rtn = Surface()
        for a_line, b_line in zip_longest(self, other, fillvalue=SurfaceLine()):
            rtn.append(a_line + b_line)
        return rtn

    @property
    def as_str(self):
        return "\n".join([line.as_str for line in self])


class SurfaceLine(list):
    @classmethod
    def drawn(cls, index, iterable):
        self = cls()
        self.draw(index, iterable)
        return self

    def draw(self, index, iterable, *, up_to=False, no_overwrite=False):
        if up_to:
            index -= len(iterable)

        if index < 0:
            raise DrawError("index_ must be positive. ")

        if len(self) < index:
            self.extend([None for _ in range(index - len(self))])
        if len(self) == index:
            self.extend(iterable)
            return False

        has_collided = False
        for i, arrow in enumerate(iterable):
            if len(self) == index + i:
                self.append(arrow)
                continue

            prev_arrow = self[index + i]
            if prev_arrow is not None:
                has_collided = True
                if no_overwrite and arrow == ARROWS["connection"]:
                    continue
            self[index + i] = arrow
        return has_collided

    def __add__(self, other):
        rtn = SurfaceLine()
        for arrow, other_arrow in zip_longest(self, other, fillvalue=None):
            if arrow is not None:
                rtn.append(arrow)
                continue

            rtn.append(other_arrow)
        return rtn

    @property
    def as_str(self):
        return "".join([arrow if arrow is not None else " " for arrow in self])


class ArrowsSurface(Surface):
    def draw_connections(self, connections):
        for generation, generation_connections in enumerate(connections):
            for connection in generation_connections.values():
                parent_coords, child_coords, connection_min, connection_max, channel = connection
                self._draw_channel(generation, channel, connection_min, connection_max)
                for child_coord in child_coords:
                    self._draw_child_connection(child_coord, channel)
                for parent_coord in parent_coords:
                    self._draw_parent_connection(parent_coord, generation, channel)

    def _draw_channel(self, generation, channel, start, end):
        for line in range(start, end + 1):
            pos = SurfacePosition.from_generation(line, generation).connection_right(channel)
            if line == start:
                if line == end:
                    self.draw(pos, ARROWS["connection"])
                    continue
                self.draw(pos, ARROWS["start"])
            elif line == end:
                self.draw(pos, ARROWS["end"])
            else:
                self.draw(pos, ARROWS["middle"])

    def _draw_child_connection(self, pos, channel):
        connection_start_pos = pos.connection_tail
        connection_end_pos = pos.connection_right(channel)
        connection_len = connection_end_pos.index_ - connection_start_pos.index_ - len(ARROWS["tail"])
        arrow = (
            ARROWS["tail"]
            + ARROWS["connection"] * connection_len
            + self._get_connection_arrow(connection_end_pos, ARROWS["left"])
        )
        self.draw(connection_start_pos, arrow, no_overwrite=True)

    def _draw_parent_connection(self, parent_pos, child_generation, channel):
        connection_start_pos = parent_pos.connection_left(channel, child_generation)
        connection_end_pos = parent_pos.connection_head
        connection_len = connection_end_pos.index_ - connection_start_pos.index_ - len(ARROWS["head"])
        arrow = (
            self._get_connection_arrow(connection_start_pos, ARROWS["right"])
            + ARROWS["connection"] * (connection_len - 1)
            + ARROWS["head"]
        )
        self.draw(connection_start_pos, arrow, no_overwrite=True)

    def _get_connection_arrow(self, pos, connection_arrow):
        try:
            prev_arrow = self[pos.line][pos.index_]
        except IndexError:
            prev_arrow = None

        if prev_arrow is None:
            return connection_arrow

        return ARROWS_ARITHMETIC[(prev_arrow, connection_arrow)]


class SurfacePosition(list):
    _generation_shift = 16
    _start_shift = 4
    _first_channel_shift = _start_shift + len(ARROWS["tail"])
    _additional_channel_shift = 2

    @classmethod
    def from_generation(cls, line, generation):
        return SurfacePosition([line, generation * cls._generation_shift])

    def __add__(self, other):
        return SurfacePosition([p_dim + p_dim_other for p_dim, p_dim_other in zip(self, other)])

    def __iadd__(self, other):
        for dim in range(len(self)):
            self[dim] += other[dim]
        return self

    def __sub__(self, other):
        return SurfacePosition([p_dim - p_dim_other for p_dim, p_dim_other in zip(self, other)])

    def __isub__(self, other):
        for dim in range(len(self)):
            self[dim] -= other[dim]
        return self

    def connection_right(self, channel):
        return self + [0, self._first_channel_shift + channel * self._additional_channel_shift]

    def connection_left(self, channel, child_generation):
        index = (
            self._first_channel_shift
            + channel * self._additional_channel_shift
            + self._generation_shift * child_generation
        )
        return SurfacePosition([self.line, index])

    @property
    def connection_tail(self):
        return self + [0, self._start_shift]

    @property
    def connection_head(self):
        return self

    @property
    def line(self):
        return self[0]

    @property
    def index_(self):
        return self[1]


class DrawError(Exception):
    pass
