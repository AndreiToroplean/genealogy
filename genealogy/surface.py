from __future__ import annotations

from collections.abc import Iterator, Sequence
from itertools import zip_longest
from typing import Literal, overload, SupportsIndex

from genealogy.utils import ARROWS, ARROWS_ARITHMETIC


DEBUG = False


class Surface(list["SurfaceLine"]):
    def compress_vertically(self) -> None:
        self.pad_as_needed()

        debug_chars = "/*+.0#"
        paths_surface = Surface()
        visited: set[tuple[int, int]] = set()
        for i, line in enumerate(self):
            paths_surface.add_line()
            if line and line[0] is not None:
                continue

            new_path_surface = Surface()
            is_success = self._find_clear_path(SurfacePosition([i, 0]), new_path_surface, paths_surface, visited)
            if is_success:
                if DEBUG:
                    new_path_surface.replace_chars(debug_chars[i % len(debug_chars)])
                paths_surface += new_path_surface

        self[:] = paths_surface + self

        if not DEBUG:
            self._compress_from_clear_paths()

        self.strip()

    def _compress_from_clear_paths(self) -> None:
        transposed_surface = self.transpose()
        transposed_surface._remove_char(ARROWS["to_remove"])
        compressed_surface = transposed_surface.transpose()
        self[:] = compressed_surface

    def transpose(self) -> Surface:
        max_length = max(len(line) for line in self)
        transposed_lines = []
        for i in range(max_length):
            new_line = SurfaceLine()
            for line in self:
                if i < len(line):
                    char = line[i]
                else:
                    char = None
                new_line.append(char)
            transposed_lines.append(new_line)
        return Surface(transposed_lines)

    def replace_chars(self, new_char: str) -> None:
        for line in self:
            line[:] = [new_char if char is not None else None for char in line]

    def pad_as_needed(self) -> None:
        max_length = max(len(line) for line in self)
        for line in self:
            line.extend([None for _ in range(max_length - len(line))])

    def strip(self) -> None:
        new_surface = Surface()
        for line in self:
            line.rstrip()
            if line:
                new_surface.append(line)
        self[:] = new_surface

    def _remove_char(self, char_to_remove: str) -> None:
        for line in self:
            line[:] = [char for char in line if char != char_to_remove]

    def _find_clear_path(
            self,
            pos: SurfacePosition,
            path_surface: Surface,
            existing_paths_surface: Surface,
            visited: set[tuple[int, int]],
    ) -> bool:
        if pos.as_tuple() in visited:
            return False
        visited.add(pos.as_tuple())

        try:
            char_self = self[pos]
        except IndexError:
            char_self = None
        char_existing = existing_paths_surface[pos]

        if char_self not in (None, ARROWS["middle"]) or char_existing is not None:
            return False

        path_surface.draw(pos, ARROWS["to_remove"])

        if pos.index >= len(self[pos.line]) - 1:
            return True

        # Move up
        if pos.line > 0 and char_self is None:
            # N.B., we don't want to move up on anything but empty space
            new_pos = SurfacePosition([pos.line - 1, pos.index])
            if self._find_clear_path(new_pos, path_surface, existing_paths_surface, visited):
                path_surface.draw(pos, (None,))
                visited.remove(pos.as_tuple())
                return True

        # Move right
        new_pos = SurfacePosition([pos.line, pos.index + 1])
        if self._find_clear_path(new_pos, path_surface, existing_paths_surface, visited):
            return True

        # Move down
        if pos.line + 1 < len(self) and char_self is None:
            # N.B., we don't want to move down on anything but empty space
            new_pos = SurfacePosition([pos.line + 1, pos.index])
            if self._find_clear_path(new_pos, path_surface, existing_paths_surface, visited):
                path_surface.draw(pos, (None,))
                visited.remove(pos.as_tuple())
                return True

        # Backtrack
        path_surface.draw(pos, (None,))
        return False

    def draw(
            self,
            pos: SurfacePosition,
            iterable: Sequence[str | None],
            *,
            up_to: bool = False,
    ) -> bool:
        if pos.line < 0:
            raise DrawError("line must be positive. ")

        self._extend_to_line(pos.line)
        has_collided = self[pos.line].draw(pos.index, iterable, up_to=up_to)
        return has_collided

    def add_line(self) -> None:
        self.append(SurfaceLine())

    def _extend_to_line(self, line: int) -> None:
        if len(self) <= line:
            self.extend([SurfaceLine() for _ in range(line - len(self) + 1)])

    def __iadd__(self, other: Sequence[SurfaceLine]) -> Surface:
        return self + other

    def __add__(self, other: Sequence[SurfaceLine]) -> Surface:
        rtn = Surface()
        for a_line, b_line in zip_longest(self, other, fillvalue=SurfaceLine()):
            rtn.append(a_line + b_line)
        return rtn

    @overload
    def __getitem__(self, item: int) -> SurfaceLine:
        ...

    @overload
    def __getitem__(self, item: slice) -> Surface:
        ...

    @overload
    def __getitem__(self, item: tuple[int, int]) -> str | None:
        ...

    @overload
    def __getitem__(self, item: SurfacePosition) -> str | None:
        ...

    def __getitem__(
            self,
            item: SupportsIndex | slice | tuple[int, int] | SurfacePosition
    ) -> Surface | SurfaceLine | str | None:
        if isinstance(item, Sequence):
            try:
                return self[item[0]][item[1]]
            except IndexError:
                return None

        if isinstance(item, slice):
            return self.__class__(super().__getitem__(item))

        return super().__getitem__(item)

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
            iterable: Sequence[str | None],
            *,
            up_to: bool = False,
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
        for i, char in enumerate(iterable):
            if len(self) == index + i:
                self.append(char)
                continue

            prev_char = self[index + i]
            if prev_char is not None:
                if char != ARROWS["connection"]:
                    has_collided = True
                else:
                    # Special case, simple horizontal connections should never overwrite, so they
                    # appear to be behind other connection types.
                    continue
            self[index + i] = char
        return has_collided

    def rstrip(self) -> None:
        while self and self[-1] is None:
            self.pop()

    def __iadd__(self, other: Sequence[str | None]) -> SurfaceLine:
        return self + other

    def __add__(self, other: Sequence[str | None]) -> SurfaceLine:
        rtn = SurfaceLine()
        for char, other_char in zip_longest(self, other, fillvalue=None):
            if char is not None:
                rtn.append(char)
                continue

            rtn.append(other_char)
        return rtn

    @property
    def as_str(self) -> str:
        return "".join([char if char is not None else " " for char in self])


