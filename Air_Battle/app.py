import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Pro Controls", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 5px; background: #111; font-family: sans-serif; overflow-x: hidden; color: white; }
    #top-bar { 
        background: #222; padding: 8px; border-radius: 8px; 
        display: flex; justify-content: space-between; align-items: center; 
        flex-wrap: wrap; gap: 5px; margin-bottom: 5px; font-size: 11px;
    }
    #viewport-container { position: relative; width: 100%; margin: 0 auto; touch-action: none; }
    #viewport { 
        position: relative; width: 100%; height: 320px; 
        background: #87CEEB; border: 2px solid #444; overflow: hidden; border-radius: 8px; 
    }
    canvas { width: 100%; height: 100%; display: block; }

    /* Нижняя панель */
    #lower-area { display: flex; flex-direction: column; width: 100%; margin-top: 10px; }
    
    #controls-row {
        display: flex;
        justify-content: space-between; /* Здоровье слева, управление справа */
        align-items: center;
        background: #2a2a2a;
        padding: 10px 15px;
        border-radius: 12px;
        border: 1px solid #444;
    }

    /* БЛОК УПРАВЛЕНИЯ СПРАВА */
    #right-stick-group {
        display: flex;
        align-items: center;
        gap: 15px; /* Расстояние между кнопкой и джойстиком */
    }

    #fireBtn { 
        width: 80px; height: 80px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: none; font-weight: bold; font-size: 14px; 
        box-shadow: 0 5px #b33030; cursor: pointer; -webkit-tap-highlight-color: transparent;
        z-index: 10;
    }
    #fireBtn:active { transform: translateY(3px); box-shadow: 0 2px #b33030; }

    #joystick-zone { 
        width: 110px; height: 110px; background: rgba(255,255,255,0.05); 
        border-radius: 50%; position: relative;
    }

    /* Левая часть: Здоровье и статус */
    #left-info { display: flex; flex-direction: column; gap: 10px; }
    #hp-bar-container { width: 100px; height: 12px; background: #444; border-radius: 6px; overflow: hidden; border: 1px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }
    .status-item { background: #333; padding: 4px 8px; border-radius: 4px; border: 1px solid #555; }
</style>

<div id="top-bar">
    <button id="mode-toggle" style="background:#555; color:white; border:none; padding:5px; border-radius:4px;">РЕЖИМ: ИИ</button>
    <div id="net-controls" style="display: none; gap: 4px;">
        <input type="text" id="remote-id" placeholder="ID Host" style="width: 60px; font-size: 10px;">
        <button id="connect-btn" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px;">OK</button>
    </div>
    <div class="status-item">ID: <strong id="my-peer-id" style="color: #00d2ff;">...</strong></div>
    <div class="status-item"><span id="sc-me" style="color: #ff4b4b;">0</span> : <span id="sc-opp" style="color: #00d2ff;">0</span></div>
</div>

<div id="viewport-container">
    <div id="viewport"><canvas id="gameCanvas" width="1000" height="600"></canvas></div>
</div>

<div id="lower-area">
    <div id="controls-row">
        <div id="left-info">
            <div id="hp-bar-container"><div id="hp-fill"></div></div>
            <div style="font-size: 10px; color: #888;">HP PILOT</div>
        </div>

        <div id="right-stick-group">
            <button id="fireBtn">ОГОНЬ</button>
            <div id="joystick-zone"></div>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>
<script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 3000, h: 2000 };
    let isSolo = true;
    let bullets = [];
    let peer = new Peer();
    let conn = null;

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, active: true, color: '#00d2ff', state: 'alive' };

    // Mode Toggle
    document.getElementById('mode-toggle').onclick = function() {
        isSolo = !isSolo;
        this.innerText = isSolo ? "РЕЖИМ: ИИ" : "РЕЖИМ: СЕТЬ";
        document.getElementById('net-controls').style.display = isSolo ? 'none' : 'flex';
    };

    // PeerJS
    peer.on('open', id => document.getElementById('my-peer-id').innerText = id);
    peer.on('connection', c => { conn = c; isSolo = false; setupConn(); });
    document.getElementById('connect-btn').onclick = () => { conn = peer.connect(document.getElementById('remote-id').value); setupConn(); };

    function setupConn() {
        conn.on('data', d => {
            if(d.t === 's') { opp.x = d.x; opp.y = d.y; opp.a = d.a; opp.hp = d.hp; opp.active = true; opp.state = d.st; }
            if(d.t === 'f') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
            if(d.t === 'sc') { me.score = d.me; opp.score = d.opp; }
        });
    }

    // Joystick
    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    // Fire
    const fireAction = (e) => {
        if(e) e.preventDefault();
        if(me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ t: 'f', x: me.x, y: me.y, a: me.a });
    };
    document.getElementById('fireBtn').addEventListener('touchstart', fireAction);
    document.getElementById('fireBtn').onclick = fireAction;

    function update() {
        // Player move
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*5; me.y += Math.sin(r)*5;
            if(me.hp <= 0) { me.state = 'falling'; me.deathTimer = 100; }
        } else {
            me.y += 6; me.a += 10; me.deathTimer--;
            if(me.deathTimer <= 0) { me.state='alive'; me.hp=5; me.x=500; me.y=500; }
        }

        // AI Logic (Simple)
        if(isSolo && opp.state === 'alive') {
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * 0.03;
            let r = opp.a * Math.PI/180;
            opp.x += Math.cos(r)*4; opp.y += Math.sin(r)*4;
            if(Math.random() < 0.02) bullets.push({x: opp.x, y: opp.y, a: opp.a, owner: 'opp'});
            if(opp.hp <= 0) { opp.state = 'falling'; opp.deathTimer = 100; }
        } else if (isSolo) {
            opp.y += 6; opp.deathTimer--; if(opp.deathTimer <= 0) { opp.state='alive'; opp.hp=5; opp.x=2500; opp.y=1500; }
        }

        bullets.forEach((b, i) => {
            let br = b.a * Math.PI/180;
            b.x += Math.cos(br)*12; b.y += Math.sin(br)*12;
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 40) {
                target.hp--;
                if(target.hp <= 0 && b.owner === 'me') me.score++;
                bullets.splice(i, 1);
            }
        });
        if(conn) conn.send({ t: 's', x: me.x, y: me.y, a: me.a, hp: me.hp, st: me.state });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(canvas.width / WORLD.w, canvas.height / WORLD.h);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 8, 0, 7); ctx.fill(); });
        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-10, -50, 20, 100); ctx.fillStyle = "#333"; ctx.fillRect(-40, -10, 80, 20);
            ctx.restore();
        };
        drawPlane(me, me.color); drawPlane(opp, opp.color);
        ctx.restore();
        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = isSolo ? "AI" : opp.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=550)