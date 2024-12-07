from __future__ import annotations

from collections.abc import Iterator, Sequence
from itertools import zip_longest
from typing import Literal, overload, SupportsIndex

from genealogy.utils import ARROWS, ARROWS_ARITHMETIC


DEBUG = False


class Surface(list["SurfaceLine"]):
    """A 2D surface holding characters or None for empty spaces.

    It is made up of SurfaceLine objects, each representing a single line in the surface. It
    provides methods for drawing to the surface and for several transformations.
    """

    def compress_vertically(self) -> None:
        """Compress the surface vertically without affecting the connections.

        Works by finding clear paths from left to right that can be safely removed without affecting
        the structure of the rendered family tree.
        """
        self.pad_as_needed()

        debug_chars = "/*+.0#"
        paths_surface = Surface()
        visited: set[tuple[int, int]] = set()
        for i, line in enumerate(self):
            paths_surface.add_line()
            if line and line[0] is not None:
                continue

            new_path_surface = Surface()
            is_success = self._find_clear_path(SurfacePosition([i, 0]), new_path_surface, visited)
            if is_success:
                if DEBUG:
                    new_path_surface.replace_chars(debug_chars[i % len(debug_chars)])
                paths_surface += new_path_surface

        self[:] = paths_surface + self

        if not DEBUG:
            self._compress_from_clear_paths()

        self.strip()

    def _compress_from_clear_paths(self) -> None:
        """Compress the surface in place by removing the clear paths marked for removal.

        Transpose the surface, remove the marked characters, and transpose back.
        """
        self.transpose()
        self._remove_char(ARROWS["to_remove"])
        self.transpose()

    def transpose(self) -> None:
        """Transpose the surface, swapping rows and columns."""
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
        self[:] = transposed_lines

    def replace_chars(self, new_char: str) -> None:
        """Replace all characters in the surface with a new character.

        :param new_char: The character to replace existing characters with.
        """
        for line in self:
            line[:] = [new_char if char is not None else None for char in line]

    def pad_as_needed(self) -> None:
        """Pad all lines in the surface with None to ensure they are the same length."""
        max_length = max(len(line) for line in self)
        for line in self:
            line.extend([None for _ in range(max_length - len(line))])

    def strip(self) -> None:
        """Remove empty lines from the beginning and end of the surface, and trailing None values on each line."""
        new_surface = Surface()
        for line in self:
            line.rstrip()
            if line:
                new_surface.append(line)
        self[:] = new_surface

    def _remove_char(self, char_to_remove: str) -> None:
        """Remove all occurrences of a specific character from the surface.

        :param char_to_remove: The character to remove from the surface.
        """
        for line in self:
            line[:] = [char for char in line if char != char_to_remove]

    def _find_clear_path(
            self,
            pos: SurfacePosition,
            path_surface: Surface,
            visited: set[tuple[int, int]],
    ) -> bool:
        """Find a clear horizontal path through the surface starting from the given position.

        :param pos: The starting position of the path.
        :param path_surface: The surface to draw the path on.
        :param visited: Set of positions already visited.
        :return: True if a path to the end was found, False otherwise.
        """
        if pos.as_tuple() in visited:
            return False
        visited.add(pos.as_tuple())

        try:
            char_self = self[pos]
        except IndexError:
            char_self = None

        if char_self not in (None, ARROWS["middle"]):
            return False

        path_surface.draw(pos, ARROWS["to_remove"])

        if pos.index >= len(self[pos.line]) - 1:
            return True

        # Move up
        if pos.line > 0 and char_self is None:
            # N.B., we don't want to move up on anything but empty space
            new_pos = SurfacePosition([pos.line - 1, pos.index])
            if self._find_clear_path(new_pos, path_surface, visited):
                path_surface.draw(pos, (None,))
                visited.remove(pos.as_tuple())
                return True

        # Move right
        new_pos = SurfacePosition([pos.line, pos.index + 1])
        if self._find_clear_path(new_pos, path_surface, visited):
            return True

        # Move down
        if pos.line + 1 < len(self) and char_self is None:
            # N.B., we don't want to move down on anything but empty space
            new_pos = SurfacePosition([pos.line + 1, pos.index])
            if self._find_clear_path(new_pos, path_surface, visited):
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
        """Draw a sequence of characters at the specified position.

        :param pos: The position to start drawing at.
        :param iterable: The characters to draw.
        :param up_to: If True, the index is the last index to draw to.
        :return: True if drawing has overwritten existing characters.
        """
        if pos.line < 0:
            raise DrawError("line must be positive. ")

        self._extend_to_line(pos.line)
        has_overwritten = self[pos.line].draw(pos.index, iterable, up_to=up_to)
        return has_overwritten

    def add_line(self) -> None:
        """Add an empty line to the surface."""
        self.append(SurfaceLine())

    def _extend_to_line(self, line: int) -> None:
        """Extend the surface to ensure it has at least a certain number of lines.

        :param line: The line index to extend the surface to.
        """
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
        """Get a line, character, or slice of the surface.

        :param item: The index, slice, or position to get.
        :return: The line, character, or slice of the surface.
        """
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
        """Get the surface as a string, replacing None with spaces."""
        return "\n".join([line.as_str for line in self])


