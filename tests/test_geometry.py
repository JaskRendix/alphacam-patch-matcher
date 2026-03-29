from patchmatcher.geometry import Rectangle, Circle


def test_rectangle_bounds():
    r = Rectangle(width=4, height=2, cx=10, cy=20)
    xmin, ymin, xmax, ymax = r.bounds

    assert xmin == 8
    assert xmax == 12
    assert ymin == 19
    assert ymax == 21


def test_circle_creation():
    c = Circle(radius=1.5, cx=5, cy=7)
    assert c.radius == 1.5
    assert c.cx == 5
    assert c.cy == 7
