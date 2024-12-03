from enum import Enum


class Rel(Enum):
    F = "father"
    M = "mother"
    AF = "adoptive father" 
    AM = "adoptive mother"


ARRS = {
        "tail": "╘═",
        "head": "═ ",
        "co": "═",
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
        }

ARRS_ARITHMETIC = {
    (ARRS["start"], ARRS["left"]): ARRS["left_start"],
    (ARRS["start"], ARRS["right"]): ARRS["right_start"],
    (ARRS["end"], ARRS["left"]): ARRS["left_end"],
    (ARRS["end"], ARRS["right"]): ARRS["right_end"],
    (ARRS["middle"], ARRS["left"]): ARRS["left_middle"],
    (ARRS["middle"], ARRS["right"]): ARRS["right_middle"],
    (ARRS["right_start"], ARRS["left"]): ARRS["both_start"],
    (ARRS["right_end"], ARRS["left"]): ARRS["both_end"],
    (ARRS["right_middle"], ARRS["left"]): ARRS["both_middle"],
    (ARRS["left_start"], ARRS["right"]): ARRS["both_start"],
    (ARRS["left_end"], ARRS["right"]): ARRS["both_end"],
    (ARRS["left_middle"], ARRS["right"]): ARRS["both_middle"],
    (ARRS["co"], ARRS["right"]): ARRS["co"],
    (ARRS["co"], ARRS["left"]): ARRS["co"],
    }
