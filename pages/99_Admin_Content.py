import streamlit as st
import sys
import os
import datetime
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

st.set_page_config(
    page_title="Admin Content | Player AI",
    page_icon="🔐",
    layout="wide",
)

ADMIN_PASSWORD = os.environ.get(
    "PLAYER_AI_ADMIN_PASSWORD", "AdminPlayerAI2026"
)

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.title("🔐 Admin Access")
    pwd = st.text_input("Admin password", type="password")
    if st.button("Login"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# authenticated
st.title("🛡️ Admin Content Editor")
st.write("Manage drill library video links, schematic diagrams, beta status, and sync changes with GitHub.")

# Display persistent success message if it exists
if "admin_success_msg" in st.session_state:
    st.success(st.session_state.admin_success_msg)
    del st.session_state.admin_success_msg

# Load drill library CSV
CSV_PATH = Path("data/production/drill_library.csv")
df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

SCHEMATIC_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    margin: 0;
    padding: 8px;
    background-color: #0e1117;
    color: #fafafa;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    user-select: none;
    overflow: hidden;
  }
  .toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-start;
    gap: 10px;
    margin-bottom: 8px;
    background: #1a1c23;
    padding: 6px 10px;
    border-radius: 8px;
    border: 1px solid #2e3344;
  }
  .toolbar-section {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .section-title {
    font-size: 10px;
    color: #888;
    margin-right: 4px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .toolbar button, .lbtn {
    padding: 4px 9px;
    font-size: 11px;
    border: 0.5px solid #ccc;
    border-radius: 6px;
    background: #1e1e1e;
    color: #ccc;
    cursor: pointer;
    outline: none;
    transition: all 0.1s ease;
  }
  .toolbar button:hover, .lbtn:hover {
    background: #2d2d2d;
    color: #fff;
  }
  .toolbar button.active, .lbtn.active {
    background: #1e3a8a;
    color: #93c5fd;
    border-color: #3b82f6;
  }
  .color-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.4);
    cursor: pointer;
    padding: 0 !important;
    outline: none;
    transition: transform 0.1s ease;
    margin: 0 2px;
  }
  .color-dot:hover {
    transform: scale(1.2);
  }
  .color-dot.active {
    transform: scale(1.3);
    border: 2px solid #93c5fd !important;
    box-shadow: 0 0 4px #93c5fd;
  }
  #schematicCanvas {
    display: block;
    margin: 0 auto;
    border: 1px solid #2e3344;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
  }
</style>
</head>
<body>

<div class="toolbar" id="layout-bar">
  <div class="toolbar-section">
    <span class="section-title">Layout:</span>
    <button id="lbtn-open" class="lbtn" onclick="setLayout('open')">Open Space</button>
    <button id="lbtn-half" class="lbtn" onclick="setLayout('half')">Half Field</button>
    <button id="lbtn-attacking" class="lbtn" onclick="setLayout('attacking')">Attacking Third</button>
    <button id="lbtn-full" class="lbtn" onclick='setLayout("full")'>Full Field</button>
    <button id="lbtn-grid" class="lbtn" onclick="setLayout('grid')">Grid</button>
  </div>
</div>

<div class="toolbar">
  <div class="toolbar-section">
    <span class="section-title">Place:</span>
    <button id="btn-select" class="active" onclick="setTool('select')">Select</button>
    <button id="btn-player" onclick="setTool('player')">Player</button>
    <button id="btn-cone" onclick="setTool('cone')">Cone</button>
    <button id="btn-ball" onclick="setTool('ball')">Ball</button>
  </div>
  
  <div class="toolbar-section">
    <span class="section-title">Draw:</span>
    <button id="btn-dribble" onclick="setTool('dribble')">Dribble</button>
    <button id="btn-pass" onclick="setTool('pass')">Pass</button>
    <button id="btn-shoot" onclick="setTool('shoot')">Shoot</button>
    <button id="btn-run" onclick="setTool('run')">Run</button>
    <button id="btn-zone" onclick="setTool('zone')">Zone</button>
  </div>
  
  <div class="toolbar-section">
    <span class="section-title">Colors:</span>
    <button class="color-dot active" data-color="#ffffff" style="background: #ffffff;" onclick="setColor('#ffffff')"></button>
    <button class="color-dot" data-color="#4FC3F7" style="background: #4FC3F7;" onclick="setColor('#4FC3F7')"></button>
    <button class="color-dot" data-color="#FF6B35" style="background: #FF6B35;" onclick="setColor('#FF6B35')"></button>
    <button class="color-dot" data-color="#FFD54F" style="background: #FFD54F;" onclick="setColor('#FFD54F')"></button>
    <button class="color-dot" data-color="#66BB6A" style="background: #66BB6A;" onclick="setColor('#66BB6A')"></button>
    <button class="color-dot" data-color="#EF5350" style="background: #EF5350;" onclick="setColor('#EF5350')"></button>
    <button class="color-dot" data-color="#CE93D8" style="background: #CE93D8;" onclick="setColor('#CE93D8')"></button>
  </div>
  
  <div class="toolbar-section" style="margin-left: auto;">
    <button onclick="undo()">Undo</button>
    <button onclick="clearCanvas()">Clear</button>
    <button style="background: #0f766e; color: #ccfbf1; border-color: #0d9488;" onclick="exportPNG()">Export PNG</button>
  </div>
</div>

<canvas id="schematicCanvas" width="660" height="400"></canvas>
<span id="drill_id_label" style="display:none;">__DRILL_ID__</span>
<input type="hidden" id="schematic_png_data" name="schematic_png_data">

<script>
const canvas = document.getElementById('schematicCanvas');
const ctx = canvas.getContext('2d');

let elements = [];
let history = [];
let activeTool = 'select';
let activeColor = '#ffffff';
let activeLayout = 'full';

