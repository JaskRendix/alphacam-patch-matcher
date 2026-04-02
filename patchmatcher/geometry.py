import math
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float
    cx: float
    cy: float

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

    @property
    def area(self) -> float:
        return math.pi * self.radius * self.radius

    def contains_point(self, x: float, y: float) -> bool:
        return (x - self.cx) ** 2 + (y - self.cy) ** 2 <= self.radius**2

    def translate(self, dx: float, dy: float) -> Self:
        return Circle(
            radius=self.radius,
            cx=self.cx + dx,
            cy=self.cy + dy,
        )
