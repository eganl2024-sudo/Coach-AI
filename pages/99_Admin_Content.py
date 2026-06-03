import streamlit as st
import sys
import os
import datetime
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
import config

st.set_page_config(page_title="Admin Content | Player AI", page_icon="🔐", layout="wide")

ADMIN_PASSWORD = os.environ.get("PLAYER_AI_ADMIN_PASSWORD", "AdminPlayerAI2026")

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

st.title("🛡️ Admin Content Editor")
st.write("Manage drill library video links, schematic diagrams, beta status, and sync changes with GitHub.")

# ── Handle pending schematic save (survives rerun via session state) ──────────
if st.session_state.get("_pending_schematic_save"):
    ps = st.session_state.pop("_pending_schematic_save")
    try:
        ddir = Path("assets/diagrams")
        ddir.mkdir(parents=True, exist_ok=True)
        fn = f"{ps['drill_id']}.png"
        fp = ddir / fn
        with open(fp, "wb") as f:
            f.write(ps["bytes"])
        raw_url = f"https://raw.githubusercontent.com/eganl2024-sudo/MDP_APP/main/assets/diagrams/{fn}"
        _df_save = pd.read_csv(Path("data/production/drill_library.csv"), dtype=str).fillna("")
        idx = _df_save.index[_df_save["drill_id"] == ps["drill_id"]][0]
        _df_save.at[idx, "diagram_url"] = raw_url
        _df_save.at[idx, "diagram_path"] = f"assets/diagrams/{fn}"
        _df_save.to_csv(Path("data/production/drill_library.csv"), index=False)
        dc = Path("data/production/users/demo/drill_library.csv")
        if dc.exists():
            _df_save.to_csv(dc, index=False)
        st.session_state.admin_success_msg = f"✅ Schematic saved for {ps['drill_id']}! Push to GitHub to make it live."
    except Exception as e:
        st.session_state.admin_success_msg = f"❌ Save failed: {e}"

if "admin_success_msg" in st.session_state:
    st.success(st.session_state.admin_success_msg)
    del st.session_state.admin_success_msg

CSV_PATH = Path("data/production/drill_library.csv")
df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

