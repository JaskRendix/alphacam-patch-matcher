# **patchmatcher**

A modern Python rewrite of the legacy *Patch‑Matcher* Alphacam macro.

This project extracts the CNC‑relevant logic from the original VB6 plugin:

https://github.com/PCipolle/Patch-Matcher

The original implementation depended on Alphacam COM automation, VB6 forms, and proprietary macro packaging.  
This rewrite isolates the useful geometry logic and exposes it as a clean, testable Python library with a CLI and optional HTTP API.

No VB6 code is reused.  
All behavior is re‑implemented from observed inputs, outputs, and data tables.

---

## **Purpose**

The original Patch‑Matcher automated three tasks used in woodworking and CNC routing:

1. Selecting the closest patch size for a given rectangle  
2. Replacing geometry with the matched patch and center hole  
3. Looking up butterfly inlay parameters (W1–W7, B1–B2)

This project preserves those behaviors without Alphacam dependencies.

---

## **What this project contains**

### **Geometry model**
Simple primitives used by the matching logic:

- `Rectangle(width, height, cx, cy)`  
- `Circle(radius, cx, cy)`

These match how the original plugin treated geometry.

### **Patch tables**
The VB6 plugin used flat numeric tables for patch sizes.  
These are preserved under `config/` and parsed by:

- `PatchTable.from_file()`

### **Matching logic**
A faithful rewrite of the closest‑patch selection rules:

- Euclidean distance in width/height space  
- deterministic tie‑breaking  
- optional X/Y adjustments

### **Replacement logic**
Given an input rectangle:

- find the closest patch  
- create a new rectangle  
- compute the center hole  
- apply optional offsets

### **Butterfly parameters**
The W1–W7 and B1–B2 inlay definitions are included as structured data.  
Custom TOML tables are supported.

### **Exporters**
Minimal DXF and SVG exporters for:

- rectangles  
- center holes  

Useful for inspection or downstream CAM pipelines.

### **CLI**
A command‑line interface exposing:

- `match`  
- `replace`  
- `butterfly`  
- `serve` (API server)

### **API**
An optional FastAPI server that mirrors the CLI functionality.

---

## **What this project does not include**

The following Alphacam‑specific elements are intentionally excluded:

- COM automation (`Drw`, `Geo`, `App`)  
- VB6 UI forms  
- toolpath generation  
- layer visibility  
- machine‑specific settings  
- `.amb` macro packaging  

The goal is a portable logic layer, not a CAM system.

---

## **Installation**

### CLI only
```
pip install patchmatcher # not yet published to PyPI
```

### CLI + API
```
pip install "patchmatcher[api]" # not yet published to PyPI
```

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

### **Replace geometry**
```
patchmatcher replace \
    --width 3.1 \
    --height 4.9 \
    --cx 10 \
    --cy 20 \
    --table config/patchSizesTop.txt
```

### **Lookup butterfly parameters**
```
patchmatcher butterfly W3
```

### **DXF export**
```
patchmatcher replace \
    --width 3.1 \
    --height 4.9 \
    --cx 10 \
    --cy 20 \
    --table config/patchSizesTop.txt \
    --dxf-out output.dxf
```

### **SVG export**
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
| **POST** | `/match` | Find closest patch |
| **POST** | `/replace` | Replace geometry and return JSON |
| **GET** | `/replace/dxf` | Return DXF as text |
| **GET** | `/replace/svg` | Return SVG as text |
| **GET** | `/butterfly/{code}` | Lookup butterfly parameters |

---

## **Request formats**

### `/match`
Query parameters:

```
width=3.1
height=4.9
table=config/patchSizesTop.txt
```

### `/replace`
```json
{
  "width": 3.1,
  "height": 4.9,
  "cx": 10,
  "cy": 20,
  "table_path": "config/patchSizesTop.txt"
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
