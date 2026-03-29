import pytest

from patchmatcher.geometry import Rectangle
from patchmatcher.tables import load_patch_table


@pytest.fixture
def top_patches():
    return load_patch_table("config/patchSizesTop.txt")


@pytest.fixture
def sample_rect():
    return Rectangle(width=3.1, height=4.9, cx=10, cy=20)