class SurfaceLine(list[str | None]):
    """A single line in the surface containing characters or None for empty spaces."""

    def draw(
            self,
            index: int,
            iterable: Sequence[str | None],
            *,
            up_to: bool = False,
    ) -> bool:
        """Draw a sequence of characters at the specified index.

        :param index: The index to start drawing at.
        :param iterable: The characters to write, one per index.
        :param up_to: If True, the index is the last index to draw to.
        :return: True if drawing has overwritten existing characters.
        """
        if up_to:
            index -= len(iterable)

        if index < 0:
            raise DrawError("index must be positive. ")

        if len(self) < index:
            self.extend([None for _ in range(index - len(self))])
        if len(self) == index:
            self.extend(iterable)
            return False

        has_overwritten = False
        for i, char in enumerate(iterable):
            if len(self) == index + i:
                self.append(char)
                continue

            prev_char = self[index + i]
            if prev_char is not None:
                if char != ARROWS["connection"]:
                    has_overwritten = True
                else:
                    # Special case, simple horizontal connections should never overwrite, so they
                    # appear to be behind other connection types.
                    continue
            self[index + i] = char
        return has_overwritten

    def rstrip(self) -> None:
        """Remove trailing None values from the line."""
        while self and self[-1] is None:
            self.pop()

    def __iadd__(self, other: Sequence[str | None]) -> SurfaceLine:
        """In-place add another sequence of characters to the line, filling-in None values.

        :param other: The sequence to add.
        :return: The updated line.
        """
        return self + other

    def __add__(self, other: Sequence[str | None]) -> SurfaceLine:
        """Add another sequence of characters to the line, filling-in None values.

        Existing characters are not overwritten.

        :param other: The sequence to add.
        :return: A new line containing the combined characters.
        """
        rtn = SurfaceLine()
        for char, other_char in zip_longest(self, other, fillvalue=None):
            if char is not None:
                rtn.append(char)
                continue

            rtn.append(other_char)
        return rtn

    @property
    def as_str(self) -> str:
        """Get the line as a string, replacing None with spaces.

        :return: The line as a string.
        """
        return "".join([char if char is not None else " " for char in self])


