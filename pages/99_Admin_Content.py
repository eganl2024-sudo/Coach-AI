import streamlit as st
import sys
import os
import datetime
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
import config


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

# Handle schematic direct saving via data bridge
if "schematic_data_bridge" in st.session_state and st.session_state.schematic_data_bridge:
    payload_str = st.session_state.schematic_data_bridge
    st.session_state.schematic_data_bridge = ""
    try:
        import json
        import base64
        
        payload = json.loads(payload_str)
        target_drill_id = payload.get("drill_id")
        base64_data = payload.get("image_data")
        
        if target_drill_id and base64_data and base64_data.startswith("data:image/png;base64,"):
            img_bytes = base64.b64decode(base64_data.split(",")[1])
            
            # Save PNG directly to assets/diagrams/DRILL_ID.png
            diagram_dir = Path("assets/diagrams")
            diagram_dir.mkdir(parents=True, exist_ok=True)
            
            file_name = f"{target_drill_id}.png"
            target_path = diagram_dir / file_name
            
            with open(target_path, "wb") as f:
                f.write(img_bytes)
                
            # Update CSV
            matching_indices = df.index[df["drill_id"] == target_drill_id].tolist()
            if matching_indices:
                idx = matching_indices[0]
                df.at[idx, "diagram_path"] = f"assets/diagrams/{file_name}"
                df.at[idx, "diagram_url"] = (
                    "https://raw.githubusercontent.com/"
                    "eganl2024-sudo/MDP_APP/main/assets/diagrams/"
                    f"{file_name}"
                )
                df.to_csv(CSV_PATH, index=False)
                
                # Also save to demo CSV if it exists
                demo_csv = Path("data/production/users/demo/drill_library.csv")
                if demo_csv.exists():
                    df.to_csv(demo_csv, index=False)
                    
                st.session_state.admin_success_msg = f"✅ Schematic saved directly to {target_drill_id} on disk!"
                st.rerun()
            else:
                st.error(f"Error: Drill ID '{target_drill_id}' not found in library.")
    except Exception as e:
        st.error(f"Failed to save schematic: {str(e)}")


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
    <button style="background: #1d4ed8; color: #f0f9ff; border-color: #1e40af; font-weight: bold;" onclick="saveToDrill()">Save to Drill</button>
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

// ─── SHARED FULL-FIELD DRAW FUNCTION ────────────────────────────────────────
// Used by full, half, and attacking layouts.
// Draws the complete 105x68m field using the same coordinate system.
// Callers use ctx.save()/clip()/restore() to show only the desired portion.
function drawFullFieldLines() {
  const scX = 600 / 105;
  const scY = 360 / 68;
  const fx = (m) => 30 + m * scX;
  const fy = (m) => 20 + m * scY;
  const fw = (m) => m * scX;
  const fh = (m) => m * scY;

  ctx.strokeStyle = 'rgba(255,255,255,0.65)';
  ctx.lineWidth = 1.5;

  // Outer boundary
  ctx.strokeRect(30, 20, 600, 360);

  // Center line
  ctx.beginPath();
  ctx.moveTo(330, 20); ctx.lineTo(330, 380); ctx.stroke();

  // Center circle
  ctx.beginPath();
  ctx.arc(330, 200, fh(9.15), 0, Math.PI * 2);
  ctx.stroke();

  // Center spot
  ctx.fillStyle = 'rgba(255,255,255,0.65)';
  ctx.beginPath(); ctx.arc(330, 200, 3, 0, Math.PI * 2); ctx.fill();

  // LEFT penalty box
  ctx.strokeRect(30, fy((68 - 40.32) / 2), fw(16.5), fh(40.32));
  // LEFT 6-yard box
  ctx.strokeRect(30, fy((68 - 18.32) / 2), fw(5.5), fh(18.32));
  // LEFT goal
  ctx.strokeRect(30 - fw(2.44), fy((68 - 7.32) / 2), fw(2.44), fh(7.32));
  // LEFT penalty spot
  ctx.fillStyle = 'rgba(255,255,255,0.65)';
  ctx.beginPath(); ctx.arc(fx(11), fy(34), 3, 0, Math.PI * 2); ctx.fill();
  // LEFT penalty arc — elliptical
  {
    const arcCX = fx(11), arcCY = fy(34);
    const arcRX = fw(9.15), arcRY = fh(9.15);
    const boxRightX = 30 + fw(16.5);
    const cosA = Math.min(1, Math.max(-1, (boxRightX - arcCX) / arcRX));
    const arcA = Math.acos(cosA);
    ctx.save();
    ctx.translate(arcCX, arcCY);
    ctx.scale(1, arcRY / arcRX);
    ctx.beginPath(); ctx.arc(0, 0, arcRX, -arcA, arcA);
    ctx.restore(); ctx.stroke();
  }

  // RIGHT penalty box
  ctx.strokeRect(fx(88.5), fy((68 - 40.32) / 2), fw(16.5), fh(40.32));
  // RIGHT 6-yard box
  ctx.strokeRect(fx(99.5), fy((68 - 18.32) / 2), fw(5.5), fh(18.32));
  // RIGHT goal
  ctx.strokeRect(fx(105), fy((68 - 7.32) / 2), fw(2.44), fh(7.32));
  // RIGHT penalty spot
  ctx.fillStyle = 'rgba(255,255,255,0.65)';
  ctx.beginPath(); ctx.arc(fx(94), fy(34), 3, 0, Math.PI * 2); ctx.fill();
  // RIGHT penalty arc — elliptical
  {
    const arcCX = fx(94), arcCY = fy(34);
    const arcRX = fw(9.15), arcRY = fh(9.15);
    const boxLeftX = fx(88.5);
    const cosA = Math.min(1, Math.max(-1, (arcCX - boxLeftX) / arcRX));
    const arcA = Math.acos(cosA);
    ctx.save();
    ctx.translate(arcCX, arcCY);
    ctx.scale(1, arcRY / arcRX);
    ctx.beginPath(); ctx.arc(0, 0, arcRX, Math.PI - arcA, Math.PI + arcA);
    ctx.restore(); ctx.stroke();
  }
}

