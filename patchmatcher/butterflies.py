from dataclasses import dataclass
from pathlib import Path

import tomllib

REQUIRED_FIELDS = {
    "diam1",
    "diam2",
    "circ_offset",
    "line1",
    "offset",
    "angle",
    "z_bottom",
    "radius1",
    "radius2",
}


def validate_butterfly_section(code: str, params: dict) -> None:
    missing = REQUIRED_FIELDS - params.keys()
    if missing:
        raise ValueError(
            f"Butterfly {code} missing fields: {', '.join(sorted(missing))}"
        )


@dataclass(frozen=True)
class ButterflyParams:
    diam1: float
    diam2: float
    circ_offset: float
    line1: float
    offset: float
    angle: float
    z_bottom: float
    radius1: float
    radius2: float

    def __post_init__(self) -> None:
        for field, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field} must be a number, got {value!r}")


def load_butterfly_table(path: str) -> dict[str, ButterflyParams]:
    data = tomllib.loads(Path(path).read_text())
    table = {}

    for code, params in data.items():
        validate_butterfly_section(code, params)
        table[code] = ButterflyParams(**params)

    return table


BUTTERFLY_TABLE = load_butterfly_table("config/butterflies.toml")


def get_butterfly_params(code: str) -> ButterflyParams:
    try:
        return BUTTERFLY_TABLE[code]
    except KeyError:
        raise ValueError(f"Unknown butterfly code: {code}")
