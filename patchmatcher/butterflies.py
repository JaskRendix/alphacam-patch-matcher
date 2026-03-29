from dataclasses import dataclass


@dataclass
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


# Extracted from Geometries.bas (W1-W7, B1-B2)
BUTTERFLY_TABLE: dict[str, ButterflyParams] = {
    "W1": ButterflyParams(0.05, 0.05, 0.35, 0.63279, 0.20458, 9, -0.5, 0, 0),
    "W2": ButterflyParams(0.05, 0.05, 0.35, 0.75935, 0.26708, 9, -0.5, 0, 0),
    "W3": ButterflyParams(0.05, 0.05, 0.60, 1.01247, 0.30823, 9, -0.5, 0, 0),
    "W4": ButterflyParams(0.05, 0.05, 0.60, 1.13902, 0.39364, 9, -0.5, 0, 0),
    "W5": ButterflyParams(0.05, 0.05, 0.975, 1.51870, 0.39985, 9, -0.5, 0, 0),
    "W6": ButterflyParams(0.05, 0.05, 1.475, 2.02493, 0.49146, 9, -0.5, 0, 0),
    "W7": ButterflyParams(0.05, 0.05, 2.118, 2.66699, 0.47879, 7.77074, -0.5, 0, 0),
    "B1": ButterflyParams(
        0.05, 0.25, 1.000, 1.39837, 0.36335, 7.944815, -0.7, 0, 0.368
    ),
    "B2": ButterflyParams(0.05, 0.25, 1.374, 1.89837, 0.38002, 8.25281, -0.7, 0, 0.362),
}


def get_butterfly_params(code: str) -> ButterflyParams:
    """
    Retrieve parametric butterfly definition (W1-W7, B1-B2).
    """
    return BUTTERFLY_TABLE[code]
