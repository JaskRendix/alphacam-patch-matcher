import math

import pytest

from patchmatcher.geometry import Circle, Rectangle


@pytest.mark.parametrize(
    "width,height,cx,cy,expected",
    [
        (4, 2, 10, 20, (8, 19, 12, 21)),
        (10, 10, 0, 0, (-5, -5, 5, 5)),
        (1, 1, -3, -3, (-3.5, -3.5, -2.5, -2.5)),
    ],
)
def test_rectangle_bounds(width, height, cx, cy, expected):
    r = Rectangle(width=width, height=height, cx=cx, cy=cy)
    assert r.bounds == expected


@pytest.mark.parametrize(
    "width,height,area",
    [
        (4, 2, 8),
        (0, 5, 0),  # zero width
        (5, 0, 0),  # zero height
        (0, 0, 0),  # degenerate
    ],
)
def test_rectangle_area(width, height, area):
    r = Rectangle(width=width, height=height, cx=0, cy=0)
    assert r.area == area


@pytest.mark.parametrize(
    "rect,point,inside",
    [
        (Rectangle(4, 2, 10, 20), (10, 20), True),
        (Rectangle(4, 2, 10, 20), (8, 19), True),
        (Rectangle(4, 2, 10, 20), (12, 21), True),
        (Rectangle(4, 2, 10, 20), (7.9, 20), False),
        (Rectangle(4, 2, 10, 20), (10, 21.1), False),
    ],
)
def test_rectangle_contains_point(rect, point, inside):
    x, y = point
    assert rect.contains_point(x, y) is inside


@pytest.mark.parametrize(
    "rect,dx,dy,expected",
    [
        (Rectangle(4, 2, 10, 20), 5, -3, (15, 17)),
        (Rectangle(4, 2, 0, 0), 0, 0, (0, 0)),
        (Rectangle(4, 2, -5, -5), 2, 2, (-3, -3)),
    ],
)
def test_rectangle_translate(rect, dx, dy, expected):
    moved = rect.translate(dx, dy)
    assert (moved.cx, moved.cy) == expected
    assert moved.width == rect.width
    assert moved.height == rect.height


def test_circle_creation():
    c = Circle(radius=1.5, cx=5, cy=7)
    assert c.radius == 1.5
    assert c.cx == 5
    assert c.cy == 7


@pytest.mark.parametrize("radius", [0, 1, 2.5, 10])
def test_circle_area(radius):
    c = Circle(radius=radius, cx=0, cy=0)
    assert math.isclose(c.area, math.pi * radius * radius)


@pytest.mark.parametrize(
    "circle,point,inside",
    [
        (Circle(3, 0, 0), (0, 0), True),
        (Circle(3, 0, 0), (3, 0), True),
        (Circle(3, 0, 0), (2.9, 0), True),
        (Circle(3, 0, 0), (3.1, 0), False),
        (Circle(0, 0, 0), (0, 0), True),  # zero radius
        (Circle(0, 0, 0), (0.1, 0), False),
    ],
)
def test_circle_contains_point(circle, point, inside):
    x, y = point
    assert circle.contains_point(x, y) is inside


@pytest.mark.parametrize(
    "circle,dx,dy,expected",
    [
        (Circle(2, 5, 7), -2, 4, (3, 11)),
        (Circle(2, 0, 0), 0, 0, (0, 0)),
        (Circle(2, -5, -5), 5, 5, (0, 0)),
    ],
)
def test_circle_translate(circle, dx, dy, expected):
    moved = circle.translate(dx, dy)
    assert (moved.cx, moved.cy) == expected
    assert moved.radius == circle.radius
