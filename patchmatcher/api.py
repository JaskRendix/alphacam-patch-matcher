from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .butterflies import get_butterfly_params, load_butterfly_table
from .geometry import Rectangle
from .io import write_dxf
from .matching import PatchMatcher
from .svg import scene_to_svg
from .tables import PatchTable

app = FastAPI(
    title="PatchMatcher API",
    version="1.0.0",
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


class RectangleOut(BaseModel):
    width: float
    height: float
    cx: float
    cy: float


class CircleOut(BaseModel):
    radius: float
    cx: float
    cy: float


class ReplaceResponse(BaseModel):
    rectangle: RectangleOut
    center_hole: CircleOut


@app.post("/match", tags=["Matching"])
async def match_patch(
    width: float, height: float, table: str = "config/patchSizesTop.txt"
):
    """Equivalent to: patchmatcher match --width X --height Y --table FILE"""
    try:
        patches = PatchTable.from_file(Path(table))
        matcher = PatchMatcher(patches)
        patch = matcher.closest_patch(width, height)
        return {"matched_width": patch.width, "matched_height": patch.height}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/replace", response_model=ReplaceResponse, tags=["Matching"])
async def replace_geometry(req: ReplaceRequest):
    """Equivalent to: patchmatcher replace ..."""
    try:
        patches = PatchTable.from_file(Path(req.table_path))
        matcher = PatchMatcher(patches)

        rect = Rectangle(
            width=req.width,
            height=req.height,
            cx=req.cx,
            cy=req.cy,
        )

        new_rect, hole = matcher.replace_geometry(
            rect,
            x_adjust=req.x_adjust,
            y_adjust=req.y_adjust,
        )

        return ReplaceResponse(
            rectangle=RectangleOut(
                width=new_rect.width,
                height=new_rect.height,
                cx=new_rect.cx,
                cy=new_rect.cy,
            ),
            center_hole=CircleOut(
                radius=hole.radius,
                cx=hole.cx,
                cy=hole.cy,
            ),
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
):
    """Return DXF text directly."""
    try:
        patches = PatchTable.from_file(Path(table))
        matcher = PatchMatcher(patches)

        rect = Rectangle(width=width, height=height, cx=cx, cy=cy)
        new_rect, hole = matcher.replace_geometry(rect, x_adjust, y_adjust)

        from .io import dxf_to_string

        return dxf_to_string(new_rect, hole)

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
):
    """Return SVG text directly."""
    try:
        patches = PatchTable.from_file(Path(table))
        matcher = PatchMatcher(patches)

        rect = Rectangle(width=width, height=height, cx=cx, cy=cy)
        new_rect, hole = matcher.replace_geometry(rect, x_adjust, y_adjust)

        svg = scene_to_svg(new_rect, hole)
        return svg

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/butterfly/{code}", tags=["Butterflies"])
async def butterfly_lookup(code: str, table: Optional[str] = None):
    """Equivalent to: patchmatcher butterfly CODE"""
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

        return params.__dict__

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
