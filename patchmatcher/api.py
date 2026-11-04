from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .butterflies import get_butterfly_params, load_butterfly_table
from .geometry import Rectangle
from .io import dxf_to_string
from .matching import PatchMatcher
from .svg import scene_to_svg
from .tables import PatchTable

app = FastAPI(
    title="PatchMatcher API",
    version="1.2.0",
    description="REST API for patch matching, geometry replacement, and butterfly lookup.",
)


class GeometryIn(BaseModel):
    width: float
    height: float
    cx: float = 0.0
    cy: float = 0.0


class ReplaceRequest(GeometryIn):
    table_path: str = "config/patchSizesTop.txt"
    x_adjust: float = 0.0
    y_adjust: float = 0.0
    hole_radius: float = 0.05
    diagnostics: bool = False


class RectangleOut(BaseModel):
    width: float
    height: float
    cx: float
    cy: float


class CircleOut(BaseModel):
    radius: float
    cx: float
    cy: float


class MatchDiagnostics(BaseModel):
    distance: float
    distance_ratio: float
    candidate_count: int


class MatchResponse(BaseModel):
    matched_width: float
    matched_height: float
    diagnostics: MatchDiagnostics | None = None


class ReplaceResponse(BaseModel):
    rectangle: RectangleOut
    center_hole: CircleOut
    diagnostics: MatchDiagnostics | None = None


@app.post("/match", response_model=MatchResponse, tags=["Matching"])
async def match_patch(
    width: float,
    height: float,
    table: str = "config/patchSizesTop.txt",
    diagnostics: bool = False,
) -> MatchResponse:
    """Return the closest patch match with optional diagnostics."""
    try:
        patches = PatchTable.from_file(Path(table))
        matcher = PatchMatcher(patches)

        if diagnostics:
            result = matcher.closest_patch_with_metrics(width, height)
            diag = MatchDiagnostics(
                distance=result.distance,
                distance_ratio=result.distance_ratio,
                candidate_count=result.candidate_count,
            )
            return MatchResponse(
                matched_width=result.patch.width,
                matched_height=result.patch.height,
                diagnostics=diag,
            )

        patch = matcher.closest_patch(width, height)
        return MatchResponse(
            matched_width=patch.width,
            matched_height=patch.height,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/replace", response_model=ReplaceResponse, tags=["Matching"])
async def replace_geometry(req: ReplaceRequest) -> ReplaceResponse:
    """Replace geometry using the closest patch and return rectangle, hole, and diagnostics."""
    try:
        patches = PatchTable.from_file(Path(req.table_path))
        matcher = PatchMatcher(patches)

        rect = Rectangle(
            width=req.width,
            height=req.height,
            cx=req.cx,
            cy=req.cy,
        )

        result = matcher.replace_geometry(
            rect,
            x_adjust=req.x_adjust,
            y_adjust=req.y_adjust,
            hole_radius=req.hole_radius,
            diagnostics=req.diagnostics,
        )

        diag_out = None
        if result.diagnostics:
            diag_out = MatchDiagnostics(
                distance=result.diagnostics.distance,
                distance_ratio=result.diagnostics.distance_ratio,
                candidate_count=result.diagnostics.candidate_count,
            )

        return ReplaceResponse(
            rectangle=RectangleOut(
                width=result.rectangle.width,
                height=result.rectangle.height,
                cx=result.rectangle.cx,
                cy=result.rectangle.cy,
            ),
            center_hole=CircleOut(
                radius=result.hole.radius,
                cx=result.hole.cx,
                cy=result.hole.cy,
            ),
            diagnostics=diag_out,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Replacement failed: {e}")


@app.get("/replace/dxf", response_class=PlainTextResponse, tags=["Export"])
async def replace_dxf(
    width: float,
    height: float,
    cx: float,
    cy: float,
    table: str = "config/patchSizesTop.txt",
    x_adjust: float = 0.0,
    y_adjust: float = 0.0,
    hole_radius: float = 0.05,
    scale: float = 1.0,
    units: str = "in",
) -> str:
    """Return a DXF string for the replaced geometry."""
    try:
        if scale <= 0:
            raise ValueError("scale must be > 0")
        if units not in {"in", "mm"}:
            raise ValueError("units must be 'in' or 'mm'")

        patches = PatchTable.from_file(Path(table))
        matcher = PatchMatcher(patches)

        rect = Rectangle(width=width, height=height, cx=cx, cy=cy)
        result = matcher.replace_geometry(
            rect,
            x_adjust=x_adjust,
            y_adjust=y_adjust,
            hole_radius=hole_radius,
        )

        return dxf_to_string(result.rectangle, result.hole, scale=scale, units=units)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/replace/svg", response_class=PlainTextResponse, tags=["Export"])
async def replace_svg(
    width: float,
    height: float,
    cx: float,
    cy: float,
    table: str = "config/patchSizesTop.txt",
    x_adjust: float = 0.0,
    y_adjust: float = 0.0,
    hole_radius: float = 0.05,
    scale: float = 1.0,
    units: str = "px",
) -> str:
    """Return an SVG string for the replaced geometry."""
    try:
        if scale <= 0:
            raise ValueError("scale must be > 0")
        if units not in {"px", "mm", "in"}:
            raise ValueError("units must be 'px', 'mm', or 'in'")

        patches = PatchTable.from_file(Path(table))
        matcher = PatchMatcher(patches)

        rect = Rectangle(width=width, height=height, cx=cx, cy=cy)
        result = matcher.replace_geometry(
            rect,
            x_adjust=x_adjust,
            y_adjust=y_adjust,
            hole_radius=hole_radius,
        )

        return scene_to_svg(result.rectangle, result.hole, scale=scale, units=units)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/butterfly/{code}", tags=["Butterflies"])
async def butterfly_lookup(code: str, table: str | None = None) -> dict:
    """Return butterfly parameters for the given code."""
    try:
        if table:
            tbl = load_butterfly_table(Path(table))
            if code not in tbl:
                raise HTTPException(
                    status_code=404, detail="Code not found in custom table"
                )
            params = tbl[code]
        else:
            params = get_butterfly_params(code)

        return asdict(params)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
