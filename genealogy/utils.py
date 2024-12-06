from __future__ import annotations

from enum import Enum


class Relationship(Enum):
    F: str = "father"
    M: str = "mother"
    AF: str = "adoptive father"
    AM: str = "adoptive mother"


ARROWS: dict[str, str] = {
    "tail": "╘═",
    "head": "═ ",
    "connection": "═",
    "right": "╞",
    "left": "╡",
    "middle": "║",
    "start": "╥",
    "end": "╨",
    "left_start": "╗",
    "left_end": "╝",
    "left_middle": "╣",
    "right_start": "╔",
    "right_end": "╚",
    "right_middle": "╠",
    "both_start": "╦",
    "both_end": "╩",
    "both_middle": "╬",
    "to_remove": "#",
}

ARROWS_ARITHMETIC: dict[tuple[str, str], str] = {
    (ARROWS["start"], ARROWS["left"]): ARROWS["left_start"],
    (ARROWS["start"], ARROWS["right"]): ARROWS["right_start"],
    (ARROWS["end"], ARROWS["left"]): ARROWS["left_end"],
    (ARROWS["end"], ARROWS["right"]): ARROWS["right_end"],
    (ARROWS["middle"], ARROWS["left"]): ARROWS["left_middle"],
    (ARROWS["middle"], ARROWS["right"]): ARROWS["right_middle"],
    (ARROWS["right_start"], ARROWS["left"]): ARROWS["both_start"],
    (ARROWS["right_end"], ARROWS["left"]): ARROWS["both_end"],
    (ARROWS["right_middle"], ARROWS["left"]): ARROWS["both_middle"],
    (ARROWS["left_start"], ARROWS["right"]): ARROWS["both_start"],
    (ARROWS["left_end"], ARROWS["right"]): ARROWS["both_end"],
    (ARROWS["left_middle"], ARROWS["right"]): ARROWS["both_middle"],
    (ARROWS["connection"], ARROWS["right"]): ARROWS["connection"],
    (ARROWS["connection"], ARROWS["left"]): ARROWS["connection"],
}