function drawFieldBackdrop() {
  // Green backdrop with stripes
  ctx.fillStyle = '#2d5a1b';
  ctx.fillRect(0, 0, 660, 400);
  const stripeW = 660 / 8;
  ctx.fillStyle = 'rgba(0,0,0,0.06)';
  for (let i = 0; i < 8; i++) {
    if (i % 2 === 1) ctx.fillRect(i * stripeW, 0, stripeW, 400);
  }

  if (activeLayout === 'full') {
    // Draw the complete field — no clipping needed
    drawFullFieldLines();

  } else if (activeLayout === 'half') {
    // Show left half of the full field (0m to 52.5m = x: 30 to 330)
    // Same coordinate system as full field, just clipped at the center line
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, 332, 400); // clip to left half + tiny overlap for boundary
    ctx.clip();
    drawFullFieldLines();
    ctx.restore();
    // Draw a clean right edge boundary over the clip
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(330, 20); ctx.lineTo(330, 380); ctx.stroke();

  } else if (activeLayout === 'attacking') {
    // Show left third of the full field (0m to 35m = x: 30 to 230)
    // Same coordinate system as full field, just clipped at the third line
    const scX = 600 / 105;
    const thirdX = 30 + 35 * scX; // x pixel at 35m mark = ~220px
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, thirdX + 2, 400); // clip to attacking third + tiny overlap
    ctx.clip();
    drawFullFieldLines();
    ctx.restore();
    // Draw a clean right edge boundary over the clip
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(thirdX, 20); ctx.lineTo(thirdX, 380); ctx.stroke();

  } else if (activeLayout === 'open') {
    ctx.strokeStyle = 'rgba(255,255,255,0.65)';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(30, 20, 600, 360);
    ctx.fillStyle = 'rgba(255,255,255,0.5)';
    ctx.beginPath(); ctx.arc(330, 200, 3, 0, Math.PI * 2); ctx.fill();

  } else if (activeLayout === 'grid') {
    const cols = 10, rows = 6;
    const cw = 600 / cols, ch = 360 / rows;
    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.lineWidth = 1;
    for (let i = 1; i < cols; i++) {
      ctx.beginPath(); ctx.moveTo(30 + i * cw, 20); ctx.lineTo(30 + i * cw, 380); ctx.stroke();
    }
    for (let j = 1; j < rows; j++) {
      ctx.beginPath(); ctx.moveTo(30, 20 + j * ch); ctx.lineTo(630, 20 + j * ch); ctx.stroke();
    }
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(330, 20); ctx.lineTo(330, 380); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(30, 200); ctx.lineTo(630, 200); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,255,255,0.9)';
    ctx.lineWidth = 3;
    ctx.strokeRect(30, 20, 600, 360);
    ctx.beginPath(); ctx.moveTo(630, 20); ctx.lineTo(630, 380); ctx.stroke();
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

