import argparse
from pathlib import Path

from .butterflies import get_butterfly_params
from .geometry import Rectangle
from .matching import closest_patch, replace_geometry
from .tables import load_patch_table


def cmd_match(args):
    patches = load_patch_table(args.table)
    w, h = closest_patch(args.width, args.height, patches)
    print(f"Matched patch: {w} x {h}")


def cmd_replace(args):
    patches = load_patch_table(args.table)

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

    print(
        f"New rectangle: {new_rect.width} x {new_rect.height} at ({new_rect.cx}, {new_rect.cy})"
    )
    print(f"Center hole: radius {hole.radius} at ({hole.cx}, {hole.cy})")


def cmd_butterfly(args):
    params = get_butterfly_params(args.code)

    print(f"Butterfly {args.code}:")
    for field, value in params.__dict__.items():
        print(f"  {field}: {value}")


def build_parser():
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
    p_replace.add_argument("--width", type=float, required=True)
    p_replace.add_argument("--height", type=float, required=True)
    p_replace.add_argument("--cx", type=float, required=True)
    p_replace.add_argument("--cy", type=float, required=True)
    p_replace.add_argument("--table", type=Path, required=True)
    p_replace.add_argument("--x-adjust", type=float, default=0.0)
    p_replace.add_argument("--y-adjust", type=float, default=0.0)
    p_replace.set_defaults(func=cmd_replace)

    # butterfly
    p_bfly = sub.add_parser(
        "butterfly", help="Lookup butterfly parameters (W1-W7, B1-B2)."
    )
    p_bfly.add_argument("code", type=str)
    p_bfly.set_defaults(func=cmd_butterfly)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
