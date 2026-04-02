import argparse
import json
from pathlib import Path

from .butterflies import get_butterfly_params
from .geometry import Circle, Rectangle
from .matching import closest_patch, replace_geometry
from .svg import scene_to_svg
from .tables import PatchTable


def load_json_input(path: Path) -> Rectangle:
    data = json.loads(path.read_text())
    return Rectangle(
        width=data["width"],
        height=data["height"],
        cx=data["cx"],
        cy=data["cy"],
    )


def write_json_output(path: Path, rect: Rectangle, hole: Circle) -> None:
    out = {
        "rectangle": {
            "width": rect.width,
            "height": rect.height,
            "cx": rect.cx,
            "cy": rect.cy,
        },
        "center_hole": {
            "radius": hole.radius,
            "cx": hole.cx,
            "cy": hole.cy,
        },
    }
    path.write_text(json.dumps(out, indent=2))


def write_dxf(path: Path, rect: Rectangle, hole) -> None:
    x1 = rect.cx - rect.width / 2
    y1 = rect.cy - rect.height / 2
    x2 = rect.cx + rect.width / 2
    y2 = rect.cy + rect.height / 2

    dxf = f"""0
SECTION
2
ENTITIES
0
LWPOLYLINE
8
0
90
4
70
1
10
{x1}
20
{y1}
10
{x2}
20
{y1}
10
{x2}
20
{y2}
10
{x1}
20
{y2}
0
CIRCLE
8
0
10
{hole.cx}
20
{hole.cy}
40
{hole.radius}
0
ENDSEC
0
EOF
"""
    path.write_text(dxf)


def cmd_match(args) -> None:
    patches = PatchTable.from_file(args.table)
    patch = closest_patch(args.width, args.height, patches)
    print(f"Matched patch: {patch.width} x {patch.height}")


def cmd_replace(args) -> None:
    patches = PatchTable.from_file(args.table)

    # JSON input overrides CLI geometry
    if args.json_in:
        rect = load_json_input(args.json_in)
    else:
        rect = Rectangle(
            width=args.width,
            height=args.height,
            cx=args.cx,
            cy=args.cy,
        )

    new_rect, hole = replace_geometry(
        rect,
        patches,
        x_adjust=args.x_adjust,
        y_adjust=args.y_adjust,
    )

    # JSON output
    if args.json_out:
        write_json_output(args.json_out, new_rect, hole)
        print(f"Wrote JSON output to {args.json_out}")
        return

    # DXF output
    if args.dxf_out:
        write_dxf(args.dxf_out, new_rect, hole)
        print(f"Wrote DXF to {args.dxf_out}")
        return

    # SVG output
    if args.svg_out:
        svg = scene_to_svg(new_rect, hole)
        args.svg_out.write_text(svg)
        print(f"Wrote SVG to {args.svg_out}")
        return

    # Default text output
    print(
        f"New rectangle: {new_rect.width} x {new_rect.height} at ({new_rect.cx}, {new_rect.cy})"
    )
    print(f"Center hole: radius {hole.radius} at ({hole.cx}, {hole.cy})")


def cmd_butterfly(args) -> None:
    params = get_butterfly_params(args.code)
    print(f"Butterfly {args.code}:")
    for field, value in params.__dict__.items():
        print(f"  {field}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchmatcher",
        description="Patch matching, geometry replacement, and butterfly lookup.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # match
    p_match = sub.add_parser("match", help="Find closest patch for width/height.")
    p_match.add_argument("--width", type=float, required=True)
    p_match.add_argument("--height", type=float, required=True)
    p_match.add_argument("--table", type=Path, required=True)
    p_match.set_defaults(func=cmd_match)

    # replace
    p_replace = sub.add_parser("replace", help="Replace geometry with closest patch.")
    p_replace.add_argument("--width", type=float)
    p_replace.add_argument("--height", type=float)
    p_replace.add_argument("--cx", type=float)
    p_replace.add_argument("--cy", type=float)
    p_replace.add_argument("--table", type=Path, required=True)
    p_replace.add_argument("--x-adjust", type=float, default=0.0)
    p_replace.add_argument("--y-adjust", type=float, default=0.0)

    # JSON I/O
    p_replace.add_argument("--json-in", type=Path)
    p_replace.add_argument("--json-out", type=Path)

    # DXF output
    p_replace.add_argument("--dxf-out", type=Path)

    # SVG output
    p_replace.add_argument("--svg-out", type=Path)

    p_replace.set_defaults(func=cmd_replace)

    # butterfly
    p_bfly = sub.add_parser(
        "butterfly", help="Lookup butterfly parameters (W1-W7, B1-B2)."
    )
    p_bfly.add_argument("code", type=str)
    p_bfly.set_defaults(func=cmd_butterfly)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