class ArrowsSurface(Surface):
    def draw_connections(self, connections: ConnectionsType) -> None:
        for generation, generation_connections in enumerate(connections):
            for couple_connection in generation_connections.values():
                assert couple_connection.allocated_channel is not None
                self._draw_channel(
                    generation,
                    couple_connection.allocated_channel,
                    couple_connection.min,
                    couple_connection.max
                )
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
        self.draw(connection_start_pos, arrow)

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
        self.draw(connection_start_pos, arrow)

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


class SurfacePosition(Sequence[int]):
    _generation_shift: int = 16
    _start_shift: int = 4
    _first_channel_shift: int = _start_shift + len(ARROWS["tail"])
    _additional_channel_shift: int = 2

    @classmethod
    def from_generation(cls, line: int, generation: int) -> SurfacePosition:
        return SurfacePosition([line, generation * cls._generation_shift])

    def __init__(self, values: Sequence[int]) -> None:
        assert len(values) == 2
        self.line: int = values[0]
        self.index: int = values[1]

    def as_tuple(self) -> tuple[int, int]:
        return self.line, self.index

    def __repr__(self) -> str:
        return f"SurfacePosition({self.line}, {self.index})"

    def __iter__(self) -> Iterator[int]:
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

    def __len__(self) -> Literal[2]:
        return 2

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SurfacePosition):
            return NotImplemented
        return (self.line, self.index) == (other.line, other.index)

    def __lt__(self, other: SurfacePosition) -> bool:
        return (self.line, self.index) < (other.line, other.index)


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
