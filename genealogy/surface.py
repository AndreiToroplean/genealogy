from __future__ import annotations

from itertools import zip_longest
from collections.abc import Iterable, Sequence

from genealogy.utils import ARROWS, ARROWS_ARITHMETIC


class Surface(list["SurfaceLine"]):
    def draw(
        self,
        pos: SurfacePosition,
        iterable: Sequence[str],
        *,
        up_to: bool = False,
        no_overwrite: bool = False,
    ) -> bool:
        if pos.line < 0:
            raise DrawError("line must be positive. ")

        self._extend_to_line(pos.line)
        has_collided = self[pos.line].draw(pos.index, iterable, up_to=up_to, no_overwrite=no_overwrite)
        return has_collided

    def add_line(self) -> None:
        self.append(SurfaceLine())

    def _extend_to_line(self, line: int) -> None:
        if len(self) <= line:
            self.extend([SurfaceLine() for _ in range(line - len(self) + 1)])

    def __add__(self, other: list[SurfaceLine]) -> Surface:
        rtn = Surface()
        for a_line, b_line in zip_longest(self, other, fillvalue=SurfaceLine()):
            rtn.append(a_line + b_line)
        return rtn

    @property
    def as_str(self) -> str:
        return "\n".join([line.as_str for line in self])


class SurfaceLine(list[str | None]):
    @classmethod
    def drawn(cls, index: int, iterable: Sequence[str]) -> SurfaceLine:
        self = cls()
        self.draw(index, iterable)
        return self

    def draw(
        self, 
        index: int, 
        iterable: Sequence[str],
        *, 
        up_to: bool = False, 
        no_overwrite: bool = False,
    ) -> bool:
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

    def __add__(self, other: list[str | None]) -> SurfaceLine:
        rtn = SurfaceLine()
        for arrow, other_arrow in zip_longest(self, other, fillvalue=None):
            if arrow is not None:
                rtn.append(arrow)
                continue

            rtn.append(other_arrow)
        return rtn

    @property
    def as_str(self) -> str:
        return "".join([arrow if arrow is not None else " " for arrow in self])


class ArrowsSurface(Surface):
    def draw_connections(self, connections: ConnectionsType) -> None:
        for generation, generation_connections in enumerate(connections):
            for couple_connection in generation_connections.values():
                assert couple_connection.allocated_channel is not None
                self._draw_channel(generation, couple_connection.allocated_channel, couple_connection.min, couple_connection.max)
                for child_coord in couple_connection.child_coords:
                    self._draw_child_connection(child_coord, couple_connection.allocated_channel)
                for parent_coord in couple_connection.parent_coords:
                    self._draw_parent_connection(parent_coord, generation, couple_connection.allocated_channel)

    def _draw_channel(
        self, 
        generation: int, 
        channel: int, 
        start: int, 
        end: int,
    ) -> None:
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

    def _draw_child_connection(
        self, 
        pos: SurfacePosition, 
        channel: int,
    ) -> None:
        connection_start_pos = pos.connection_tail
        connection_end_pos = pos.connection_right(channel)
        connection_len = connection_end_pos.index - connection_start_pos.index - len(ARROWS["tail"])
        arrow = (
            ARROWS["tail"]
            + ARROWS["connection"] * connection_len
            + self._get_connection_arrow(connection_end_pos, ARROWS["left"])
        )
        self.draw(connection_start_pos, arrow, no_overwrite=True)

    def _draw_parent_connection(
        self, 
        parent_pos: SurfacePosition, 
        child_generation: int, 
        channel: int,
    ) -> None:
        connection_start_pos = parent_pos.connection_left(channel, child_generation)
        connection_end_pos = parent_pos.connection_head
        connection_len = connection_end_pos.index - connection_start_pos.index - len(ARROWS["head"])
        arrow = (
            self._get_connection_arrow(connection_start_pos, ARROWS["right"])
            + ARROWS["connection"] * (connection_len - 1)
            + ARROWS["head"]
        )
        self.draw(connection_start_pos, arrow, no_overwrite=True)

    def _get_connection_arrow(
        self, 
        pos: SurfacePosition, 
        connection_arrow: str,
    ) -> str:
        try:
            prev_arrow = self[pos.line][pos.index]
        except IndexError:
            prev_arrow = None

        if prev_arrow is None:
            return connection_arrow

        return ARROWS_ARITHMETIC[(prev_arrow, connection_arrow)]


class SurfacePosition:
    _generation_shift: int = 16
    _start_shift: int = 4
    _first_channel_shift: int = _start_shift + len(ARROWS["tail"])
    _additional_channel_shift: int = 2

    @classmethod
    def from_generation(cls, line: int, generation: int) -> SurfacePosition:
        return SurfacePosition([line, generation * cls._generation_shift])

    def __init__(self, values: Sequence[int]) -> None:
        self.line = values[0]
        self.index = values[1]

    def __repr__(self) -> str:
        return f"SurfacePosition({self.line}, {self.index})"

    def __iter__(self) -> Iterable[int]:
        yield self.line
        yield self.index

    def __getitem__(self, key: int) -> int:
        if key == 0:
            return self.line
        elif key == 1:
            return self.index
        raise IndexError("SurfacePosition index out of range")

    def __add__(self, other: Sequence[int]) -> SurfacePosition:
        return SurfacePosition([self.line + other[0], self.index + other[1]])

    def __iadd__(self, other: Sequence[int]) -> SurfacePosition:
        self.line += other[0]
        self.index += other[1]
        return self

    def __sub__(self, other: Sequence[int]) -> SurfacePosition:
        return SurfacePosition([self.line - other[0], self.index - other[1]])

    def __isub__(self, other: Sequence[int]) -> SurfacePosition:
        self.line -= other[0]
        self.index -= other[1]
        return self

    def connection_right(self, channel: int) -> SurfacePosition:
        return self + [0, self._first_channel_shift + channel * self._additional_channel_shift]

    def connection_left(self, channel: int, child_generation: int) -> SurfacePosition:
        index = (
            self._first_channel_shift
            + channel * self._additional_channel_shift
            + self._generation_shift * child_generation
        )
        return SurfacePosition([self.line, index])

    @property
    def connection_tail(self) -> SurfacePosition:
        return self + [0, self._start_shift]

    @property
    def connection_head(self) -> SurfacePosition:
        return self


class CoupleConnection:
    def __init__(
            self,
            parent_coords: list[SurfacePosition] | None = None,
            child_coords: list[SurfacePosition] | None = None,
            allocated_channel: int | None = None,
    ):
        self.parent_coords = parent_coords if parent_coords is not None else []
        self.child_coords = child_coords if child_coords is not None else []
        self.allocated_channel = allocated_channel

    @property
    def min(self) -> int:
        return min(self.used_lines)

    @property
    def max(self) -> int:
        return max(self.used_lines)

    @property
    def used_lines(self) -> tuple[int, ...]:
        return tuple([pos.line for pos in self.parent_coords + self.child_coords])


ConnectionsType = list[dict[tuple[str, ...], CoupleConnection]]


class DrawError(Exception):
    pass
