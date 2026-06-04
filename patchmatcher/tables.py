import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Self


def _validate_number(name: str, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be a finite number, got {value}")


def _validate_positive(name: str, value: float) -> None:
    _validate_number(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")


@dataclass(frozen=True)
class Patch:
    width: float
    height: float

    def __post_init__(self):
        _validate_positive("patch width", self.width)
        _validate_positive("patch height", self.height)


class PatchTable:
    """
    Represents a table of patch sizes extracted from legacy VB6 data files.
    Each patch consists of a width/height pair.
    """

    def __init__(self, patches: Iterable[Patch]):
        patches = list(patches)
        if not patches:
            raise ValueError("PatchTable cannot be empty")

        # Validate all patches
        for p in patches:
            if not isinstance(p, Patch):
                raise TypeError(f"Expected Patch, got {type(p).__name__}")

        self.patches = patches

        # Precompute bounds
        self._min_w = min(p.width for p in patches)
        self._max_w = max(p.width for p in patches)
        self._min_h = min(p.height for p in patches)
        self._max_h = max(p.height for p in patches)

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        """
        Load a VB6-style patch table where each patch is stored as:
            width\n
            height\n

        The file must contain an even number of non-empty lines.
        """
        path = Path(path)
        lines = [l.strip() for l in path.read_text().splitlines() if l.strip()]

        if len(lines) % 2 != 0:
            raise ValueError(f"Expected an even number of lines in {path}")

        patches = [
            Patch(float(lines[i]), float(lines[i + 1])) for i in range(0, len(lines), 2)
        ]
        return cls(patches)

    def __len__(self) -> int:
        return len(self.patches)

    def __iter__(self) -> Iterator[Patch]:
        return iter(self.patches)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """
        Return (min_width, min_height, max_width, max_height).
        """
        return self._min_w, self._min_h, self._max_w, self._max_h

    def validate_query(
        self, width: float, height: float, *, tolerance: float = 2.0
    ) -> None:
        """
        Validate that the requested width/height are within a reasonable range
        of the patch table.

        tolerance = multiplier for allowed deviation.
        Example: tolerance=2.0 allows queries up to 2× outside the table range.
        """
        _validate_positive("query width", width)
        _validate_positive("query height", height)

        min_w, min_h, max_w, max_h = self.bounds

        if width < min_w / tolerance or width > max_w * tolerance:
            raise ValueError(
                f"Width {width} is outside safe bounds "
                f"({min_w}-{max_w}, tolerance={tolerance})"
            )

        if height < min_h / tolerance or height > max_h * tolerance:
            raise ValueError(
                f"Height {height} is outside safe bounds "
                f"({min_h}-{max_h}, tolerance={tolerance})"
            )