class ArrowsSurface(Surface):
    """Specialized surface for drawing connection arrows between family members."""

    def draw_connections(self, connections: ConnectionsType) -> None:
        """Draw all family connections using box-drawing characters.

        :param connections: The connections to draw, per generation and parental couple.
        """
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
        """Draw a vertical channel for a parental connection.

        :param generation: The generation number.
        :param channel: The channel index.
        :param start: The starting line index.
        :param end: The ending line index.
        """
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
            child_pos: SurfacePosition,
            channel: int,
    ) -> None:
        """Draw the connection from a child to a channel.

        :param child_pos: The position of the child.
        :param channel: The channel index.
        """
        connection_start_pos = child_pos.connection_tail
        connection_end_pos = child_pos.connection_right(channel)
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
        """Draw the connection from a parent to a channel.

        :param parent_pos: The position of the parent.
        :param child_generation: The generation index of the child.
        :param channel: The channel index.
        """
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
        """Determine the correct arrow character when drawing connections.

        :param pos: The current position.
        :param connection_arrow: The proposed arrow character.
        :return: The arrow character to use.
        """
        try:
            prev_arrow = self[pos.line][pos.index]
        except IndexError:
            prev_arrow = None

        if prev_arrow is None:
            return connection_arrow

        return ARROWS_ARITHMETIC[(prev_arrow, connection_arrow)]


class SurfacePosition(Sequence[int]):
    """Represents a position in the 2D surface with line and index coordinates.

    Provides utilities for calculating connection positions.
    """
    _generation_shift: int = 16
    _start_shift: int = 4
    _first_channel_shift: int = _start_shift + len(ARROWS["tail"])
    _additional_channel_shift: int = 2

    @classmethod
    def from_generation(cls, line: int, generation: int) -> SurfacePosition:
        """Create a SurfacePosition based on a line index and generation number.

        :param line: The line index.
        :param generation: The generation number.
        :return: The new `SurfacePosition`.
        """
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
        """Get the position where the connection of a child should end on the channel.

        :param channel: The channel index.
        :return: The position where the connection should end (the right of the child connection).
        """
        index = (
            self.index
            + self._first_channel_shift
            + channel * self._additional_channel_shift
        )
        return SurfacePosition([self.line, index])

    def connection_left(self, channel: int, child_generation: int) -> SurfacePosition:
        """Get the position where the connection of a parent should start on the channel.

        :param channel: The channel index.
        :param child_generation: The generation number of the child.
        :return: The position where the connection should start (the left of the parent connection).
        """
        index = (
            self._first_channel_shift
            + channel * self._additional_channel_shift
            + self._generation_shift * child_generation
        )
        return SurfacePosition([self.line, index])

    @property
    def connection_tail(self) -> SurfacePosition:
        """Get the position for drawing the tail of a connection (pointing to a parent).

        :return: The position to draw the tail.
        """
        return self + [0, self._start_shift]

    @property
    def connection_head(self) -> SurfacePosition:
        """Get the position for drawing the head of a connection (pointing to a child).

        :return: The position to draw the head.
        """
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
    """Represents a connection between a parental couple and their children."""

    def __init__(
            self,
            parent_coords: list[SurfacePosition] | None = None,
            child_coords: list[SurfacePosition] | None = None,
            allocated_channel: int | None = None,
    ):
        """Initialize a CoupleConnection.

        :param parent_coords: Positions of the parents on the surface.
        :param child_coords: Positions of the children on the surface.
        :param allocated_channel: The allocated channel index.
        """
        self.parent_coords = parent_coords if parent_coords is not None else []
        self.child_coords = child_coords if child_coords is not None else []
        self.allocated_channel = allocated_channel

    @property
    def min(self) -> int:
        """Get the minimum line index used by this connection.

        :return: The minimum line index.
        """
        return min(self.used_lines)

    @property
    def max(self) -> int:
        """Get the maximum line index used by this connection.

        :return: The maximum line index.
        """
        return max(self.used_lines)

    @property
    def used_lines(self) -> tuple[int, ...]:
        """Get all the line indices used by this connection.

        :return: The line indices.
        """
        return tuple([pos.line for pos in self.parent_coords + self.child_coords])


ConnectionsType = list[dict[tuple[str, ...], CoupleConnection]]


class DrawError(Exception):
    """Exception raised when drawing operations encounter an error."""
    pass
