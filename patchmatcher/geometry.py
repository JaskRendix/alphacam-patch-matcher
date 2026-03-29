from dataclasses import dataclass


@dataclass
class Rectangle:
    width: float
    height: float
    cx: float
    cy: float

    @property
    def bounds(self):
        return (
            self.cx - self.width / 2,
            self.cy - self.height / 2,
            self.cx + self.width / 2,
            self.cy + self.height / 2,
        )


@dataclass
class Circle:
    radius: float
    cx: float
    cy: float
