"""Utilities for rendering drill diagrams from metadata."""
from __future__ import annotations

import math
import logging
from pathlib import Path

import config

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrow, Rectangle
except ImportError:  # pragma: no cover
    plt = None
try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None

FIELD_COLOR = "#0a7d23"
LINE_COLOR = "#ffffff"
PLAYER_COLORS = {
    "blue": "#1f77b4",
    "red": "#d62728",
    "yellow": "#ffbf00",
}


def _require_matplotlib():
    if plt is None:
        raise RuntimeError(
            "matplotlib is required for interactive rendering. "
            "Use save_diagram() to generate placeholders without matplotlib."
        )


def draw_diagram(diagram: dict):
    """Return a matplotlib figure for the provided metadata."""
    _require_matplotlib()
    field_w, field_h = diagram.get("field_dimensions", [100, 70])
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, field_w)
    ax.set_ylim(0, field_h)
    ax.axis('off')

    rect = Rectangle((0, 0), field_w, field_h, linewidth=2, edgecolor=LINE_COLOR, facecolor=FIELD_COLOR, zorder=0)
    ax.add_patch(rect)
    mid_x = field_w / 2
    ax.plot([mid_x, mid_x], [0, field_h], color=LINE_COLOR, linewidth=1.5, linestyle='--', alpha=0.6)

    # Players
    for player in diagram.get('players', []):
        color = PLAYER_COLORS.get(player.get('team', '').lower(), '#ffffff')
        ax.scatter(player.get('x', 0), player.get('y', 0), s=120, c=color, edgecolors='black', linewidths=1.0, zorder=3)
        label = player.get('label') or player.get('role')
        if label:
            ax.text(player.get('x', 0), player.get('y', 0), label, color='black', ha='center', va='center', fontsize=8, zorder=4)

    # Cones/equipment
    for cone in diagram.get('cones', []):
        ax.scatter(cone.get('x', 0), cone.get('y', 0), marker='^', s=80, c='#f39c12', edgecolors='black', zorder=2)

    # Arrows
    for arrow in diagram.get('arrows', []):
        start = arrow.get('from') or arrow.get('start')
        end = arrow.get('to') or arrow.get('end')
        if not start or not end:
            continue
        color = '#ffffff' if arrow.get('type') == 'run' else '#ffeb3b'
        arrow_style = '-|>' if arrow.get('type') != 'run' else '->'
        ax.annotate('', xy=(end[0], end[1]), xytext=(start[0], start[1]),
                    arrowprops=dict(arrowstyle=arrow_style, color=color, linewidth=2.0, shrinkA=0, shrinkB=0))

    ax.invert_yaxis()
    fig.tight_layout()
    return fig


def save_diagram(diagram: dict, output_path: Path | str):
    """Render diagram metadata and save to disk.

    Falls back to a lightweight SVG writer when matplotlib is unavailable.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if plt is not None:
        fig = draw_diagram(diagram)
        fig.savefig(output_path, bbox_inches='tight', transparent=True)
        plt.close(fig)
    else:
        _write_svg_diagram(diagram, output_path)


def _write_svg_diagram(diagram: dict, output_path: Path):
    """Fallback SVG generator used when matplotlib is missing."""
    field_w, field_h = diagram.get("field_dimensions", [100, 70])
    scale_x = 6  # simple scaling factors to give us ~600px width
    scale_y = 6
    width = field_w * scale_x + 40
    height = field_h * scale_y + 40

    def _sx(val):
        return 20 + val * scale_x

    def _sy(val):
        return 20 + val * scale_y

    svg_parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        f"<rect x='20' y='20' width='{field_w * scale_x}' height='{field_h * scale_y}' rx='20' ry='20' fill='{FIELD_COLOR}' stroke='{LINE_COLOR}' stroke-width='4'/>",
        f"<line x1='{_sx(field_w/2)}' y1='20' x2='{_sx(field_w/2)}' y2='{_sy(field_h)}' stroke='{LINE_COLOR}' stroke-width='2' stroke-dasharray='10 10'/>"
    ]

    for player in diagram.get('players', []):
        color = PLAYER_COLORS.get(player.get('team', '').lower(), '#ffffff')
        x = _sx(player.get('x', 0))
        y = _sy(player.get('y', 0))
        label = player.get('label') or player.get('role', '')
        svg_parts.append(f"<circle cx='{x}' cy='{y}' r='16' fill='{color}' stroke='black' stroke-width='1.5' />")
        if label:
            svg_parts.append(f"<text x='{x}' y='{y + 4}' text-anchor='middle' font-size='12' font-family='Segoe UI, Arial'>{label}</text>")

    for cone in diagram.get('cones', []):
        x = _sx(cone.get('x', 0))
        y = _sy(cone.get('y', 0))
        svg_parts.append(f"<polygon points='{x},{y-10} {x-10},{y+10} {x+10},{y+10}' fill='#f39c12' stroke='black' stroke-width='1' />")

    for arrow in diagram.get('arrows', []):
        start = arrow.get('from') or arrow.get('start')
        end = arrow.get('to') or arrow.get('end')
        if not start or not end:
            continue
        color = '#ffffff' if arrow.get('type') == 'run' else '#ffeb3b'
        svg_parts.append(
            f"<defs><marker id='arrowhead' markerWidth='10' markerHeight='7' refX='10' refY='3.5' orient='auto'>"
            f"<polygon points='0 0, 10 3.5, 0 7' fill='{color}'/></marker></defs>"
        )
        svg_parts.append(
            f"<line x1='{_sx(start[0])}' y1='{_sy(start[1])}' x2='{_sx(end[0])}' y2='{_sy(end[1])}' "
            f"stroke='{color}' stroke-width='3' marker-end='url(#arrowhead)' />"
        )

    svg_parts.append("</svg>")
    output_path.write_text("\n".join(svg_parts), encoding='utf-8')


def render_diagram(drill_id: str, diagram_path: str | None = None) -> bool:
    """
    Render an existing diagram image for a drill. Returns True if rendered.
    Looks for an explicit diagram_path first, otherwise tries assets/diagrams/{drill_id}.{png|svg|jpg}.
    """
    if st is None:
        return False
    candidates = []
    if diagram_path:
        candidates.append(config.get_diagram_file(diagram_path))
    diagram_dir = config.DIAGRAMS_DIR
    for ext in (".png", ".svg", ".jpg", ".jpeg"):
        candidates.append(diagram_dir / f"{drill_id}{ext}")

    for candidate in candidates:
        if not candidate:
            continue
        if not Path(candidate).exists():
            continue
        suffix = Path(candidate).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".svg"}:
            logging.warning("Unsupported diagram file type for %s", candidate)
            continue
        try:
            st.image(str(candidate), use_container_width=True)
            return True
        except Exception as exc:
            logging.warning("Failed to render diagram %s: %s", candidate, exc)
            continue
    st.caption("Diagram file not found or unsupported.")
    return False


__all__ = ["draw_diagram", "save_diagram", "render_diagram"]
