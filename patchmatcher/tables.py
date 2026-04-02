from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Self


@dataclass(frozen=True)
class Patch:
    width: float
    height: float


class PatchTable:
    """
    Represents a table of patch sizes extracted from legacy VB6 data files.
    Each patch consists of a width/height pair.
    """

    def __init__(self, patches: Iterable[Patch]):
        self.patches = list(patches)

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