function saveToDrill() {
  const prevSelected = selectedElement;
  selectedElement = null;
  draw();
  
  const dataURL = canvas.toDataURL('image/png');
  const drillId = document.getElementById('drill_id_label').textContent;
  
  const payload = JSON.stringify({
    drill_id: drillId,
    image_data: dataURL
  });
  
  const textarea = window.parent.document.querySelector('textarea[aria-label="schematic_data_bridge_textarea"]');
  if (textarea) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
    nativeInputValueSetter.call(textarea, payload);
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  } else {
    alert("Error: Streamlit data bridge not found. Make sure the page is fully loaded.");
  }
  
  selectedElement = prevSelected;
  draw();
}
</script>
</body>
</html>
"""

# Create tabs for cleaner layout
tab1, tab2, tab3 = st.tabs([
  "📋 Edit Drill Metadata",
  "🎨 Schematic Painter",
  "👁️ Drill Preview"
])

with tab1:
    # Metrics Dashboard
    total = len(df)
    filmed = len(df[df["video_status"].str.lower() == "filmed"])
    published = len(df[df["video_status"].str.lower() == "published"])
    not_filmed = total - filmed - published
    beta_ready_count = len(df[df["beta_ready"].str.lower() == "true"])

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Drills", total)
    with col_m2:
        st.metric("Filmed", filmed)
    with col_m3:
        st.metric("Beta Ready", beta_ready_count)
    with col_m4:
        st.metric("Not Filmed", not_filmed, delta=f"-{not_filmed} to go")

    if total > 0:
        pct = round((filmed + published) / total * 100)
    else:
        pct = 0
    st.progress(pct / 100, text=f"{pct}% of library has video")

    st.divider()

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
                    status_val = row.get("video_status", "not filmed").lower().strip()
                    status_list = ["not filmed", "filmed", "published"]
                    status_idx = status_list.index(status_val) if status_val in status_list else 0
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
                    df.to_csv(CSV_PATH, index=False)
                    demo_csv = Path("data/production/users/demo/drill_library.csv")
                    if demo_csv.exists():
                        df.to_csv(demo_csv, index=False)
                    st.session_state.admin_success_msg = f"✅ {drill_id} saved."
                    st.rerun()

with tab2:
    st.header("🎨 Schematic Painter")
    st.write("Draw soccer drill setups on top of tactical field backdrops and link them to the drill.")

    drill_names = [f"{row['drill_id']} — {row['drill_name']}"
                   for _, row in df.iterrows()]

    default_select_idx = 0
    if "newly_created_drill_id" in st.session_state:
        target_id = st.session_state.newly_created_drill_id
        matching_indices = df.index[df["drill_id"] == target_id].tolist()
        if matching_indices:
            default_select_idx = matching_indices[0]
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
                    new_row_data["skill_category"] = skill_cat_map.get(new_cat, "Technical")
                    for k, v in new_row_data.items():
                        new_row_data[k] = str(v) if v is not None else ""
                    new_df_row = pd.DataFrame([new_row_data])
                    new_df_row = new_df_row[df.columns]
                    df_updated = pd.concat([df, new_df_row], ignore_index=True)
                    df_updated.to_csv(CSV_PATH, index=False)
                    demo_csv = Path("data/production/users/demo/drill_library.csv")
                    if demo_csv.exists():
                        df_updated.to_csv(demo_csv, index=False)
                    st.session_state.newly_created_drill_id = clean_id
                    st.session_state.admin_success_msg = f"✅ Drill '{clean_id}' successfully created!"
                    st.rerun()

    existing_url = drill_row.get("diagram_url", "").strip()
    existing_path = drill_row.get("diagram_path", "").strip()
    local_file = config.get_diagram_file(existing_path) if existing_path else None
    
    if local_file and local_file.exists():
        st.image(str(local_file),
                 caption=f"Current schematic — {selected_drill_id} (Local)",
                 use_container_width=False, width=400)
    elif existing_url and "raw.githubusercontent" in existing_url:
        st.image(existing_url,
                 caption=f"Current schematic — {selected_drill_id} (GitHub)",
                 use_container_width=False, width=400)

    st.info(
        "🎨 Use the canvas below. Place players, cones, balls. "
        "Draw movement arrows. When done click **Save to Drill** "
        "to save it directly on disk and update the library, or **Export PNG** "
        "to download the file."
    )

    skill_category = drill_row.get("skill_category", "").lower().strip()
    drill_name_lower = drill_row.get("drill_name", "").lower()
    focus_tags = drill_row.get("focus_tags", "").lower()

    cat = skill_category
    if any(w in cat for w in ["finish", "shoot", "1v1 attack", "crossing"]):
        default_layout = "attacking"
    elif any(w in cat for w in ["pass", "receiv", "tactical", "defend", "1v1 def"]):
        default_layout = "half"
    elif any(w in cat for w in ["speed", "agility", "fitness", "strength", "warmup", "cool"]):
        default_layout = "open"
    elif any(w in cat for w in ["ball master", "dribbl", "move", "weak foot", "touch", "mental"]):
        default_layout = "open"
    elif "goalkeep" in cat:
        default_layout = "half"
    else:
        default_layout = "open"

    if any(kw in drill_name_lower or kw in focus_tags
           for kw in ["finish", "shoot", "cross", "1v1 attack", "goal"]):
        default_layout = "attacking"

    html_with_drill = SCHEMATIC_HTML.replace(
        '__DRILL_ID__', selected_drill_id
    ).replace(
        "setLayout('full')", f"setLayout('{default_layout}')"
    )
    
    # Hide the data bridge textarea completely from UI
    st.markdown(
        """
        <style>
        div[data-testid="stTextArea"]:has(textarea[aria-label="schematic_data_bridge_textarea"]) {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Render the bridge textarea
    st.text_area(
        "schematic_data_bridge_textarea",
        value="",
        key="schematic_data_bridge",
        label_visibility="collapsed",
    )
    
    st.components.v1.html(html_with_drill, height=560, scrolling=False)

    st.caption(
        "Clicking 'Save to Drill' directly updates the local library. "
        "Alternatively, paste a custom Raw GitHub URL below."
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
        if st.form_submit_button("💾 Save Schematic URL", type="primary"):
            idx = df.index[df["drill_id"] == selected_drill_id][0]
            df.at[idx, "diagram_url"] = pasted_url
            df.at[idx, "diagram_path"] = f"assets/diagrams/{selected_drill_id.lower()}.png"
            df.to_csv(CSV_PATH, index=False)
            demo_csv = Path("data/production/users/demo/drill_library.csv")
            if demo_csv.exists():
                df.to_csv(demo_csv, index=False)
            st.session_state.admin_success_msg = (
                f"✅ Schematic URL saved for {selected_drill_id}"
            )
            st.rerun()

with tab3:
    st.header("👁️ Drill Preview")
    st.write(
        "See exactly what a drill looks like to an athlete "
        "before publishing. Select any drill to preview the "
        "full card as it appears in the app."
    )

    preview_idx = st.selectbox(
        "Select drill to preview",
        range(len(df)),
        format_func=lambda i: (
            f"{df.iloc[i]['drill_id']} — "
            f"{df.iloc[i]['drill_name']}"
        ),
        key="preview_drill_select"
    )
    preview_row = df.iloc[preview_idx]

    st.divider()

    vid_url = preview_row.get("video_url", "").strip()
    diag_url = preview_row.get("diagram_url", "").strip()
    drill_name = preview_row.get("drill_name", "")
    category = preview_row.get("category", preview_row.get("skill_category", ""))
    difficulty = preview_row.get("difficulty", "").title()
    duration = preview_row.get("duration_minutes", "")
    p_min = preview_row.get("players_min", "")
    p_max = preview_row.get("players_max", "")
    description = preview_row.get("description", "")
    setup = preview_row.get("setup_data", preview_row.get("setup_instructions", ""))
    coaching = preview_row.get("coaching_points", preview_row.get("coaching_cues", ""))
    equipment = preview_row.get("equipment", "")
    tags_raw = preview_row.get("tags", "")
    presenter_id = preview_row.get("presenter_id", "")
    beta_ready = preview_row.get("beta_ready", "").lower() == "true"

    badge_col1, badge_col2, badge_col3 = st.columns(3)
    with badge_col1:
        if beta_ready:
            st.success("✅ Beta Ready — live in app")
        else:
            st.warning("⚠️ Not beta ready — hidden from players")
    with badge_col2:
        video_status = preview_row.get("video_status", "Not Filmed")
        if video_status.lower() in ["filmed", "published"]:
            st.success(f"🎬 Video: {video_status}")
        else:
            st.warning("📹 No video yet")
    diag_path = preview_row.get("diagram_path", "").strip()
    local_diag_file = config.get_diagram_file(diag_path) if diag_path else None
    with badge_col3:
        if (local_diag_file and local_diag_file.exists()) or (diag_url and "raw.githubusercontent" in diag_url):
            st.success("🗺️ Schematic linked")
        else:
            st.warning("🗺️ No schematic yet")

    st.subheader(drill_name)

    meta_cols = st.columns(4)
    with meta_cols[0]:
        st.metric("Category", category or "—")
    with meta_cols[1]:
        st.metric("Difficulty", difficulty or "—")
    with meta_cols[2]:
        st.metric("Duration", f"{duration} min" if duration else "—")
    with meta_cols[3]:
        st.metric("Players", f"{p_min}–{p_max}" if p_min and p_max else "—")

    st.divider()

    content_col1, content_col2 = st.columns([3, 2])

    with content_col1:
        st.subheader("📹 Drill Video")
        if vid_url:
            st.video(vid_url)
        else:
            st.info("No video linked yet. Add a YouTube URL in the Drill Editor tab.")

    with content_col2:
        st.subheader("🗺️ Setup Schematic")
        if local_diag_file and local_diag_file.exists():
            st.image(str(local_diag_file), use_container_width=True)
        elif diag_url and "raw.githubusercontent" in diag_url:
            st.image(diag_url, use_container_width=True)
        else:
            st.info("No schematic yet. Draw one in the Schematic Painter tab.")

    st.divider()

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        if description:
            st.subheader("📋 Description")
            st.write(description)
        if setup:
            st.subheader("⚙️ Setup")
            st.write(setup)

    with detail_col2:
        if coaching:
            st.subheader("💡 Coaching Points")
            st.write(coaching)
        if equipment:
            st.subheader("🧰 Equipment")
            st.write(equipment)

    if tags_raw:
        st.divider()
        st.subheader("🏷️ Tags")
        tags = [t.strip() for t in tags_raw.split("|") if t.strip()]
        st.markdown(" ".join([f"`{t}`" for t in tags]))

    if presenter_id:
        st.divider()
        st.caption(f"Presented by: {presenter_id}")

    st.divider()
    st.subheader("⚡ Quick Actions")
    qa_col1, qa_col2, qa_col3 = st.columns(3)

    with qa_col1:
        drill_id_preview = preview_row.get("drill_id", "")
        current_beta = preview_row.get("beta_ready", "").lower() == "true"
        new_beta_label = "🚫 Remove from Beta" if current_beta else "✅ Mark Beta Ready"
        if st.button(new_beta_label, use_container_width=True, key="preview_toggle_beta"):
            idx = df.index[df["drill_id"] == drill_id_preview][0]
            df.at[idx, "beta_ready"] = str(not current_beta)
            df.to_csv(CSV_PATH, index=False)
            st.session_state.admin_success_msg = f"✅ {drill_id_preview} beta status updated."
            st.rerun()

    with qa_col2:
        if st.button("✏️ Edit in Drill Editor", use_container_width=True, key="preview_go_edit"):
            st.info("Switch to the 📋 Edit Drill Metadata tab and find this drill.")

    with qa_col3:
        if st.button("🎨 Edit Schematic", use_container_width=True, key="preview_go_schematic"):
            st.session_state.newly_created_drill_id = drill_id_preview
            st.info("Switch to the 🎨 Schematic Painter tab — this drill will be pre-selected.")

# Git push section
st.divider()
st.subheader("🚀 Publish to GitHub")
st.caption(
    "Pushes updated drill_library.csv and generated schematics to GitHub. "
    "Streamlit Cloud redeploys in ~60 seconds."
)

if st.button("Push to GitHub", type="primary", key="git_push_btn"):
    import subprocess
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
            st.caption("Streamlit Cloud will redeploy in ~60s.")
        else:
            st.error(f"Push failed: {push.stderr}")
            st.caption(
                "Push may fail on Streamlit Cloud (read-only fs). "
                "Use locally or via GitHub web editor for cloud deploys."
            )
