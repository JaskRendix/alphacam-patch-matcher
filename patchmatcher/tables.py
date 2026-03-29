from pathlib import Path

PatchSize = tuple[float, float]


def load_patch_table(path: str | Path) -> list[PatchSize]:
    """
    Load a VB6-style patch table where each patch is stored as:
        width\n
        height\n
    """
    path = Path(path)
    lines = [l.strip() for l in path.read_text().splitlines() if l.strip()]

    if len(lines) % 2 != 0:
        raise ValueError(f"Expected an even number of lines in {path}")

    patches = []
    for i in range(0, len(lines), 2):
        w = float(lines[i])
        h = float(lines[i + 1])
        patches.append((w, h))

    return patches
