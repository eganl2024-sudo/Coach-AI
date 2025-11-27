# Drill Schema Notes

## Diagram Fields

| Field | Type | Description |
| --- | --- | --- |
| `diagram_path` | string | Relative path to a static diagram asset (e.g. `assets/diagrams/WU_001.svg`). Stored in CSV so the UI can render the field layout immediately. |
| `diagram_metadata` | string/JSON | Reserved for structured diagram metadata (Phase 2). Leave blank for now or store a JSON string if metadata is available. |

**Usage**
- Keep `diagram_path` relative to the project root so it works in Streamlit Cloud and local installs.
- When adding a new drill, drop the static SVG/PNG into `assets/diagrams/` and point `diagram_path` to it.
- `diagram_metadata` will eventually power auto-generated diagrams; document JSON examples in this file as the renderer evolves.

## Diagram Metadata (Phase 2)

Metadata follows a normalized 0–100 (x) by 0–70 (y) coordinate system so diagrams scale to any canvas. Example:

```json
{
  "field_dimensions": [100, 70],
  "players": [
    {"label": "A1", "team": "blue", "x": 20, "y": 35},
    {"label": "A2", "team": "blue", "x": 40, "y": 25}
  ],
  "cones": [
    {"x": 10, "y": 20},
    {"x": 10, "y": 50}
  ],
  "arrows": [
    {"from": [20, 35], "to": [40, 35], "type": "run"},
    {"from": [40, 25], "to": [60, 25], "type": "pass"}
  ],
  "zones": [
    {"shape": "rectangle", "x": 45, "y": 20, "width": 10, "height": 30}
  ]
}
```

- `players` can include `team` or `color` fields for styling.
- `arrows.type` supports `run`, `pass`, `shot`, and controls the style the renderer uses.
- Additional objects (e.g., `goals`, `shaded_zones`) can be added later; keep the schema backward compatible.