function setLayout(layout) {
  activeLayout = layout;
  const buttons = document.querySelectorAll('.lbtn');
  buttons.forEach(btn => {
    if (btn.id === 'lbtn-' + layout) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  draw();
}

// Drag/Selection state
let selectedElement = null;
let isDragging = false;
let dragOffsets = {};

// Two-Click Arrow and Zone State
let arrowStartPoint = null;
let currentMousePos = { x: 0, y: 0 };
let zoneStartPoint = null;
let isDrawingZone = false;

window.onload = function() {
  setLayout('full');
};

function saveHistory() {
  if (history.length >= 40) {
    history.shift();
  }
  history.push(JSON.parse(JSON.stringify(elements)));
}

function undo() {
  if (history.length > 0) {
    elements = history.pop();
    selectedElement = null;
    draw();
  }
}

function clearCanvas() {
  saveHistory();
  elements = [];
  selectedElement = null;
  draw();
}

function setTool(tool) {
  activeTool = tool;
  const buttons = document.querySelectorAll('.toolbar button');
  buttons.forEach(btn => {
    if (btn.id === 'btn-' + tool) {
      btn.classList.add('active');
    } else if (btn.id && btn.id.startsWith('btn-')) {
      btn.classList.remove('active');
    }
  });
  
  arrowStartPoint = null;
  zoneStartPoint = null;
  isDrawingZone = false;
  
  if (tool !== 'select') {
    selectedElement = null;
  }
  
  draw();
}

function setColor(color) {
  activeColor = color;
  const dots = document.querySelectorAll('.color-dot');
  dots.forEach(dot => {
    if (dot.getAttribute('data-color').toLowerCase() === color.toLowerCase()) {
      dot.classList.add('active');
    } else {
      dot.classList.remove('active');
    }
  });

  if (selectedElement && (selectedElement.type === 'player' || selectedElement.type === 'zone' || selectedElement.type === 'arrow')) {
    if (selectedElement.type === 'arrow' && selectedElement.arrowType === 'shoot') {
      // Shoot is always red
    } else {
      saveHistory();
      selectedElement.color = color;
      draw();
    }
  }
}

function drawFieldBackdrop() {
  // Green backdrop
  ctx.fillStyle = '#2d5a1b';
  ctx.fillRect(0, 0, 660, 400);

  // 8 stripes
  const stripeW = 660 / 8;
  ctx.fillStyle = 'rgba(0, 0, 0, 0.06)';
  for (let i = 0; i < 8; i++) {
    if (i % 2 === 1) {
      ctx.fillRect(i * stripeW, 0, stripeW, 400);
    }
  }

  // Draw lines based on activeLayout
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
  ctx.lineWidth = 1.5;

  if (activeLayout === 'full') {
    const scX2 = 600/105, scY2 = 360/68;
    const fx = (m) => 30 + m * scX2;
    const fy = (m) => 20 + m * scY2;
    const fw = (m) => m * scX2;
    const fh = (m) => m * scY2;

    // 1. Outer boundary:
    ctx.strokeRect(30, 20, 600, 360);

    // 2. Center line:
    ctx.beginPath();
    ctx.moveTo(330, 20); ctx.lineTo(330, 380); ctx.stroke();

    // 3. Center circle (9.15m radius):
    ctx.beginPath();
    ctx.arc(330, 200, fh(9.15), 0, Math.PI*2);
    ctx.stroke();

    // 4. Center spot:
    ctx.fillStyle = 'rgba(255,255,255,0.65)';
    ctx.beginPath(); ctx.arc(330, 200, 3, 0, Math.PI*2);
    ctx.fill();

    // 5. LEFT penalty box (16.5m deep × 40.32m wide, centered):
    ctx.strokeRect(30, fy((68-40.32)/2), fw(16.5), fh(40.32));

    // 6. LEFT 6-yard box (5.5m deep × 18.32m wide):
    ctx.strokeRect(30, fy((68-18.32)/2), fw(5.5), fh(18.32));

    // 7. LEFT goal (2.44m deep × 7.32m wide):
    ctx.strokeRect(30 - fw(2.44), fy((68-7.32)/2), fw(2.44), fh(7.32));

    // 8. LEFT penalty spot (11m from left goal line):
    ctx.fillStyle = 'rgba(255,255,255,0.65)';
    ctx.beginPath();
    ctx.arc(fx(11), fy(34), 3, 0, Math.PI*2);
    ctx.fill();

    // 9. LEFT penalty arc — elliptical, connects to box edge
    {
      const arcCX = fx(11);
      const arcCY = fy(34);
      const arcRX = fw(9.15);  // horizontal radius
      const arcRY = fh(9.15);  // vertical radius
      const boxRightX = 30 + fw(16.5);
      const cosA = (boxRightX - arcCX) / arcRX;
      const arcA = Math.acos(Math.min(1, Math.max(-1, cosA)));
      ctx.save();
      ctx.translate(arcCX, arcCY);
      ctx.scale(1, arcRY / arcRX);
      ctx.beginPath();
      ctx.arc(0, 0, arcRX, -arcA, arcA);
      ctx.restore();
      ctx.stroke();
    }

    // 10. RIGHT penalty box (mirrored: starts at 105-16.5 = 88.5m):
    ctx.strokeRect(fx(88.5), fy((68-40.32)/2), fw(16.5), fh(40.32));

    // 11. RIGHT 6-yard box (starts at 105-5.5 = 99.5m):
    ctx.strokeRect(fx(99.5), fy((68-18.32)/2), fw(5.5), fh(18.32));

    // 12. RIGHT goal (starts at 105m = right edge):
    ctx.strokeRect(fx(105), fy((68-7.32)/2), fw(2.44), fh(7.32));

    // 13. RIGHT penalty spot (11m from right = 94m from left):
    ctx.fillStyle = 'rgba(255,255,255,0.65)';
    ctx.beginPath();
    ctx.arc(fx(94), fy(34), 3, 0, Math.PI*2);
    ctx.fill();

    // 14. RIGHT penalty arc — elliptical, connects to box edge
    {
      const arcCX = fx(94);
      const arcCY = fy(34);
      const arcRX = fw(9.15);
      const arcRY = fh(9.15);
      const boxLeftX = fx(88.5);
      const cosA = (arcCX - boxLeftX) / arcRX;
      const arcA = Math.acos(Math.min(1, Math.max(-1, cosA)));
      ctx.save();
      ctx.translate(arcCX, arcCY);
      ctx.scale(1, arcRY / arcRX);
      ctx.beginPath();
      ctx.arc(0, 0, arcRX, Math.PI - arcA, Math.PI + arcA);
      ctx.restore();
      ctx.stroke();
    }

  } else if (activeLayout === 'half') {
    // Outer boundary
    ctx.strokeRect(30, 20, 590, 360);

    // Goal (extends left of x=30)
    ctx.strokeRect(12, 175, 18, 50);

    // Penalty box
    ctx.strokeRect(30, 115, 130, 170);

    // 6-yard box
    ctx.strokeRect(30, 160, 48, 80);

    // Penalty spot
    ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
    ctx.beginPath();
    ctx.arc(118, 200, 3, 0, 2 * Math.PI);
    ctx.fill();

    // Penalty arc
    ctx.beginPath();
    ctx.arc(118, 200, 55, -0.75, 0.75);
    ctx.stroke();

    // Center arc hint at right edge
    ctx.beginPath();
    ctx.arc(620, 200, 55, Math.PI * 0.45, Math.PI * 1.55);
    ctx.stroke();

  } else if (activeLayout === 'attacking') {
    // Scale: 42m deep (left→right) × 68m wide (top→bottom)
    // mapped to 600px × 360px drawable area
    const scXa = 600 / 42;  // px per metre, horizontal
    const scYa = 360 / 68;  // px per metre, vertical
    const ax = (m) => 30 + m * scXa;   // metres from left edge
    const ay = (m) => 20 + m * scYa;   // metres from top edge
    const aw = (m) => m * scXa;         // horizontal distance
    const ah = (m) => m * scYa;         // vertical distance

    ctx.strokeStyle = 'rgba(255,255,255,0.65)';
    ctx.lineWidth = 1.5;

    // 1. Outer boundary
    ctx.strokeRect(30, 20, 600, 360);

    // 2. Penalty box
    // 16.5m deep from goal line (horizontal), 40.32m wide (vertical)
    // Centered on pitch (pitch is 68m, box is 40.32m wide)
    const boxLeft   = 30;
    const boxTop    = ay((68 - 40.32) / 2);
    const boxWidth  = aw(16.5);          // 94px horizontal depth
    const boxHeight = ah(40.32);         // 213px vertical width
    ctx.strokeRect(boxLeft, boxTop, boxWidth, boxHeight);

    // 3. 6-yard box
    const s6Left   = 30;
    const s6Top    = ay((68 - 18.32) / 2);
    const s6Width  = aw(5.5);            // 31px horizontal
    const s6Height = ah(18.32);          // 97px vertical
    ctx.strokeRect(s6Left, s6Top, s6Width, s6Height);

    // 4. Goal (extends left off canvas edge, 7.32m wide vertically)
    const goalTop    = ay((68 - 7.32) / 2);
    const goalHeight = ah(7.32);         // 39px
    const goalDepth  = aw(2.44);         // 14px off left edge
    ctx.strokeRect(30 - goalDepth, goalTop, goalDepth, goalHeight);

    // 5. Penalty spot at 11m from goal line, center of pitch
    const pspotX = ax(11);
    const pspotY = ay(34);
    ctx.fillStyle = 'rgba(255,255,255,0.65)';
    ctx.beginPath();
    ctx.arc(pspotX, pspotY, 3, 0, Math.PI * 2);
    ctx.fill();

    // 6. Penalty arc — the D shape outside the penalty box
    // Use ctx.save/restore + scale to draw an elliptical arc
    // that respects the different horizontal/vertical scales
    const arcCenterX = pspotX;  // ax(11)
    const arcCenterY = pspotY;  // ay(34)
    const arcRadiusX = aw(9.15);  // horizontal radius in px
    const arcRadiusY = ah(9.15);  // vertical radius in px
    const boxEdgeX = 30 + aw(16.5);  // right edge of penalty box

    // Calculate angle where ellipse meets the box edge
    // (boxEdgeX - arcCenterX) / arcRadiusX = cos(angle)
    const cosAngle = (boxEdgeX - arcCenterX) / arcRadiusX;
    const arcAngle = Math.acos(Math.min(1, Math.max(-1, cosAngle)));

    ctx.save();
    ctx.translate(arcCenterX, arcCenterY);
    ctx.scale(1, arcRadiusY / arcRadiusX);
    ctx.beginPath();
    ctx.arc(0, 0, arcRadiusX, -arcAngle, arcAngle);
    ctx.restore();
    ctx.stroke();

    // 7. Attacking third line at 35m (dashed)
    const thirdX = ax(35);
    ctx.strokeStyle = 'rgba(255,255,255,0.28)';
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(thirdX, 20);
    ctx.lineTo(thirdX, 380);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';

    // 8. Horizontal channel lines (left channel, half-space, centre)
    ctx.strokeStyle = 'rgba(255,255,255,0.18)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 5]);
    [68 / 3, (68 * 2) / 3].forEach(m => {
      ctx.beginPath();
      ctx.moveTo(30, ay(m));
      ctx.lineTo(630, ay(m));
      ctx.stroke();
    });
    ctx.setLineDash([]);
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';

  } else if (activeLayout === 'grid') {
    // Interior grid lines — subtle
    const cols = 10, rows = 6;
    const cw = 600 / cols;   // 60px per column
    const ch = 360 / rows;   // 60px per row

    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.lineWidth = 1;

    for (let i = 1; i < cols; i++) {
      ctx.beginPath();
      ctx.moveTo(30 + i * cw, 20);
      ctx.lineTo(30 + i * cw, 380);
      ctx.stroke();
    }
    for (let j = 1; j < rows; j++) {
      ctx.beginPath();
      ctx.moveTo(30, 20 + j * ch);
      ctx.lineTo(630, 20 + j * ch);
      ctx.stroke();
    }

    // Emphasized center crosshair
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(330, 20); ctx.lineTo(330, 380); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(30, 200); ctx.lineTo(630, 200); ctx.stroke();

    // Strong outer boundary — drawn LAST so it sits on top
    ctx.strokeStyle = 'rgba(255,255,255,0.9)';
    ctx.lineWidth = 3;
    ctx.strokeRect(30, 20, 600, 360);

    // Reinforce right edge explicitly
    ctx.beginPath();
    ctx.moveTo(630, 20);
    ctx.lineTo(630, 380);
    ctx.strokeStyle = 'rgba(255,255,255,0.9)';
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';
    ctx.lineWidth = 1.5;

    // Reset
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';
    ctx.lineWidth = 1.5;
  }
}

function drawWavyBezier(ctx, x1, y1, cx, cy, x2, y2, color, strokeWidth) {
  ctx.strokeStyle = color;
  ctx.lineWidth = strokeWidth;
  ctx.beginPath();
  
  let prevX = x1, prevY = y1;
  let totalDist = 0;
  let points = [];
  
  for (let i = 0; i <= 100; i++) {
    let t = i / 100;
    let mt = 1 - t;
    let bx = mt * mt * x1 + 2 * mt * t * cx + t * t * x2;
    let by = mt * mt * y1 + 2 * mt * t * cy + t * t * y2;
    
    let dx = 2 * mt * (cx - x1) + 2 * t * (x2 - cx);
    let dy = 2 * mt * (cy - y1) + 2 * t * (x2 - cy);
    let len = Math.sqrt(dx * dx + dy * dy);
    
    let nx = 0, ny = 0;
    if (len > 0) {
      nx = -dy / len;
      ny = dx / len;
    }
    
    if (i > 0) {
      let segDist = Math.sqrt((bx - prevX) * (bx - prevX) + (by - prevY) * (by - prevY));
      totalDist += segDist;
    }
    prevX = bx;
    prevY = by;
    
    points.push({ t, bx, by, nx, ny, dist: totalDist });
  }
  
  ctx.moveTo(x1, y1);
  for (let i = 1; i <= 100; i++) {
    let pt = points[i];
    let envelope = Math.sin(pt.t * Math.PI);
    let wave = 5 * envelope * Math.sin((2 * Math.PI * pt.dist) / 12);
    let wx = pt.bx + pt.nx * wave;
    let wy = pt.by + pt.ny * wave;
    ctx.lineTo(wx, wy);
  }
  ctx.stroke();
}

function drawArrowhead(ctx, x, y, angle, color, size) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x - size * Math.cos(angle - Math.PI / 6), y - size * Math.sin(angle - Math.PI / 6));
  ctx.lineTo(x - size * Math.cos(angle + Math.PI / 6), y - size * Math.sin(angle + Math.PI / 6));
  ctx.closePath();
  ctx.fill();
}

