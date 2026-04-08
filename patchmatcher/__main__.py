import argparse
from pathlib import Path

from .butterflies import get_butterfly_params, load_butterfly_table
from .geometry import Rectangle
from .io import load_json_input, write_dxf, write_json_output
from .matching import PatchMatcher
from .svg import scene_to_svg
from .tables import PatchTable

try:
    import uvicorn
except ImportError:
    uvicorn = None


def cmd_serve(args):
    if uvicorn is None:
        raise SystemExit(
            "FastAPI/uvicorn not installed. Install with:\n"
            "  pip install 'patchmatcher[api]'"
        )

    uvicorn.run(
        "patchmatcher.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def cmd_match(args) -> None:
    patches = PatchTable.from_file(args.table)
    matcher = PatchMatcher(patches)
    patch = matcher.closest_patch(args.width, args.height)
    print(f"Matched patch: {patch.width} x {patch.height}")


def cmd_replace(args) -> None:
    patches = PatchTable.from_file(args.table)
    matcher = PatchMatcher(patches)

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

    new_rect, hole = matcher.replace_geometry(
        rect,
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
    # If user provided a custom table, load it
    if args.table:
        try:
            table = load_butterfly_table(args.table)
        except Exception as e:
            print(f"Failed to load butterfly table: {e}")
            return

        if args.code not in table:
            print(f"Unknown butterfly code: {args.code}")
            return

        params = table[args.code]

    else:
        # Default built‑in table
        try:
            params = get_butterfly_params(args.code)
        except ValueError as e:
            print(e)
            return

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
    p_bfly.add_argument("--table", type=Path, help="Path to butterfly TOML file")
    p_bfly.set_defaults(func=cmd_butterfly)

    # serve
    p_serve = sub.add_parser(
        "serve", help="Start the FastAPI server (requires the [api] extra)."
    )
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument(
        "--reload", action="store_true", help="Enable auto-reload (development only)."
    )
    p_serve.set_defaults(func=cmd_serve)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