SCHEMATIC_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0;padding:8px;background-color:#0e1117;color:#fafafa;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    user-select:none;overflow:hidden; }
  .toolbar { display:flex;flex-wrap:wrap;align-items:center;gap:10px;
    margin-bottom:8px;background:#1a1c23;padding:6px 10px;
    border-radius:8px;border:1px solid #2e3344; }
  .toolbar-section { display:flex;align-items:center;gap:4px; }
  .section-title { font-size:10px;color:#888;margin-right:4px;font-weight:bold;
    text-transform:uppercase;letter-spacing:0.5px; }
  .toolbar button,.lbtn { padding:4px 9px;font-size:11px;border:0.5px solid #ccc;
    border-radius:6px;background:#1e1e1e;color:#ccc;cursor:pointer;outline:none;
    transition:all 0.1s ease; }
  .toolbar button:hover,.lbtn:hover { background:#2d2d2d;color:#fff; }
  .toolbar button.active,.lbtn.active { background:#1e3a8a;color:#93c5fd;border-color:#3b82f6; }
  #btn-delete { background:#2d1515;color:#f87171;border-color:#7f1d1d; }
  #btn-delete:hover { background:#3d1515;color:#fca5a5; }
  #btn-delete.has-selection { background:#7f1d1d;color:#fca5a5;border-color:#ef4444; }
  .color-dot { width:14px;height:14px;border-radius:50%;border:1px solid rgba(255,255,255,0.4);
    cursor:pointer;padding:0!important;outline:none;transition:transform 0.1s ease;margin:0 2px; }
  .color-dot:hover { transform:scale(1.2); }
  .color-dot.active { transform:scale(1.3);border:2px solid #93c5fd!important;box-shadow:0 0 4px #93c5fd; }
  #schematicCanvas { display:block;margin:0 auto;border:1px solid #2e3344;
    border-radius:8px;box-shadow:0 4px 10px rgba(0,0,0,0.4); }
  #sel-hint { font-size:10px;color:#888;margin-top:4px;text-align:center;min-height:14px; }
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
    <button class="color-dot active" data-color="#ffffff" style="background:#ffffff" onclick="setColor('#ffffff')"></button>
    <button class="color-dot" data-color="#4FC3F7" style="background:#4FC3F7" onclick="setColor('#4FC3F7')"></button>
    <button class="color-dot" data-color="#FF6B35" style="background:#FF6B35" onclick="setColor('#FF6B35')"></button>
    <button class="color-dot" data-color="#FFD54F" style="background:#FFD54F" onclick="setColor('#FFD54F')"></button>
    <button class="color-dot" data-color="#66BB6A" style="background:#66BB6A" onclick="setColor('#66BB6A')"></button>
    <button class="color-dot" data-color="#EF5350" style="background:#EF5350" onclick="setColor('#EF5350')"></button>
    <button class="color-dot" data-color="#CE93D8" style="background:#CE93D8" onclick="setColor('#CE93D8')"></button>
  </div>
  <div class="toolbar-section" style="margin-left:auto">
    <button id="btn-delete" onclick="deleteSelected()" title="Delete selected element (or press Delete key)">🗑 Delete</button>
    <button onclick="undo()">Undo</button>
    <button onclick="clearCanvas()">Clear</button>
    <button style="background:#0f766e;color:#ccfbf1;border-color:#0d9488" onclick="exportPNG()">Export PNG</button>
  </div>
</div>
<canvas id="schematicCanvas" width="660" height="400"></canvas>
<div id="sel-hint"></div>
<span id="drill_id_label" style="display:none">__DRILL_ID__</span>
<script>
const canvas=document.getElementById('schematicCanvas');
const ctx=canvas.getContext('2d');
const selHint=document.getElementById('sel-hint');
const delBtn=document.getElementById('btn-delete');
let elements=[],history=[],activeTool='select',activeColor='#ffffff',activeLayout='full';
let selectedElement=null,isDragging=false,dragOffsets={};
let arrowStartPoint=null,currentMousePos={x:0,y:0},zoneStartPoint=null,isDrawingZone=false;

function updateSelHint(){
  if(selectedElement){
    const type=selectedElement.type==='arrow'?selectedElement.arrowType+' arrow':selectedElement.type;
    selHint.textContent='Selected: '+type+' — click Delete button or press Delete key to remove';
    delBtn.classList.add('has-selection');
  } else {
    selHint.textContent='';
    delBtn.classList.remove('has-selection');
  }
}

function deleteSelected(){
  if(!selectedElement) return;
  saveHistory();
  elements=elements.filter(el=>el.id!==selectedElement.id);
  selectedElement=null;
  updateSelHint();
  draw();
}

function setLayout(layout){
  activeLayout=layout;
  document.querySelectorAll('.lbtn').forEach(b=>b.classList.toggle('active',b.id==='lbtn-'+layout));
  draw();
}
window.onload=()=>setLayout('full');

function saveHistory(){if(history.length>=40)history.shift();history.push(JSON.parse(JSON.stringify(elements)));}
function undo(){if(history.length>0){elements=history.pop();selectedElement=null;updateSelHint();draw();}}
function clearCanvas(){saveHistory();elements=[];selectedElement=null;updateSelHint();draw();}

function setTool(t){
  activeTool=t;
  document.querySelectorAll('.toolbar button').forEach(b=>{if(b.id&&b.id.startsWith('btn-')&&b.id!=='btn-delete')b.classList.toggle('active',b.id==='btn-'+t);});
  arrowStartPoint=null;zoneStartPoint=null;isDrawingZone=false;
  if(t!=='select'){selectedElement=null;updateSelHint();}
  draw();
}

function setColor(c){
  activeColor=c;
  document.querySelectorAll('.color-dot').forEach(d=>d.classList.toggle('active',d.getAttribute('data-color').toLowerCase()===c.toLowerCase()));
  if(selectedElement&&(selectedElement.type==='player'||selectedElement.type==='zone'||(selectedElement.type==='arrow'&&selectedElement.arrowType!=='shoot'))){
    saveHistory();selectedElement.color=c;draw();
  }
}

function drawFullFieldLines(){
  const scX=600/105,scY=360/68;
  const fx=m=>30+m*scX,fy=m=>20+m*scY,fw=m=>m*scX,fh=m=>m*scY;
  ctx.strokeStyle='rgba(255,255,255,0.65)';ctx.lineWidth=1.5;
  ctx.strokeRect(30,20,600,360);
  ctx.beginPath();ctx.moveTo(330,20);ctx.lineTo(330,380);ctx.stroke();
  ctx.beginPath();ctx.arc(330,200,fh(9.15),0,Math.PI*2);ctx.stroke();
  ctx.fillStyle='rgba(255,255,255,0.65)';ctx.beginPath();ctx.arc(330,200,3,0,Math.PI*2);ctx.fill();
  ctx.strokeRect(30,fy((68-40.32)/2),fw(16.5),fh(40.32));
  ctx.strokeRect(30,fy((68-18.32)/2),fw(5.5),fh(18.32));
  ctx.strokeRect(30-fw(2.44),fy((68-7.32)/2),fw(2.44),fh(7.32));
  ctx.fillStyle='rgba(255,255,255,0.65)';ctx.beginPath();ctx.arc(fx(11),fy(34),3,0,Math.PI*2);ctx.fill();
  {const ax=fx(11),ay=fy(34),rx=fw(9.15),ry=fh(9.15),bx=30+fw(16.5);
   const ca=Math.min(1,Math.max(-1,(bx-ax)/rx)),a=Math.acos(ca);
   ctx.save();ctx.translate(ax,ay);ctx.scale(1,ry/rx);ctx.beginPath();ctx.arc(0,0,rx,-a,a);ctx.restore();ctx.stroke();}
  ctx.strokeRect(fx(88.5),fy((68-40.32)/2),fw(16.5),fh(40.32));
  ctx.strokeRect(fx(99.5),fy((68-18.32)/2),fw(5.5),fh(18.32));
  ctx.strokeRect(fx(105),fy((68-7.32)/2),fw(2.44),fh(7.32));
  ctx.fillStyle='rgba(255,255,255,0.65)';ctx.beginPath();ctx.arc(fx(94),fy(34),3,0,Math.PI*2);ctx.fill();
  {const ax=fx(94),ay=fy(34),rx=fw(9.15),ry=fh(9.15),bx=fx(88.5);
   const ca=Math.min(1,Math.max(-1,(ax-bx)/rx)),a=Math.acos(ca);
   ctx.save();ctx.translate(ax,ay);ctx.scale(1,ry/rx);ctx.beginPath();ctx.arc(0,0,rx,Math.PI-a,Math.PI+a);ctx.restore();ctx.stroke();}
}

function drawFieldBackdrop(){
  ctx.fillStyle='#2d5a1b';ctx.fillRect(0,0,660,400);
  const sw=660/8;ctx.fillStyle='rgba(0,0,0,0.06)';
  for(let i=0;i<8;i++)if(i%2===1)ctx.fillRect(i*sw,0,sw,400);
  if(activeLayout==='full'){drawFullFieldLines();}
  else if(activeLayout==='half'){
    ctx.save();ctx.beginPath();ctx.rect(0,0,332,400);ctx.clip();drawFullFieldLines();ctx.restore();
    ctx.strokeStyle='rgba(255,255,255,0.65)';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(330,20);ctx.lineTo(330,380);ctx.stroke();
  }else if(activeLayout==='attacking'){
    const thirdX=30+35*(600/105);
    ctx.save();ctx.beginPath();ctx.rect(0,0,thirdX+2,400);ctx.clip();drawFullFieldLines();ctx.restore();
    ctx.strokeStyle='rgba(255,255,255,0.65)';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(thirdX,20);ctx.lineTo(thirdX,380);ctx.stroke();
  }else if(activeLayout==='open'){
    ctx.strokeStyle='rgba(255,255,255,0.65)';ctx.lineWidth=1.5;ctx.strokeRect(30,20,600,360);
    ctx.fillStyle='rgba(255,255,255,0.5)';ctx.beginPath();ctx.arc(330,200,3,0,Math.PI*2);ctx.fill();
  }else if(activeLayout==='grid'){
    const cols=10,rows=6,cw=600/cols,ch=360/rows;
    ctx.strokeStyle='rgba(255,255,255,0.2)';ctx.lineWidth=1;
    for(let i=1;i<cols;i++){ctx.beginPath();ctx.moveTo(30+i*cw,20);ctx.lineTo(30+i*cw,380);ctx.stroke();}
    for(let j=1;j<rows;j++){ctx.beginPath();ctx.moveTo(30,20+j*ch);ctx.lineTo(630,20+j*ch);ctx.stroke();}
    ctx.strokeStyle='rgba(255,255,255,0.4)';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(330,20);ctx.lineTo(330,380);ctx.stroke();
    ctx.beginPath();ctx.moveTo(30,200);ctx.lineTo(630,200);ctx.stroke();
    ctx.strokeStyle='rgba(255,255,255,0.9)';ctx.lineWidth=3;
    ctx.strokeRect(30,20,600,360);
    ctx.beginPath();ctx.moveTo(630,20);ctx.lineTo(630,380);ctx.stroke();
    ctx.strokeStyle='rgba(255,255,255,0.65)';ctx.lineWidth=1.5;
  }
}

function drawArrowhead(x,y,angle,color,size){
  ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x,y);
  ctx.lineTo(x-size*Math.cos(angle-Math.PI/6),y-size*Math.sin(angle-Math.PI/6));
  ctx.lineTo(x-size*Math.cos(angle+Math.PI/6),y-size*Math.sin(angle+Math.PI/6));
  ctx.closePath();ctx.fill();
}

function drawElement(el){
  const isSel=selectedElement&&selectedElement.id===el.id;
  if(el.type==='arrow'&&el.playerId){
    const p=elements.find(e=>e.type==='player'&&e.id===el.playerId);
    if(p){el.x1=p.x;el.y1=p.y;}
  }
  if(el.type==='player'){
    ctx.fillStyle=el.color;ctx.beginPath();ctx.arc(el.x,el.y,11,0,2*Math.PI);ctx.fill();
    ctx.strokeStyle='rgba(0,0,0,0.2)';ctx.lineWidth=1;ctx.stroke();
    ctx.fillStyle='#fff';ctx.font='bold 11px Arial';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(el.number,el.x,el.y);
    if(isSel){ctx.strokeStyle='#FFD54F';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.beginPath();ctx.arc(el.x,el.y,16,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);}
  }else if(el.type==='cone'){
    ctx.fillStyle='rgba(0,0,0,0.2)';ctx.beginPath();ctx.ellipse(el.x,el.y+8,10,3,0,0,2*Math.PI);ctx.fill();
    ctx.fillStyle='#FF6B35';ctx.beginPath();ctx.moveTo(el.x,el.y-11);ctx.lineTo(el.x-9,el.y+8);ctx.lineTo(el.x+9,el.y+8);ctx.closePath();ctx.fill();
    ctx.strokeStyle='rgba(0,0,0,0.3)';ctx.lineWidth=1;ctx.stroke();
    if(isSel){ctx.strokeStyle='#FFD54F';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.beginPath();ctx.arc(el.x,el.y,16,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);}
  }else if(el.type==='ball'){
    ctx.fillStyle='#fff';ctx.strokeStyle='#000';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(el.x,el.y,7,0,2*Math.PI);ctx.fill();ctx.stroke();
    ctx.fillStyle='#000';
    for(let i=0;i<5;i++){const a=(i*2*Math.PI/5)-Math.PI/2;ctx.beginPath();ctx.arc(el.x+2.5*Math.cos(a),el.y+2.5*Math.sin(a),1.8,0,2*Math.PI);ctx.fill();}
    if(isSel){ctx.strokeStyle='#FFD54F';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.beginPath();ctx.arc(el.x,el.y,12,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);}
  }else if(el.type==='arrow'){
    const c=el.color;
    if(el.arrowType==='dribble'){
      const dx=el.x2-el.x1,dy=el.y2-el.y1,len=Math.sqrt(dx*dx+dy*dy)||1;
      const mx=(el.x1+el.x2)/2,my=(el.y1+el.y2)/2;
      const nx=-dy/len,ny=dx/len;
      const cx=mx+nx*(len*0.12),cy=my+ny*(len*0.12);
      ctx.strokeStyle=c;ctx.lineWidth=2;ctx.setLineDash([]);
      let prev={x:el.x1,y:el.y1},pts=[],totalD=0;
      for(let i=0;i<=80;i++){const t=i/80,mt=1-t;
        const bx=mt*mt*el.x1+2*mt*t*cx+t*t*el.x2,by=mt*mt*el.y1+2*mt*t*cy+t*t*el.y2;
        if(i>0)totalD+=Math.hypot(bx-prev.x,by-prev.y);
        const ddx=2*mt*(cx-el.x1)+2*t*(el.x2-cx),ddy=2*mt*(cy-el.y1)+2*t*(el.y2-cy);
        const dl=Math.hypot(ddx,ddy)||1;
        pts.push({bx,by,nx:-ddy/dl,ny:ddx/dl,d:totalD});prev={x:bx,y:by};}
      ctx.beginPath();ctx.moveTo(el.x1,el.y1);
      pts.forEach(p=>{const w=5*Math.sin(p.d/12*Math.PI*2);ctx.lineTo(p.bx+p.nx*w,p.by+p.ny*w);});
      ctx.stroke();
      drawArrowhead(el.x2,el.y2,Math.atan2(el.y2-cy,el.x2-cx),c,10);
    }else{
      ctx.strokeStyle=el.arrowType==='shoot'?'#EF5350':c;
      ctx.lineWidth=el.arrowType==='shoot'?3.5:2;
      ctx.setLineDash(el.arrowType==='pass'?[8,6]:el.arrowType==='run'?[3,5]:[]);
      ctx.beginPath();ctx.moveTo(el.x1,el.y1);ctx.lineTo(el.x2,el.y2);ctx.stroke();ctx.setLineDash([]);
      drawArrowhead(el.x2,el.y2,Math.atan2(el.y2-el.y1,el.x2-el.x1),el.arrowType==='shoot'?'#EF5350':c,el.arrowType==='shoot'?12:10);
    }
    if(isSel){ctx.strokeStyle='#FFD54F';ctx.lineWidth=2;ctx.setLineDash([3,3]);ctx.beginPath();ctx.arc(el.x1,el.y1,6,0,2*Math.PI);ctx.stroke();ctx.beginPath();ctx.arc(el.x2,el.y2,6,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);}
  }else if(el.type==='zone'){
    const r=parseInt(el.color.slice(1,3),16),g=parseInt(el.color.slice(3,5),16),b=parseInt(el.color.slice(5,7),16);
    ctx.fillStyle=`rgba(${r},${g},${b},0.12)`;ctx.strokeStyle=`rgba(${r},${g},${b},0.5)`;
    ctx.lineWidth=1.5;ctx.setLineDash([6,4]);
    ctx.fillRect(el.x,el.y,el.w,el.h);ctx.strokeRect(el.x,el.y,el.w,el.h);ctx.setLineDash([]);
    if(isSel){ctx.strokeStyle='#FFD54F';ctx.lineWidth=2;ctx.setLineDash([3,3]);ctx.strokeRect(el.x-2,el.y-2,el.w+4,el.h+4);ctx.setLineDash([]);}
  }
}

function draw(){
  ctx.clearRect(0,0,660,400);drawFieldBackdrop();
  elements.forEach(el=>drawElement(el));
  if(arrowStartPoint){
    ctx.fillStyle='#FFD54F';ctx.beginPath();ctx.arc(arrowStartPoint.x,arrowStartPoint.y,4,0,2*Math.PI);ctx.fill();
    ctx.strokeStyle=activeColor;ctx.lineWidth=activeTool==='shoot'?3.5:2;
    ctx.setLineDash(activeTool==='pass'?[8,6]:activeTool==='run'?[3,5]:[]);
    ctx.beginPath();ctx.moveTo(arrowStartPoint.x,arrowStartPoint.y);ctx.lineTo(currentMousePos.x,currentMousePos.y);ctx.stroke();ctx.setLineDash([]);
  }else if(activeTool==='zone'&&isDrawingZone&&zoneStartPoint){
    const x=Math.min(zoneStartPoint.x,currentMousePos.x),y=Math.min(zoneStartPoint.y,currentMousePos.y);
    const w=Math.abs(zoneStartPoint.x-currentMousePos.x),h=Math.abs(zoneStartPoint.y-currentMousePos.y);
    ctx.fillStyle=activeColor;ctx.strokeStyle=activeColor;ctx.lineWidth=1.5;ctx.setLineDash([6,4]);
    ctx.globalAlpha=0.12;ctx.fillRect(x,y,w,h);ctx.globalAlpha=0.5;ctx.strokeRect(x,y,w,h);
    ctx.globalAlpha=1;ctx.setLineDash([]);
  }
}

function nearestPlayer(x,y,d){let b=null,bd=d;elements.forEach(e=>{if(e.type==='player'){const dd=Math.hypot(e.x-x,e.y-y);if(dd<bd){bd=dd;b=e;}}});return b;}
function getAt(x,y){for(let i=elements.length-1;i>=0;i--){const el=elements[i];
  if(['player','cone'].includes(el.type)&&Math.hypot(el.x-x,el.y-y)<=15)return el;
  if(el.type==='ball'&&Math.hypot(el.x-x,el.y-y)<=11)return el;
  if(el.type==='zone'&&x>=el.x&&x<=el.x+el.w&&y>=el.y&&y<=el.y+el.h)return el;
  if(el.type==='arrow'){const dx=el.x2-el.x1,dy=el.y2-el.y1,l2=dx*dx+dy*dy;
    if(l2===0)continue;const t=Math.max(0,Math.min(1,((x-el.x1)*dx+(y-el.y1)*dy)/l2));
    if(Math.hypot(el.x1+t*dx-x,el.y1+t*dy-y)<=12)return el;}}return null;}

canvas.addEventListener('mousedown',e=>{
  const r=canvas.getBoundingClientRect(),cx=e.clientX-r.left,cy=e.clientY-r.top;
  if(activeTool==='select'){const el=getAt(cx,cy);if(el){saveHistory();selectedElement=el;isDragging=true;
    if(el.type==='arrow')dragOffsets={x1:cx-el.x1,y1:cy-el.y1,x2:cx-el.x2,y2:cy-el.y2};
    else dragOffsets={x:cx-el.x,y:cy-el.y};}else selectedElement=null;updateSelHint();draw();
  }else if(activeTool==='player'){saveHistory();let mx=0;elements.forEach(el=>{if(el.type==='player'&&el.number>mx)mx=el.number;});
    elements.push({type:'player',id:'p'+(mx+1)+'_'+Date.now(),x:cx,y:cy,number:mx+1,color:activeColor});draw();
  }else if(activeTool==='cone'){saveHistory();elements.push({type:'cone',id:'c'+Date.now(),x:cx,y:cy});draw();
  }else if(activeTool==='ball'){saveHistory();elements.push({type:'ball',id:'b'+Date.now(),x:cx,y:cy});draw();
  }else if(['dribble','pass','shoot','run'].includes(activeTool)){
    if(!arrowStartPoint){const sn=nearestPlayer(cx,cy,40);
      arrowStartPoint=sn?{x:sn.x,y:sn.y,playerId:sn.id}:{x:cx,y:cy,playerId:null};
      currentMousePos={x:cx,y:cy};draw();
    }else{if(Math.hypot(cx-arrowStartPoint.x,cy-arrowStartPoint.y)>5){
      saveHistory();elements.push({type:'arrow',arrowType:activeTool,id:'a'+Date.now(),
        x1:arrowStartPoint.x,y1:arrowStartPoint.y,x2:cx,y2:cy,
        color:activeTool==='shoot'?'#EF5350':activeColor,playerId:arrowStartPoint.playerId});}
      arrowStartPoint=null;draw();}
  }else if(activeTool==='zone'){zoneStartPoint={x:cx,y:cy};isDrawingZone=true;currentMousePos={x:cx,y:cy};}
});

canvas.addEventListener('mousemove',e=>{
  const r=canvas.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
  currentMousePos={x:mx,y:my};
  if(activeTool==='select'&&isDragging&&selectedElement){
    const el=selectedElement;
    if(el.type==='arrow'){el.x1=mx-dragOffsets.x1;el.y1=my-dragOffsets.y1;el.x2=mx-dragOffsets.x2;el.y2=my-dragOffsets.y2;el.playerId=null;}
    else{el.x=mx-dragOffsets.x;el.y=my-dragOffsets.y;}
    draw();
  }else if((activeTool==='zone'&&isDrawingZone)||arrowStartPoint)draw();
});

canvas.addEventListener('mouseup',e=>{
  if(activeTool==='select'&&isDragging){isDragging=false;}
  else if(activeTool==='zone'&&isDrawingZone&&zoneStartPoint){
    const r=canvas.getBoundingClientRect(),rx=e.clientX-r.left,ry=e.clientY-r.top;
    const x=Math.min(zoneStartPoint.x,rx),y=Math.min(zoneStartPoint.y,ry);
    const w=Math.abs(zoneStartPoint.x-rx),h=Math.abs(zoneStartPoint.y-ry);
    if(w>5&&h>5){saveHistory();elements.push({type:'zone',id:'z'+Date.now(),x,y,w,h,color:activeColor});}
    isDrawingZone=false;zoneStartPoint=null;draw();}
});

window.addEventListener('keydown',e=>{
  if((e.key==='Delete'||e.key==='Backspace')&&selectedElement){
    deleteSelected();}
});

function exportPNG(){
  const prev=selectedElement;selectedElement=null;draw();
  const url=canvas.toDataURL('image/png');
  const a=document.createElement('a');
  a.download=document.getElementById('drill_id_label').textContent.trim()+'.png';
  a.href=url;document.body.appendChild(a);a.click();document.body.removeChild(a);
  selectedElement=prev;updateSelHint();draw();
}
</script>
</body>
</html>
"""

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Edit Drill Metadata",
    "🎨 Schematic Painter",
    "👁️ Drill Preview",
    "📹 Video Queue",
])

with tab1:
    total=len(df)
    filmed=len(df[df["video_status"].str.lower()=="filmed"])
    published=len(df[df["video_status"].str.lower()=="published"])
    not_filmed=total-filmed-published
    beta_ready_count=len(df[df["beta_ready"].str.lower()=="true"])
    col_m1,col_m2,col_m3,col_m4=st.columns(4)
    with col_m1: st.metric("Total Drills",total)
    with col_m2: st.metric("Filmed",filmed)
    with col_m3: st.metric("Beta Ready",beta_ready_count)
    with col_m4: st.metric("Not Filmed",not_filmed,delta=f"-{not_filmed} to go")
    pct=round((filmed+published)/total*100) if total>0 else 0
    st.progress(pct/100,text=f"{pct}% of library has video")
    st.divider()
    st.subheader("🔍 Filters")
    fc1,fc2=st.columns(2)
    with fc1:
        pres_opts=["All"]+sorted(df["presenter_id"].unique().tolist())
        sel_pres=st.selectbox("Filter by presenter",pres_opts,key="metadata_presenter_filter")
    with fc2:
        sel_stat=st.selectbox("Filter by video status",["All","Not Filmed","Filmed","Published"],key="metadata_status_filter")
    fdf=df.copy()
    if sel_pres!="All": fdf=fdf[fdf["presenter_id"]==sel_pres]
    if sel_stat!="All": fdf=fdf[fdf["video_status"].str.lower()==sel_stat.lower()]
    st.subheader(f"📋 Drills ({len(fdf)})")
    for _,row in fdf.iterrows():
        did=row["drill_id"]
        is_f=row.get("video_status","").lower() in ["filmed","published"]
        lbl=f"{'✅' if is_f else '📹'} {did} — {row['drill_name']} [{row.get('video_status','Not Filmed')}]"
        with st.expander(lbl,expanded=not is_f):
            with st.form(key=f"form_{did}"):
                cur=row.get("video_url","").strip()
                if cur: st.video(cur)
                else: st.info("No video linked yet.")
                c1,c2=st.columns(2)
                with c1:
                    nu=st.text_input("YouTube URL",value=cur,key=f"url_{did}")
                    sv=row.get("video_status","not filmed").lower().strip()
                    sl=["not filmed","filmed","published"]
                    ns=st.selectbox("Video status",["Not Filmed","Filmed","Published"],index=sl.index(sv) if sv in sl else 0,key=f"status_{did}")
                    nb=st.checkbox("Beta Ready",value=row.get("beta_ready","").lower()=="true",key=f"beta_{did}")
                with c2:
                    nn=st.text_area("Filming notes",value=row.get("filming_notes",""),height=80,key=f"notes_{did}")
                    nd=st.text_input("Schematic URL (diagram_url)",value=row.get("diagram_url",""),key=f"diag_{did}")
                    st.caption("Use the Schematic Painter tab to draw and export a diagram for this drill.")
                if st.form_submit_button("💾 Save Changes",type="primary",use_container_width=True):
                    idx=df.index[df["drill_id"]==did][0]
                    df.at[idx,"video_url"]=nu;df.at[idx,"video_status"]=ns
                    df.at[idx,"beta_ready"]=str(nb);df.at[idx,"filming_notes"]=nn
                    df.at[idx,"diagram_url"]=nd
                    df.at[idx,"filming_date"]=datetime.date.today().isoformat() if ns=="Filmed" else row.get("filming_date","")
                    df.to_csv(CSV_PATH,index=False)
                    dc=Path("data/production/users/demo/drill_library.csv")
                    if dc.exists(): df.to_csv(dc,index=False)
                    st.session_state.admin_success_msg=f"✅ {did} saved."
                    st.rerun()

with tab2:
    st.header("🎨 Schematic Painter")
    dnames=[f"{r['drill_id']} — {r['drill_name']}" for _,r in df.iterrows()]
    def_idx=0
    if "newly_created_drill_id" in st.session_state:
        tid=st.session_state.newly_created_drill_id
        mi=df.index[df["drill_id"]==tid].tolist()
        if mi: def_idx=mi[0]
        del st.session_state.newly_created_drill_id
    sel_idx=st.selectbox("Select drill to build schematic for",range(len(dnames)),index=def_idx,format_func=lambda i:dnames[i],key="canvas_drill_select")
    sel_did=df.iloc[sel_idx]["drill_id"]
    drow=df.iloc[sel_idx]

    with st.expander("➕ Create a new drill instead",expanded=False):
        with st.form("create_new_drill_form"):
            c1,c2=st.columns(2)
            with c1:
                ni=st.text_input("Drill ID (unique identifier)",placeholder="e.g. TECH_010")
                nn=st.text_input("Drill Name",placeholder="e.g. 1v1 Goal Attack")
                nc=st.selectbox("Category",["Ball Mastery","First Touch","Dribbling & Moves","Passing & Receiving","Finishing","Shooting Technique","1v1 Attacking","1v1 Defending","Weak Foot","Aerial & Headers","Speed & Agility","Strength & Fitness","Goalkeeping","Mental & Decision Making","Warmup & Cool Down"])
                nd=st.selectbox("Difficulty",["beginner","intermediate","advanced"])
                nit=st.selectbox("Intensity",["low","medium","high"])
                ndu=st.number_input("Duration (minutes)",min_value=1,max_value=120,value=10)
                npm=st.number_input("Min Players",min_value=1,max_value=50,value=2)
                npx=st.number_input("Max Players",min_value=1,max_value=50,value=4)
            with c2:
                nvu=st.text_input("YouTube URL (optional)",placeholder="https://www.youtube.com/watch?v=...")
                ndesc=st.text_area("Description")
                nset=st.text_area("Setup Instructions")
                nel=st.multiselect("Equipment Required",["Ball","Cones","Goal","Rebounder","Agility Ladder","Poles/Sticks","Bibs","Mannequin","Speed Rings","Mini Goals","Resistance Band","None"],default=["Ball","Cones"])
                ncp=st.text_area("Coaching Points")
                nmis=st.text_area("Common Mistakes")
                ntl=st.multiselect("Tags",["1v1","dribbling","passing","finishing","first touch","weak foot","shooting","defending","heading","crossing","speed","agility","strength","goalkeeping","ball mastery","transition","pressing","movement","warmup","solo"],default=[])
            if st.form_submit_button("➕ Create Drill",type="primary",use_container_width=True):
                cid=ni.strip().upper();cnm=nn.strip()
                if not cid: st.error("❌ Drill ID cannot be empty.")
                elif not cnm: st.error("❌ Drill Name cannot be empty.")
                elif cid in df["drill_id"].values: st.error(f"❌ Drill ID '{cid}' already exists.")
                else:
                    from data_loader import DRILL_DEFAULTS
                    nr=DRILL_DEFAULTS.copy()
                    scm={"Ball Mastery":"Technical","First Touch":"Technical","Dribbling & Moves":"Dribbling","Passing & Receiving":"Passing","Finishing":"Finishing","Shooting Technique":"Finishing","1v1 Attacking":"Dribbling","1v1 Defending":"Defending","Weak Foot":"Technical","Aerial & Headers":"Technical","Speed & Agility":"Speed","Strength & Fitness":"Fitness","Goalkeeping":"Goalkeeping","Mental & Decision Making":"Technical","Warmup & Cool Down":"Fitness"}
                    nr.update({"drill_id":cid,"drill_name":cnm,"category":nc,"difficulty":nd,"intensity":nit,"duration_minutes":str(ndu),"players_min":str(npm),"players_max":str(npx),"description":ndesc,"setup_data":nset,"equipment":", ".join(nel),"coaching_points":ncp,"common_mistakes":nmis,"tags":"|".join(ntl),"video_url":nvu,"video_status":"Filmed" if nvu.strip() else "Not Filmed","skill_category":scm.get(nc,"Technical")})
                    nr={k:str(v) if v is not None else "" for k,v in nr.items()}
                    ndfr=pd.DataFrame([nr])[df.columns]
                    dfu=pd.concat([df,ndfr],ignore_index=True)
                    dfu.to_csv(CSV_PATH,index=False)
                    dc=Path("data/production/users/demo/drill_library.csv")
                    if dc.exists(): dfu.to_csv(dc,index=False)
                    st.session_state.newly_created_drill_id=cid
                    st.session_state.admin_success_msg=f"✅ Drill '{cid}' created!"
                    st.rerun()

    ex_url=drow.get("diagram_url","").strip()
    ex_path=drow.get("diagram_path","").strip()
    lf=config.get_diagram_file(ex_path) if ex_path else None
    if lf and lf.exists(): st.image(str(lf),caption=f"Current schematic — {sel_did} (local)",width=400)
    elif ex_url and "raw.githubusercontent" in ex_url: st.image(ex_url,caption=f"Current schematic — {sel_did} (GitHub)",width=400)

    scat=drow.get("skill_category","").lower()
    dnl=drow.get("drill_name","").lower()
    ftag=drow.get("focus_tags","").lower()
    if any(w in scat for w in ["finish","shoot","1v1 attack","crossing"]): dlayout="attacking"
    elif any(w in scat for w in ["pass","receiv","tactical","defend","1v1 def"]): dlayout="half"
    elif "goalkeep" in scat: dlayout="half"
    else: dlayout="open"
    if any(kw in dnl or kw in ftag for kw in ["finish","shoot","cross","1v1 attack","goal"]): dlayout="attacking"

    st.info(f"🎨 Draw the schematic below. Click **Export PNG** when done — the file saves as `{sel_did}.png`. Then upload it below to save it directly to this drill.")

    hwd=SCHEMATIC_HTML.replace('__DRILL_ID__',sel_did).replace("setLayout('full')",f"setLayout('{dlayout}')")
    st.components.v1.html(hwd,height=560,scrolling=False)

    st.divider()
    st.subheader("💾 Save Schematic to Drill")
    st.caption(f"After clicking Export PNG above, upload the downloaded `{sel_did}.png` file here.")

    uploaded=st.file_uploader(
        f"Upload schematic PNG for {sel_did}",
        type=["png"],
        key=f"upload_{sel_did}",
        help="Click Export PNG above first, then upload the downloaded file here."
    )

    if uploaded is not None:
        st.session_state["_uploaded_png_bytes"] = uploaded.read()
        st.session_state["_uploaded_png_drill_id"] = sel_did

    save_ready = (
        st.session_state.get("_uploaded_png_bytes") is not None
        and st.session_state.get("_uploaded_png_drill_id") == sel_did
    )

    if st.button(
        "💾 Save to Drill",
        type="primary",
        use_container_width=False,
        disabled=not save_ready,
        key="save_schematic_btn"
    ):
        st.session_state["_pending_schematic_save"] = {
            "drill_id": st.session_state["_uploaded_png_drill_id"],
            "bytes": st.session_state["_uploaded_png_bytes"],
        }
        del st.session_state["_uploaded_png_bytes"]
        del st.session_state["_uploaded_png_drill_id"]
        st.rerun()

with tab3:
    st.header("👁️ Drill Preview")
    prev_idx=st.selectbox("Select drill to preview",range(len(df)),format_func=lambda i:f"{df.iloc[i]['drill_id']} — {df.iloc[i]['drill_name']}",key="preview_drill_select")
    pr=df.iloc[prev_idx]
    st.divider()
    vid=pr.get("video_url","").strip()
    durl=pr.get("diagram_url","").strip()
    dpath=pr.get("diagram_path","").strip()
    ldf=config.get_diagram_file(dpath) if dpath else None
    bc1,bc2,bc3=st.columns(3)
    beta=pr.get("beta_ready","").lower()=="true"
    with bc1:
        if beta: st.success("✅ Beta Ready — live in app")
        else: st.warning("⚠️ Not beta ready — hidden from players")
    with bc2:
        vs=pr.get("video_status","Not Filmed")
        if vs.lower() in ["filmed","published"]: st.success(f"🎬 Video: {vs}")
        else: st.warning("📹 No video yet")
    with bc3:
        if (ldf and ldf.exists()) or (durl and "raw.githubusercontent" in durl): st.success("🗺️ Schematic linked")
        else: st.warning("🗺️ No schematic yet")
    st.subheader(pr.get("drill_name",""))
    mc=st.columns(4)
    with mc[0]: st.metric("Category",pr.get("category",pr.get("skill_category","")) or "—")
    with mc[1]: st.metric("Difficulty",(pr.get("difficulty","") or "").title() or "—")
    with mc[2]: du=pr.get("duration_minutes","");st.metric("Duration",f"{du} min" if du else "—")
    with mc[3]: pm,px=pr.get("players_min",""),pr.get("players_max","");st.metric("Players",f"{pm}–{px}" if pm and px else "—")
    st.divider()
    vc1,vc2=st.columns([3,2])
    with vc1:
        st.subheader("📹 Drill Video")
        if vid: st.video(vid)
        else: st.info("No video linked yet. Add a YouTube URL in the Drill Editor tab.")
    with vc2:
        st.subheader("🗺️ Setup Schematic")
        if ldf and ldf.exists(): st.image(str(ldf),use_container_width=True)
        elif durl and "raw.githubusercontent" in durl: st.image(durl,use_container_width=True)
        else: st.info("No schematic yet. Draw one in the Schematic Painter tab.")
    st.divider()
    dc1,dc2=st.columns(2)
    with dc1:
        desc=pr.get("description","");setup=pr.get("setup_data",pr.get("setup_instructions",""))
        if desc: st.subheader("📋 Description");st.write(desc)
        if setup: st.subheader("⚙️ Setup");st.write(setup)
    with dc2:
        coach=pr.get("coaching_points",pr.get("coaching_cues",""));equip=pr.get("equipment","")
        if coach: st.subheader("💡 Coaching Points");st.write(coach)
        if equip: st.subheader("🧰 Equipment");st.write(equip)
    tr=pr.get("tags","")
    if tr:
        st.divider();st.subheader("🏷️ Tags")
        st.markdown(" ".join([f"`{t.strip()}`" for t in tr.split("|") if t.strip()]))
    pid=pr.get("presenter_id","")
    if pid: st.divider();st.caption(f"Presented by: {pid}")
    st.divider();st.subheader("⚡ Quick Actions")
    qa1,qa2,qa3=st.columns(3)
    with qa1:
        dpid=pr.get("drill_id","");cbeta=pr.get("beta_ready","").lower()=="true"
        if st.button("🚫 Remove from Beta" if cbeta else "✅ Mark Beta Ready",use_container_width=True,key="preview_toggle_beta"):
            idx=df.index[df["drill_id"]==dpid][0];df.at[idx,"beta_ready"]=str(not cbeta)
            df.to_csv(CSV_PATH,index=False);st.session_state.admin_success_msg=f"✅ {dpid} beta status updated.";st.rerun()
    with qa2:
        if st.button("✏️ Edit in Drill Editor",use_container_width=True,key="preview_go_edit"): st.info("Switch to the 📋 Edit Drill Metadata tab.")
    with qa3:
        if st.button("🎨 Edit Schematic",use_container_width=True,key="preview_go_schematic"):
            st.session_state.newly_created_drill_id=dpid;st.info("Switch to the 🎨 Schematic Painter tab — drill pre-selected.")

with tab4:
    import json
    queue_path = Path("data/production/video_queue.json")
    if queue_path.exists():
        queue_cfg = json.loads(queue_path.read_text())
    else:
        queue_cfg = {"drive_folder_id": "", "reviewed": []}

    st.subheader("📁 Google Drive Folder")
    st.caption(
        "Set the Google Drive folder where your filmed videos "
        "are stored. To find a folder ID: open the folder in "
        "Drive, the ID is the last part of the URL: "
        "drive.google.com/drive/folders/**THIS_PART**"
    )

    with st.form("drive_folder_form"):
        folder_id_input = st.text_input(
            "Drive Folder ID",
            value=queue_cfg.get("drive_folder_id", ""),
            placeholder="e.g. 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74"
        )
        if st.form_submit_button("💾 Save Folder ID"):
            queue_cfg["drive_folder_id"] = folder_id_input.strip()
            queue_path.write_text(json.dumps(queue_cfg, indent=2))
            st.session_state.admin_success_msg = (
                "✅ Drive folder saved."
            )
            st.rerun()

    folder_id = queue_cfg.get("drive_folder_id", "").strip()

    if not folder_id:
        st.info(
            "👆 Paste your Google Drive folder ID above to "
            "start scanning for new videos."
        )
    else:
        scan_col, clear_col = st.columns([2, 1])
        with scan_col:
            if st.button(
                "🔍 Scan for New Videos",
                type="primary",
                key="scan_drive_btn"
            ):
                try:
                    import requests
                    query = (
                        f"'{folder_id}' in parents "
                        f"and mimeType contains 'video/' "
                        f"and trashed = false"
                    )
                    try:
                        from google.oauth2 import service_account
                        from googleapiclient.discovery import build
                        creds_path = Path(".streamlit/google_creds.json")
                        if creds_path.exists():
                            creds = service_account.Credentials.from_service_account_file(
                                str(creds_path),
                                scopes=["https://www.googleapis.com/auth/drive.readonly"]
                            )
                            service = build("drive", "v3", credentials=creds)
                            results = (
                                service.files()
                                .list(
                                    q=query,
                                    fields="files(id,name,mimeType,createdTime,size,thumbnailLink,webViewLink)",
                                    orderBy="createdTime desc"
                                )
                                .execute()
                            )
                            files = results.get("files", [])
                        else:
                            files = []
                            st.warning("No Google credentials found. See setup instructions below.")
                    except ImportError:
                        files = []
                        st.warning("google-api-python-client not installed. Run: pip install google-api-python-client google-auth")

                    st.session_state["drive_scan_results"] = files
                    st.session_state["drive_scan_time"] = (
                        datetime.datetime.now()
                        .strftime("%H:%M:%S")
                    )
                except Exception as ex:
                    st.error(f"Scan failed: {ex}")

        with clear_col:
            if st.button("🗑 Clear Queue", key="clear_reviewed"):
                queue_cfg["reviewed"] = []
                queue_path.write_text(json.dumps(queue_cfg, indent=2))
                st.session_state.pop("drive_scan_results", None)
                st.success("Queue cleared.")

        files = st.session_state.get("drive_scan_results", [])
        reviewed_ids = queue_cfg.get("reviewed", [])
        scan_time = st.session_state.get("drive_scan_time","")

        pending = [f for f in files if f["id"] not in reviewed_ids]
        done = [f for f in files if f["id"] in reviewed_ids]

        if scan_time:
            st.caption(f"Last scan: {scan_time} — {len(pending)} pending, {len(done)} reviewed")

        if not files:
            st.info("Click 'Scan for New Videos' to check your Drive folder for new footage.")
        elif not pending:
            st.success("✅ All videos in this folder have been reviewed. Scan again to check for new ones.")
        else:
            st.subheader(f"📋 Pending Review ({len(pending)} videos)")

            for vid_file in pending:
                fid = vid_file["id"]
                fname = vid_file.get("name", "Unnamed")
                created = vid_file.get("createdTime", "")[:10]
                size_bytes = int(vid_file.get("size", 0))
                size_mb = round(size_bytes / 1024 / 1024, 1)
                preview_url = f"https://drive.google.com/file/d/{fid}/preview"
                view_url = vid_file.get("webViewLink", "")

                with st.expander(f"📹 {fname} — {created} ({size_mb} MB)", expanded=True):
                    vcol1, vcol2 = st.columns([3, 2])

                    with vcol1:
                        st.markdown("**Preview:**")
                        st.components.v1.iframe(preview_url, height=240)
                        if view_url:
                            st.caption(f"[Open in Drive]({view_url})")

                    with vcol2:
                        st.markdown("**Link to drill:**")
                        drill_options = (
                            ["— Select a drill —"] +
                            [f"{r['drill_id']} — {r['drill_name']}" for _, r in df.iterrows()]
                        )
                        sel_drill = st.selectbox("Drill", drill_options, key=f"queue_drill_{fid}")
                        yt_url = st.text_input(
                            "YouTube URL (if already uploaded)",
                            placeholder="https://youtube.com/watch?v=...",
                            key=f"queue_yt_{fid}"
                        )
                        drive_as_fallback = st.checkbox(
                            "Use Drive preview as temp video",
                            value=False,
                            key=f"queue_drive_{fid}",
                            help="Links the Drive preview URL to the drill temporarily. Replace with YouTube URL when ready."
                        )

                        link_btn = st.button(
                            "🔗 Link to Drill",
                            key=f"queue_link_{fid}",
                            type="primary",
                            use_container_width=True,
                            disabled=sel_drill == "— Select a drill —"
                        )

                        if link_btn:
                            did = sel_drill.split(" — ")[0]
                            idx = df.index[df["drill_id"] == did][0]

                            if yt_url.strip():
                                df.at[idx, "video_url"] = yt_url.strip()
                                df.at[idx, "video_status"] = "Filmed"
                            elif drive_as_fallback:
                                df.at[idx, "video_url"] = preview_url
                                df.at[idx, "video_status"] = "Filmed"

                            df.at[idx, "filming_date"] = datetime.date.today().isoformat()
                            df.to_csv(CSV_PATH, index=False)

                            # Update demo copy if it exists
                            demo_csv = Path("data/production/users/demo/drill_library.csv")
                            if demo_csv.exists():
                                df.to_csv(demo_csv, index=False)

                            if fid not in reviewed_ids:
                                queue_cfg["reviewed"].append(fid)
                                queue_path.write_text(json.dumps(queue_cfg, indent=2))

                            st.session_state.admin_success_msg = f"✅ {fname} linked to {did}!"
                            st.rerun()

        if done:
            with st.expander(f"✅ Already reviewed ({len(done)})", expanded=False):
                for vf in done:
                    st.caption(f"✓ {vf.get('name','?')} — {vf.get('createdTime','')[:10]}")

    with st.expander("⚙️ Google Drive API Setup (first time only)", expanded=False):
        st.markdown("""
**To connect your Google Drive folder:**

**Option 1 — Service Account (recommended for Streamlit Cloud):**
1. Go to console.cloud.google.com
2. Create a project → Enable the Google Drive API
3. Create a Service Account → Download JSON key
4. Save the JSON file as `.streamlit/google_creds.json`
5. Share your Drive filming folder with the
   service account email address (found in the JSON)
6. Paste the folder ID above and scan

**Option 2 — Use Google Drive MCP (already connected):**
If the Google Drive MCP connector is active in Claude,
you can browse and search your Drive files from the
Claude chat interface directly. Ask Claude to search
for recently added video files in your filming folder.

**Finding your folder ID:**
Open the folder in Google Drive. The URL will look like:
`drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjg`
The folder ID is the last segment after `/folders/`.
        """)

st.divider()
st.subheader("🚀 Publish to GitHub")
st.caption("Pushes updated drill_library.csv and schematics to GitHub. Streamlit Cloud redeploys in ~60s.")
if st.button("Push to GitHub",type="primary",key="git_push_btn"):
    import subprocess
    r1=subprocess.run(["git","add","data/production/drill_library.csv","assets/diagrams/"],capture_output=True,text=True,cwd=str(Path.cwd()))
    if r1.returncode!=0: st.error(f"git add failed: {r1.stderr}")
    else:
        subprocess.run(["git","commit","-m","Player AI — drill library content update"],capture_output=True,text=True,cwd=str(Path.cwd()))
        r3=subprocess.run(["git","push","origin","main"],capture_output=True,text=True,cwd=str(Path.cwd()))
        if r3.returncode==0: st.success("✅ Pushed to GitHub!");st.caption("Streamlit Cloud will redeploy in ~60s.")
        else: st.error(f"Push failed: {r3.stderr}")