function drawElement(el) {
  const isSelected = (selectedElement && selectedElement.id === el.id);

  if (el.type === 'arrow' && el.playerId) {
    const player = elements.find(p => p.type === 'player' && p.id === el.playerId);
    if (player) {
      el.x1 = player.x;
      el.y1 = player.y;
    }
  }

  if (el.type === 'player') {
    ctx.fillStyle = el.color;
    ctx.beginPath();
    ctx.arc(el.x, el.y, 11, 0, 2 * Math.PI);
    ctx.fill();
    
    ctx.strokeStyle = 'rgba(0,0,0,0.2)';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 11px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(el.number, el.x, el.y);

    if (isSelected) {
      ctx.strokeStyle = '#FFD54F';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.arc(el.x, el.y, 15, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  } else if (el.type === 'cone') {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.beginPath();
    ctx.ellipse(el.x, el.y + 8, 10, 3, 0, 0, 2 * Math.PI);
    ctx.fill();

    ctx.fillStyle = '#FF6B35';
    ctx.beginPath();
    ctx.moveTo(el.x, el.y - 11);
    ctx.lineTo(el.x - 9, el.y + 8);
    ctx.lineTo(el.x + 9, el.y + 8);
    ctx.closePath();
    ctx.fill();
    
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.lineWidth = 1;
    ctx.stroke();

    if (isSelected) {
      ctx.strokeStyle = '#FFD54F';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.arc(el.x, el.y, 15, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  } else if (el.type === 'ball') {
    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(el.x, el.y, 7, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#000000';
    ctx.beginPath();
    for (let i = 0; i < 5; i++) {
      let angle = (i * 2 * Math.PI / 5) - Math.PI / 2;
      let px = el.x + 2.5 * Math.cos(angle);
      let py = el.y + 2.5 * Math.sin(angle);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();

    ctx.beginPath();
    for (let i = 0; i < 5; i++) {
      let angle = (i * 2 * Math.PI / 5) - Math.PI / 2;
      let px1 = el.x + 2.5 * Math.cos(angle);
      let py1 = el.y + 2.5 * Math.sin(angle);
      let px2 = el.x + 7 * Math.cos(angle);
      let py2 = el.y + 7 * Math.sin(angle);
      ctx.moveTo(px1, py1);
      ctx.lineTo(px2, py2);
    }
    ctx.stroke();

    if (isSelected) {
      ctx.strokeStyle = '#FFD54F';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.arc(el.x, el.y, 11, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  } else if (el.type === 'arrow') {
    let strokeColor = el.color;
    
    if (el.arrowType === 'dribble') {
      let x1 = el.x1, y1 = el.y1, x2 = el.x2, y2 = el.y2;
      let dx = x2 - x1;
      let dy = y2 - y1;
      let len = Math.sqrt(dx * dx + dy * dy);
      let mx = (x1 + x2) / 2;
      let my = (y1 + y2) / 2;
      let nx = -dy / (len || 1);
      let ny = dx / (len || 1);
      let cx = mx + nx * (len * 0.12);
      let cy = my + ny * (len * 0.12);
      
      drawWavyBezier(ctx, x1, y1, cx, cy, x2, y2, strokeColor, 2);
      
      let angle = Math.atan2(y2 - cy, x2 - cx);
      drawArrowhead(ctx, x2, y2, angle, strokeColor, 10);
    } else {
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = (el.arrowType === 'shoot') ? 3.5 : 2;
      
      if (el.arrowType === 'pass') {
        ctx.setLineDash([8, 6]);
      } else if (el.arrowType === 'run') {
        ctx.setLineDash([3, 5]);
      } else {
        ctx.setLineDash([]);
      }
      
      ctx.beginPath();
      ctx.moveTo(el.x1, el.y1);
      ctx.lineTo(el.x2, el.y2);
      ctx.stroke();
      ctx.setLineDash([]);
      
      let angle = Math.atan2(el.y2 - el.y1, el.x2 - el.x1);
      let arrowheadSize = (el.arrowType === 'shoot') ? 12 : 10;
      drawArrowhead(ctx, el.x2, el.y2, angle, strokeColor, arrowheadSize);
    }

    if (isSelected) {
      ctx.strokeStyle = '#FFD54F';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.arc(el.x1, el.y1, 5, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(el.x2, el.y2, 5, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  } else if (el.type === 'zone') {
    ctx.fillStyle = el.color;
    ctx.strokeStyle = el.color;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);

    ctx.globalAlpha = 0.12;
    ctx.fillRect(el.x, el.y, el.w, el.h);
    
    ctx.globalAlpha = 0.5;
    ctx.strokeRect(el.x, el.y, el.w, el.h);
    
    ctx.globalAlpha = 1.0;
    ctx.setLineDash([]);

    if (isSelected) {
      ctx.strokeStyle = '#FFD54F';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(el.x - 2, el.y - 2, el.w + 4, el.h + 4);
      ctx.setLineDash([]);
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawFieldBackdrop();
  
  for (let el of elements) {
    drawElement(el);
  }
  
  if (arrowStartPoint) {
    ctx.fillStyle = '#FFD54F';
    ctx.beginPath();
    ctx.arc(arrowStartPoint.x, arrowStartPoint.y, 4, 0, 2 * Math.PI);
    ctx.fill();
    
    ctx.strokeStyle = activeColor;
    ctx.lineWidth = (activeTool === 'shoot') ? 3.5 : 2;
    if (activeTool === 'pass') ctx.setLineDash([8, 6]);
    else if (activeTool === 'run') ctx.setLineDash([3, 5]);
    else ctx.setLineDash([]);
    
    ctx.beginPath();
    ctx.moveTo(arrowStartPoint.x, arrowStartPoint.y);
    ctx.lineTo(currentMousePos.x, currentMousePos.y);
    ctx.stroke();
    ctx.setLineDash([]);
  } else if (activeTool === 'zone' && isDrawingZone && zoneStartPoint) {
    ctx.fillStyle = activeColor;
    ctx.strokeStyle = activeColor;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);
    
    let x = Math.min(zoneStartPoint.x, currentMousePos.x);
    let y = Math.min(zoneStartPoint.y, currentMousePos.y);
    let w = Math.abs(zoneStartPoint.x - currentMousePos.x);
    let h = Math.abs(zoneStartPoint.y - currentMousePos.y);
    
    ctx.globalAlpha = 0.12;
    ctx.fillRect(x, y, w, h);
    ctx.globalAlpha = 0.5;
    ctx.strokeRect(x, y, w, h);
    
    ctx.globalAlpha = 1.0;
    ctx.setLineDash([]);
  }
}

function getPlayerWithinDistance(x, y, maxDist) {
  let nearestPlayer = null;
  let minDist = maxDist;
  for (let el of elements) {
    if (el.type === 'player') {
      let dist = Math.sqrt((x - el.x) * (x - el.x) + (y - el.y) * (y - el.y));
      if (dist < minDist) {
        minDist = dist;
        nearestPlayer = el;
      }
    }
  }
  return nearestPlayer;
}

function getElementAt(x, y) {
  for (let i = elements.length - 1; i >= 0; i--) {
    let el = elements[i];
    if (el.type === 'player' || el.type === 'cone') {
      let dist = Math.sqrt((x - el.x) * (x - el.x) + (y - el.y) * (y - el.y));
      if (dist <= 15) return el;
    } else if (el.type === 'ball') {
      let dist = Math.sqrt((x - el.x) * (x - el.x) + (y - el.y) * (y - el.y));
      if (dist <= 11) return el;
    } else if (el.type === 'zone') {
      if (x >= el.x && x <= el.x + el.w && y >= el.y && y <= el.y + el.h) {
        return el;
      }
    } else if (el.type === 'arrow') {
      let dist = getDistanceToSegment(x, y, el.x1, el.y1, el.x2, el.y2);
      if (dist <= 12) return el;
    }
  }
  return null;
}

function getDistanceToSegment(x, y, x1, y1, x2, y2) {
  let dx = x2 - x1;
  let dy = y2 - y1;
  let l2 = dx * dx + dy * dy;
  if (l2 === 0) return Math.sqrt((x - x1) * (x - x1) + (y - y1) * (y - y1));
  let t = ((x - x1) * dx + (y - y1) * dy) / l2;
  t = Math.max(0, Math.min(1, t));
  let px = x1 + t * dx;
  let py = y1 + t * dy;
  return Math.sqrt((x - px) * (x - px) + (y - py) * (y - py));
}

canvas.addEventListener('mousedown', function(e) {
  const rect = canvas.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;
  
  if (activeTool === 'select') {
    let el = getElementAt(clickX, clickY);
    if (el) {
      saveHistory();
      selectedElement = el;
      isDragging = true;
      if (el.type === 'arrow') {
        dragOffsets = {
          x1: clickX - el.x1,
          y1: clickY - el.y1,
          x2: clickX - el.x2,
          y2: clickY - el.y2
        };
      } else {
        dragOffsets = {
          x: clickX - el.x,
          y: clickY - el.y
        };
      }
    } else {
      selectedElement = null;
    }
    draw();
  } else if (activeTool === 'player') {
    saveHistory();
    let maxNum = 0;
    for (let el of elements) {
      if (el.type === 'player' && el.number > maxNum) {
        maxNum = el.number;
      }
    }
    const playerNum = maxNum + 1;
    elements.push({
      type: 'player',
      id: 'p' + playerNum + '_' + Date.now(),
      x: clickX,
      y: clickY,
      number: playerNum,
      color: activeColor
    });
    draw();
  } else if (activeTool === 'cone') {
    saveHistory();
    elements.push({
      type: 'cone',
      id: 'c' + Date.now() + Math.random().toString(36).substr(2, 5),
      x: clickX,
      y: clickY
    });
    draw();
  } else if (activeTool === 'ball') {
    saveHistory();
    elements.push({
      type: 'ball',
      id: 'b' + Date.now() + Math.random().toString(36).substr(2, 5),
      x: clickX,
      y: clickY
    });
    draw();
  } else if (activeTool === 'dribble' || activeTool === 'pass' || activeTool === 'shoot' || activeTool === 'run') {
    if (!arrowStartPoint) {
      let snapped = getPlayerWithinDistance(clickX, clickY, 40);
      if (snapped) {
        arrowStartPoint = { x: snapped.x, y: snapped.y, playerId: snapped.id };
      } else {
        arrowStartPoint = { x: clickX, y: clickY, playerId: null };
      }
      currentMousePos = { x: clickX, y: clickY };
      draw();
    } else {
      let dx = clickX - arrowStartPoint.x;
      let dy = clickY - arrowStartPoint.y;
      let dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 5) {
        saveHistory();
        elements.push({
          type: 'arrow',
          arrowType: activeTool,
          id: 'a' + Date.now() + Math.random().toString(36).substr(2, 5),
          x1: arrowStartPoint.x,
          y1: arrowStartPoint.y,
          x2: clickX,
          y2: clickY,
          color: activeTool === 'shoot' ? '#EF5350' : activeColor,
          playerId: arrowStartPoint.playerId
        });
      }
      arrowStartPoint = null;
      draw();
    }
  } else if (activeTool === 'zone') {
    zoneStartPoint = { x: clickX, y: clickY };
    isDrawingZone = true;
    currentMousePos = { x: clickX, y: clickY };
  }
});

canvas.addEventListener('mousemove', function(e) {
  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;
  currentMousePos = { x: mouseX, y: mouseY };

  if (activeTool === 'select' && isDragging && selectedElement) {
    let el = selectedElement;
    if (el.type === 'arrow') {
      el.x1 = mouseX - dragOffsets.x1;
      el.y1 = mouseY - dragOffsets.y1;
      el.x2 = mouseX - dragOffsets.x2;
      el.y2 = mouseY - dragOffsets.y2;
      el.playerId = null;
    } else {
      el.x = mouseX - dragOffsets.x;
      el.y = mouseY - dragOffsets.y;
    }
    draw();
  } else if (activeTool === 'zone' && isDrawingZone) {
    draw();
  } else if (arrowStartPoint) {
    draw();
  }
});

canvas.addEventListener('mouseup', function(e) {
  if (activeTool === 'select' && isDragging) {
    isDragging = false;
  } else if (activeTool === 'zone' && isDrawingZone && zoneStartPoint) {
    const rect = canvas.getBoundingClientRect();
    const releaseX = e.clientX - rect.left;
    const releaseY = e.clientY - rect.top;
    
    let x = Math.min(zoneStartPoint.x, releaseX);
    let y = Math.min(zoneStartPoint.y, releaseY);
    let w = Math.abs(zoneStartPoint.x - releaseX);
    let h = Math.abs(zoneStartPoint.y - releaseY);
    
    if (w > 5 && h > 5) {
      saveHistory();
      elements.push({
        type: 'zone',
        id: 'z' + Date.now() + Math.random().toString(36).substr(2, 5),
        x: x,
        y: y,
        w: w,
        h: h,
        color: activeColor
      });
    }
    
    isDrawingZone = false;
    zoneStartPoint = null;
    draw();
  }
});

window.addEventListener('keydown', function(e) {
  if ((e.key === 'Delete' || e.key === 'Backspace') && selectedElement) {
    saveHistory();
    elements = elements.filter(el => el.id !== selectedElement.id);
    selectedElement = null;
    draw();
  }
});

function exportPNG() {
  const prevSelected = selectedElement;
  selectedElement = null;
  draw();
  
  const dataURL = canvas.toDataURL('image/png');
  document.getElementById('schematic_png_data').value = dataURL;
  
  const link = document.createElement('a');
  link.download = 'drill-schematic.png';
  link.href = dataURL;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  const drillId = document.getElementById('drill_id_label').textContent;
  window.parent.postMessage({
    type: 'schematic_export',
    data: dataURL,
    drill_id: drillId
  }, '*');
  
  selectedElement = prevSelected;
  draw();
}
</script>
</body>
</html>
"""

# Create tabs for cleaner layout
tab1, tab2 = st.tabs(["📋 Edit Drill Metadata", "🎨 Schematic Painter"])

with tab1:
    # Metrics Dashboard
    total = len(df)
    filmed = len(df[df["video_status"].str.lower() == "filmed"])
    published = len(df[df["video_status"].str.lower() == "published"])
    not_filmed = total - filmed - published
    beta_ready_count = len(df[df["beta_ready"].str.lower() == "true"])

    # Display as 4 metric columns
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Drills", total)
    with col_m2:
        st.metric("Filmed", filmed)
    with col_m3:
        st.metric("Beta Ready", beta_ready_count)
    with col_m4:
        st.metric("Not Filmed", not_filmed, delta=f"-{not_filmed} to go")

    # Progress bar
    if total > 0:
        pct = round((filmed + published) / total * 100)
    else:
        pct = 0
    st.progress(pct / 100, text=f"{pct}% of library has video")

    st.divider()

    # Filters
    st.subheader("🔍 Filters")
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        presenter_options = ["All"] + sorted(
            df["presenter_id"].unique().tolist()
        )
        selected_presenter = st.selectbox(
            "Filter by presenter", presenter_options, key="metadata_presenter_filter"
        )

    with filter_col2:
        status_options = ["All", "Not Filmed", "Filmed", "Published"]
        selected_status = st.selectbox(
            "Filter by video status", status_options, key="metadata_status_filter"
        )

    # Apply filters
    filtered_df = df.copy()
    if selected_presenter != "All":
        filtered_df = filtered_df[
            filtered_df["presenter_id"] == selected_presenter
        ]
    if selected_status != "All":
        filtered_df = filtered_df[
            filtered_df["video_status"].str.lower() ==
            selected_status.lower()
        ]

    # Drill Editor Cards
    st.subheader(f"📋 Drills ({len(filtered_df)})")

    for _, row in filtered_df.iterrows():
        drill_id = row["drill_id"]
        is_filmed = row.get("video_status", "").lower() in ["filmed", "published"]
        label = (
            f"{'✅' if is_filmed else '📹'} "
            f"{drill_id} — {row['drill_name']} "
            f"[{row.get('video_status', 'Not Filmed')}]"
        )
        with st.expander(label, expanded=not is_filmed):
            with st.form(key=f"form_{drill_id}"):
                # Current video preview
                current_url = row.get("video_url", "").strip()
                if current_url:
                    st.video(current_url)
                else:
                    st.info("No video linked yet.")

                col1, col2 = st.columns(2)

                with col1:
                    new_url = st.text_input(
                        "YouTube URL",
                        value=current_url,
                        key=f"url_{drill_id}"
                    )
                    
                    # Make sure the current status is mapped to valid option index
                    status_val = row.get("video_status", "not filmed").lower().strip()
                    status_list = ["not filmed", "filmed", "published"]
                    if status_val in status_list:
                        status_idx = status_list.index(status_val)
                    else:
                        status_idx = 0
                        
                    new_status = st.selectbox(
                        "Video status",
                        ["Not Filmed", "Filmed", "Published"],
                        index=status_idx,
                        key=f"status_{drill_id}"
                    )
                    new_beta = st.checkbox(
                        "Beta Ready",
                        value=row.get("beta_ready", "").lower() == "true",
                        key=f"beta_{drill_id}"
                    )

                with col2:
                    new_notes = st.text_area(
                        "Filming notes",
                        value=row.get("filming_notes", ""),
                        height=80,
                        key=f"notes_{drill_id}"
                    )
                    new_diagram = st.text_input(
                        "Schematic URL (diagram_url)",
                        value=row.get("diagram_url", ""),
                        key=f"diag_{drill_id}"
                    )
                    st.caption("Use the Schematic Painter tab to draw and export a diagram for this drill.")

                submitted = st.form_submit_button(
                    "💾 Save Changes", type="primary",
                    use_container_width=True
                )

                if submitted:
                    # Update the main df in place
                    idx = df.index[df["drill_id"] == drill_id][0]
                    df.at[idx, "video_url"]     = new_url
                    df.at[idx, "video_status"]  = new_status
                    df.at[idx, "beta_ready"]    = str(new_beta)
                    df.at[idx, "filming_notes"] = new_notes
                    df.at[idx, "diagram_url"]   = new_diagram
                    df.at[idx, "filming_date"]  = (
                        datetime.date.today().isoformat()
                        if new_status == "Filmed" else
                        row.get("filming_date", "")
                    )

                    # Write CSV
                    df.to_csv(CSV_PATH, index=False)

                    # Also update demo user sandbox if it exists
                    demo_csv = Path(
                        "data/production/users/demo/drill_library.csv"
                    )
                    if demo_csv.exists():
                        df.to_csv(demo_csv, index=False)
                    
                    st.session_state.admin_success_msg = f"✅ {drill_id} saved."
                    st.rerun()

with tab2:
    st.header("🎨 Schematic Painter")
    st.write("Draw soccer drill setups on top of tactical field backdrops and link them to the drill.")

    # Drill selector
    drill_names = [f"{row['drill_id']} — {row['drill_name']}"
                   for _, row in df.iterrows()]

    default_select_idx = 0
    if "newly_created_drill_id" in st.session_state:
        target_id = st.session_state.newly_created_drill_id
        matching_indices = df.index[df["drill_id"] == target_id].tolist()
        if matching_indices:
            default_select_idx = matching_indices[0]
        # Remove it from session state so it doesn't stick forever
        del st.session_state.newly_created_drill_id

    selected_idx = st.selectbox(
        "Select drill to build schematic for",
        range(len(drill_names)),
        index=default_select_idx,
        format_func=lambda i: drill_names[i],
        key="canvas_drill_select"
    )
    selected_drill_id = df.iloc[selected_idx]["drill_id"]
    drill_row = df.iloc[selected_idx]

    with st.expander("➕ Create a new drill instead", expanded=False):
        with st.form("create_new_drill_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Drill ID (unique identifier)", placeholder="e.g. TECH_010")
                new_name = st.text_input("Drill Name", placeholder="e.g. 1v1 Goal Attack")
                new_cat = st.selectbox("Category", [
                    "Ball Mastery",
                    "First Touch",
                    "Dribbling & Moves",
                    "Passing & Receiving",
                    "Finishing",
                    "Shooting Technique",
                    "1v1 Attacking",
                    "1v1 Defending",
                    "Weak Foot",
                    "Aerial & Headers",
                    "Speed & Agility",
                    "Strength & Fitness",
                    "Goalkeeping",
                    "Mental & Decision Making",
                    "Warmup & Cool Down",
                ])
                new_difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])
                new_intensity = st.selectbox("Intensity", ["low", "medium", "high"])
                new_duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=10)
                new_p_min = st.number_input("Min Players", min_value=1, max_value=50, value=2)
                new_p_max = st.number_input("Max Players", min_value=1, max_value=50, value=4)
            with col2:
                new_video_url = st.text_input(
                    "YouTube URL (optional)",
                    placeholder="https://www.youtube.com/watch?v=..."
                )
                new_desc = st.text_area("Description")
                new_setup = st.text_area("Setup Instructions")
                new_equip_list = st.multiselect(
                    "Equipment Required",
                    ["Ball", "Cones", "Goal", "Rebounder",
                     "Agility Ladder", "Poles/Sticks", "Bibs",
                     "Mannequin", "Speed Rings", "Mini Goals",
                     "Resistance Band", "None"],
                    default=["Ball", "Cones"]
                )
                new_equip = ", ".join(new_equip_list)
                new_coaching = st.text_area("Coaching Points")
                new_mistakes = st.text_area("Common Mistakes")
                new_tags_list = st.multiselect(
                    "Tags",
                    ["1v1", "dribbling", "passing", "finishing",
                     "first touch", "weak foot", "shooting",
                     "defending", "heading", "crossing", "speed",
                     "agility", "strength", "goalkeeping",
                     "ball mastery", "transition", "pressing",
                     "movement", "warmup", "solo"],
                    default=[]
                )
                new_tags = "|".join(new_tags_list)
            
            submitted_new = st.form_submit_button("➕ Create Drill", type="primary", use_container_width=True)
            
            if submitted_new:
                clean_id = new_id.strip().upper()
                clean_name = new_name.strip()
                if not clean_id:
                    st.error("❌ Drill ID cannot be empty.")
                elif not clean_name:
                    st.error("❌ Drill Name cannot be empty.")
                elif clean_id in df["drill_id"].values:
                    st.error(f"❌ Drill ID '{clean_id}' already exists.")
                else:
                    from data_loader import DRILL_DEFAULTS
                    new_row_data = DRILL_DEFAULTS.copy()
                    new_row_data.update({
                        "drill_id": clean_id,
                        "drill_name": clean_name,
                        "category": new_cat,
                        "difficulty": new_difficulty,
                        "intensity": new_intensity,
                        "duration_minutes": str(new_duration),
                        "players_min": str(new_p_min),
                        "players_max": str(new_p_max),
                        "description": new_desc,
                        "setup_data": new_setup,
                        "equipment": new_equip,
                        "coaching_points": new_coaching,
                        "common_mistakes": new_mistakes,
                        "tags": new_tags,
                        "video_url": new_video_url,
                        "video_status": "Filmed" if new_video_url.strip() else "Not Filmed",
                    })
                    # Map category to skill_category for RRS radar matching
                    skill_cat_map = {
                        "Ball Mastery": "Technical",
                        "First Touch": "Technical",
                        "Dribbling & Moves": "Dribbling",
                        "Passing & Receiving": "Passing",
                        "Finishing": "Finishing",
                        "Shooting Technique": "Finishing",
                        "1v1 Attacking": "Dribbling",
                        "1v1 Defending": "Defending",
                        "Weak Foot": "Technical",
                        "Aerial & Headers": "Technical",
                        "Speed & Agility": "Speed",
                        "Strength & Fitness": "Fitness",
                        "Goalkeeping": "Goalkeeping",
                        "Mental & Decision Making": "Technical",
                        "Warmup & Cool Down": "Fitness",
                    }
                    new_row_data["skill_category"] = skill_cat_map.get(
                        new_cat, "Technical"
                    )
                    # Make sure all columns in the DataFrame are strings
                    for k, v in new_row_data.items():
                        new_row_data[k] = str(v) if v is not None else ""
                    
                    new_df_row = pd.DataFrame([new_row_data])
                    new_df_row = new_df_row[df.columns]
                    
                    df_updated = pd.concat([df, new_df_row], ignore_index=True)
                    df_updated.to_csv(CSV_PATH, index=False)
                    
                    # Mirror to demo user sandbox if it exists
                    demo_csv = Path("data/production/users/demo/drill_library.csv")
                    if demo_csv.exists():
                        df_updated.to_csv(demo_csv, index=False)
                        
                    st.session_state.newly_created_drill_id = clean_id
                    st.session_state.admin_success_msg = f"✅ Drill '{clean_id}' successfully created!"
                    st.rerun()

    # Show existing schematic if one exists
    existing_url = drill_row.get("diagram_url", "").strip()
    if existing_url and "raw.githubusercontent" in existing_url:
        st.image(existing_url,
                 caption=f"Current schematic — {selected_drill_id}",
                 use_container_width=False, width=400)

    st.info(
        "🎨 Use the canvas below. Place players, cones, balls. "
        "Draw movement arrows. When done click **Export PNG** "
        "which downloads the file — then commit it to "
        f"`assets/diagrams/{selected_drill_id.lower()}.png` "
        "and paste the raw GitHub URL in the Drill Editor tab "
        "to link it to this drill."
    )

    # Default layout logic based on skill_category and focus
    skill_category = drill_row.get("skill_category", "").lower().strip()
    drill_name = drill_row.get("drill_name", "").lower()
    focus_tags = drill_row.get("focus_tags", "").lower()

    cat = skill_category
    if any(w in cat for w in
           ["finish", "shoot", "1v1 attack", "crossing"]):
        default_layout = "attacking"
    elif any(w in cat for w in
             ["pass", "receiv", "tactical", "defend",
              "1v1 def"]):
        default_layout = "half"
    elif any(w in cat for w in
             ["speed", "agility", "fitness", "strength",
              "warmup", "cool"]):
        default_layout = "open"
    elif any(w in cat for w in
             ["ball master", "dribbl", "move", "weak foot",
              "touch", "mental"]):
        default_layout = "open"
    elif "goalkeep" in cat:
        default_layout = "half"
    else:
        default_layout = "open"

    # Name/tag override
    if any(kw in drill_name or kw in focus_tags
           for kw in ["finish", "shoot", "cross",
                      "1v1 attack", "goal"]):
        default_layout = "attacking"

    # Inject the selected drill ID and default layout into the HTML
    html_with_drill = SCHEMATIC_HTML.replace(
        '__DRILL_ID__', selected_drill_id
    ).replace(
        "setLayout('full')", f"setLayout('{default_layout}')"
    )
    st.components.v1.html(html_with_drill, height=560,
                          scrolling=False)

    st.caption(
        "After exporting, commit the PNG to "
        "assets/diagrams/ and paste the raw GitHub URL below."
    )
    with st.form("save_schematic_url"):
        pasted_url = st.text_input(
            "Raw GitHub URL of exported schematic",
            value=existing_url,
            placeholder=(
                "https://raw.githubusercontent.com/"
                "eganl2024-sudo/MDP_APP/main/assets/diagrams/"
                f"{selected_drill_id.lower()}.png"
            )
        )
        if st.form_submit_button("💾 Save Schematic URL",
                                 type="primary"):
            idx = df.index[df["drill_id"]==selected_drill_id][0]
            df.at[idx, "diagram_url"] = pasted_url
            df.at[idx, "diagram_path"] = (
                f"assets/diagrams/"
                f"{selected_drill_id.lower()}.png"
            )
            df.to_csv(CSV_PATH, index=False)
            demo_csv = Path(
                "data/production/users/demo/drill_library.csv"
            )
            if demo_csv.exists():
                df.to_csv(demo_csv, index=False)
            st.session_state.admin_success_msg = (
                f"✅ Schematic URL saved for {selected_drill_id}"
            )
            st.rerun()

# Git push section
st.divider()
st.subheader("🚀 Publish to GitHub")
st.caption(
    "Pushes updated drill_library.csv and generated schematics to GitHub. "
    "Streamlit Cloud redeploys in ~60 seconds."
)

if st.button("Push to GitHub", type="primary", key="git_push_btn"):
    import subprocess
    # Stage CSV and any generated diagrams
    result = subprocess.run(
        ["git", "add", "data/production/drill_library.csv", "assets/diagrams/"],
        capture_output=True, text=True,
        cwd=str(Path.cwd())
    )
    if result.returncode != 0:
        st.error(f"git add failed: {result.stderr}")
    else:
        commit = subprocess.run(
            ["git", "commit", "-m", "Player AI — drill library content update"],
            capture_output=True, text=True,
            cwd=str(Path.cwd())
        )
        push = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True,
            cwd=str(Path.cwd())
        )
        if push.returncode == 0:
            st.success("✅ Pushed to GitHub!")
            st.caption(
                "Streamlit Cloud will redeploy in ~60s."
            )
        else:
            st.error(f"Push failed: {push.stderr}")
            st.caption(
                "Push may fail on Streamlit Cloud "
                "(read-only fs). Use locally or via "
                "GitHub web editor for cloud deploys."
            )
