# **patchmatcher**

A modern Python rewrite of the legacy *Patch‑Matcher* Alphacam macro.

This project extracts the CNC‑relevant logic from the original VB6 plugin:

[https://github.com/PCipolle/Patch-Matcher](https://github.com/PCipolle/Patch-Matcher)

The original implementation depended on Alphacam COM automation, VB6 forms, and proprietary macro packaging.  
This rewrite isolates the geometry and matching logic and exposes it as a clean, testable Python library with a CLI and optional HTTP API.

No VB6 code is reused.  
All behavior is re‑implemented from observed inputs, outputs, and data tables.

---

## **Purpose**

The original Patch‑Matcher automated three tasks used in woodworking and CNC routing:

1. Selecting the closest patch size for a rectangle  
2. Replacing geometry with the matched patch and a center hole  
3. Looking up butterfly inlay parameters (W1–W7, B1–B2)

This project preserves those behaviors without Alphacam dependencies.

---

## **What this project contains**

### **Geometry model**
Simple primitives used by the matching logic:

- `Rectangle(width, height, cx, cy)`  
- `Circle(radius, cx, cy)`

Geometry objects include strict validation for dimensions and coordinates.

### **Patch tables**
The VB6 plugin used flat numeric tables for patch sizes.  
These are preserved under `config/` and parsed by:

- `PatchTable.from_file()`

Patch tables include:

- numeric validation  
- table‑wide bounds  
- query validation for safety

### **Matching logic**
A modern rewrite of the closest‑patch selection rules:

- Euclidean distance in width/height space  
- deterministic tie‑breaking  
- optional diagnostics (distance, percentile, confidence)  
- bounds checking through `PatchTable.validate_query()`

### **Replacement logic**
Given an input rectangle:

- find the closest patch  
- create a new rectangle  
- compute the center hole  
- apply optional offsets  
- support configurable hole radius  
- return diagnostics when requested

### **Butterfly parameters**
The W1–W7 and B1–B2 inlay definitions are included as structured data.  
Custom TOML tables are supported.

### **Exporters**
DXF and SVG exporters for:

- rectangles  
- center holes  

Exporters support:

- scale factors  
- unit selection  
- correct SVG viewBox computation  
- DRY DXF generation

### **CLI**
A command‑line interface exposing:

- `match`  
- `replace`  
- `butterfly`  
- `serve` (API server)

CLI commands support:

- diagnostics  
- configurable hole radius  
- DXF/SVG scale and units  
- JSON input and output

### **API**
A FastAPI server that mirrors the CLI functionality.  
Endpoints support diagnostics, hole radius, scale, and units.

---

## **What this project does not include**

The following Alphacam‑specific elements are excluded:

- COM automation (`Drw`, `Geo`, `App`)  
- VB6 UI forms  
- toolpath generation  
- layer visibility  
- machine‑specific settings  
- `.amb` macro packaging  

The goal is a portable logic layer, not a CAM system.

---

## **Installation**

### Development install
```
pip install -e .[api]
```

---

## **CLI usage**

### **Find the closest patch**
```
patchmatcher match \
    --width 3.1 \
    --height 4.9 \
    --table config/patchSizesTop.txt
```

### **Find the closest patch with diagnostics**
```
patchmatcher match \
    --width 3.1 \
    --height 4.9 \
    --table config/patchSizesTop.txt \
    --diagnostics
```

### **Replace geometry**
```
patchmatcher replace \
    --width 3.1 \
    --height 4.9 \
    --cx 10 \
    --cy 20 \
    --table config/patchSizesTop.txt
```

### **Replace geometry with custom hole radius**
```
patchmatcher replace \
    --width 3.1 \
    --height 4.9 \
    --cx 10 \
    --cy 20 \
    --hole-radius 0.125 \
    --table config/patchSizesTop.txt
```

### **DXF export with units**
```
patchmatcher replace \
    --width 3.1 \
    --height 4.9 \
    --cx 10 \
    --cy 20 \
    --table config/patchSizesTop.txt \
    --dxf-out output.dxf \
    --hole-radius 0.125
```

### **SVG export with scale**
```
patchmatcher replace \
    --width 3.1 \
    --height 4.9 \
    --cx 10 \
    --cy 20 \
    --table config/patchSizesTop.txt \
    --svg-out output.svg
```

### **JSON input/output**
```
patchmatcher replace \
    --json-in input.json \
    --table config/patchSizesTop.txt \
    --json-out result.json
```

---

## **API usage**

Start the server:

```
patchmatcher serve --reload
```

Or manually:

```
uvicorn patchmatcher.api:app --reload
```

Interactive docs:

- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

## **Endpoints**

| Method | Path | Description |
|--------|------|-------------|
| **POST** | `/match` | Find closest patch (supports diagnostics) |
| **POST** | `/replace` | Replace geometry and return JSON (supports diagnostics) |
| **GET** | `/replace/dxf` | Return DXF text (supports scale and units) |
| **GET** | `/replace/svg` | Return SVG text (supports scale and units) |
| **GET** | `/butterfly/{code}` | Lookup butterfly parameters |

---

## **Request formats**

### `/match`
```
POST /match?width=3.1&height=4.9&table=config/patchSizesTop.txt
```

### `/replace`
```json
{
  "width": 3.1,
  "height": 4.9,
  "cx": 10,
  "cy": 20,
  "table_path": "config/patchSizesTop.txt",
  "x_adjust": 0.0,
  "y_adjust": 0.0,
  "hole_radius": 0.05,
  "diagnostics": false
}
```

### `/butterfly/{code}`
```
GET /butterfly/W3
```

---

## **Examples**

### Replace geometry via API
```
curl -X POST http://localhost:8000/replace \
     -H "Content-Type: application/json" \
     -d '{"width":3.1,"height":4.9,"cx":10,"cy":20}'
```

### Export DXF via API
```
curl "http://localhost:8000/replace/dxf?width=3.1&height=4.9&cx=10&cy=20" \
     -o output.dxf
```

---

## **Tests**

```
pytest
```

The test suite covers:

- patch table parsing  
- matching logic  
- geometry replacement  
- butterfly lookup  
- DXF/SVG exporters  
- CLI commands  
- API endpoints  

All tests pass.
