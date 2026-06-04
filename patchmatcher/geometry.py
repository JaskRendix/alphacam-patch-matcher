import math
from dataclasses import dataclass
from typing import Self


def _validate_positive(name: str, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")

    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be a finite number, got {value}")

    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")


def _validate_coordinate(name: str, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")

    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be a finite number, got {value}")


@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float
    cx: float
    cy: float

    def __post_init__(self):
        _validate_positive("width", self.width)
        _validate_positive("height", self.height)
        _validate_coordinate("cx", self.cx)
        _validate_coordinate("cy", self.cy)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return (
            self.cx - self.width / 2,
            self.cy - self.height / 2,
            self.cx + self.width / 2,
            self.cy + self.height / 2,
        )

    @property
    def area(self) -> float:
        return self.width * self.height

    def contains_point(self, x: float, y: float) -> bool:
        xmin, ymin, xmax, ymax = self.bounds
        return xmin <= x <= xmax and ymin <= y <= ymax

    def translate(self, dx: float, dy: float) -> Self:
        _validate_coordinate("dx", dx)
        _validate_coordinate("dy", dy)
        return Rectangle(
            width=self.width,
            height=self.height,
            cx=self.cx + dx,
            cy=self.cy + dy,
        )


@dataclass(frozen=True)
class Circle:
    radius: float
    cx: float
    cy: float

    def __post_init__(self):
        _validate_positive("radius", self.radius)
        _validate_coordinate("cx", self.cx)
        _validate_coordinate("cy", self.cy)

    @property
    def area(self) -> float:
        return math.pi * self.radius * self.radius

    def contains_point(self, x: float, y: float) -> bool:
        return (x - self.cx) ** 2 + (y - self.cy) ** 2 <= self.radius**2

    def translate(self, dx: float, dy: float) -> Self:
        _validate_coordinate("dx", dx)
        _validate_coordinate("dy", dy)
        return Circle(
            radius=self.radius,
            cx=self.cx + dx,
            cy=self.cy + dy,
        )
