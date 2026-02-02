import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Solo & Multi", layout="wide")

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

    #lower-area { display: flex; flex-direction: column; width: 100%; margin-top: 10px; gap: 10px; }
    #controls-row {
        display: flex; justify-content: space-between; align-items: center;
        background: #2a2a2a; padding: 15px; border-radius: 12px; border: 1px solid #444;
    }
    #right-control-group { display: flex; align-items: center; gap: 20px; }
    #fireBtn { 
        width: 75px; height: 75px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: none; font-weight: bold; font-size: 14px; 
        box-shadow: 0 5px #b33030; cursor: pointer; -webkit-tap-highlight-color: transparent;
    }
    #joystick-zone { width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; }
    #hp-bar-container { width: 120px; height: 12px; background: #444; border-radius: 6px; overflow: hidden; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }
    .status-item { background: #333; padding: 4px 8px; border-radius: 4px; border: 1px solid #555; }
    
    .btn-toggle { background: #555; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }
</style>

<div id="top-bar">
    <button id="mode-toggle" class="btn-toggle active-mode">ОДИНОЧНЫЙ (ИИ)</button>
    <div id="net-controls" style="display: none; gap: 4px;">
        <input type="text" id="remote-id" placeholder="ID Host" style="width: 70px; font-size: 10px;">
        <button id="connect-btn" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px;">СЕТЬ</button>
    </div>
    <div class="status-item">ID: <strong id="my-peer-id" style="color: #00d2ff;">...</strong></div>
    <div class="status-item"><span id="sc-me" style="color: #ff4b4b;">0</span> : <span id="sc-opp" style="color: #00d2ff;">0</span></div>
</div>

<div id="viewport-container">
    <div id="viewport">
        <canvas id="gameCanvas" width="1000" height="600"></canvas>
    </div>
</div>

<div id="lower-area">
    <div id="controls-row">
        <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
            <div id="hp-bar-container"><div id="hp-fill"></div></div>
            <div style="font-size: 10px; color: #aaa;">Цель: Сбить врага!</div>
        </div>
        <div id="right-control-group">
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
    let aiFireTimer = 0;
    
    let peer = new Peer();
    let conn = null;
    let bullets = [];
    
    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive', deathTimer: 0 };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, active: true, color: '#00d2ff', state: 'alive', deathTimer: 0 };

    // Mode Toggle
    document.getElementById('mode-toggle').onclick = function() {
        isSolo = !isSolo;
        this.innerText = isSolo ? "ОДИНОЧНЫЙ (ИИ)" : "СЕТЕВОЙ РЕЖИМ";
        this.classList.toggle('active-mode');
        document.getElementById('net-controls').style.display = isSolo ? 'none' : 'flex';
        // Сброс позиций
        respawn(me);
        respawn(opp);
    };

    // PeerJS
    peer.on('open', id => document.getElementById('my-peer-id').innerText = id);
    peer.on('connection', c => { 
        conn = c; 
        isSolo = false; 
        document.getElementById('mode-toggle').innerText = "В СЕТИ";
        setupConn(); 
    });
    document.getElementById('connect-btn').onclick = () => { conn = peer.connect(document.getElementById('remote-id').value); setupConn(); };

    function setupConn() {
        conn.on('data', d => {
            if(d.t === 's') { opp.x = d.x; opp.y = d.y; opp.a = d.a; opp.hp = d.hp; opp.active = true; opp.state = d.st; }
            if(d.t === 'f') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
            if(d.t === 'sc') { me.score = d.me; opp.score = d.opp; }
        });
    }

    // Controls
    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    document.getElementById('fireBtn').addEventListener('touchstart', (e) => {
        e.preventDefault(); fire();
    });
    document.getElementById('fireBtn').onmousedown = fire;

    function fire() {
        if(me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ t: 'f', x: me.x, y: me.y, a: me.a });
    }

    // AI Logic
    function updateAI() {
        if (!isSolo || opp.state !== 'alive') return;

        // 1. Поворот к игроку
        let angleToPlayer = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
        let diff = angleToPlayer - opp.a;
        while (diff < -180) diff += 360;
        while (diff > 180) diff -= 360;
        
        opp.a += diff * 0.05; // Плавность поворота ИИ

        // 2. Движение
        let r = opp.a * Math.PI/180;
        opp.x += Math.cos(r) * 4.5;
        opp.y += Math.sin(r) * 4.5;

        // 3. Стрельба
        aiFireTimer++;
        if (aiFireTimer > 40 && Math.abs(diff) < 15 && Math.hypot(me.x - opp.x, me.y - opp.y) < 800) {
            bullets.push({ x: opp.x, y: opp.y, a: opp.a, owner: 'opp' });
            aiFireTimer = 0;
        }
    }

    function update() {
        // Player move
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*5.5; me.y += Math.sin(r)*5.5;
            if(me.hp <= 0) { me.state = 'falling'; me.deathTimer = 100; }
        } else {
            me.y += 6; me.a += 15; me.deathTimer--;
            if(me.deathTimer <= 0) respawn(me);
        }

        // AI move
        if (isSolo) {
            if (opp.state === 'alive') {
                updateAI();
                if(opp.hp <= 0) { opp.state = 'falling'; opp.deathTimer = 100; }
            } else {
                opp.y += 6; opp.a += 15; opp.deathTimer--;
                if(opp.deathTimer <= 0) respawn(opp);
            }
        }

        // Screen wrap
        [me, opp].forEach(p => {
            if(p.x < 0) p.x = WORLD.w; if(p.x > WORLD.w) p.x = 0;
            if(p.y < 0) p.y = WORLD.h; if(p.y > WORLD.h) p.y = 0;
        });

        // Bullets
        bullets.forEach((b, i) => {
            let br = b.a * Math.PI/180;
            b.x += Math.cos(br)*14; b.y += Math.sin(br)*14;
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 45) {
                target.hp--;
                if(target.hp <= 0 && b.owner === 'me') me.score++;
                if(target.hp <= 0 && b.owner === 'opp' && !isSolo) opp.score++;
                bullets.splice(i, 1);
            }
            if(b.x < -500 || b.x > WORLD.w+500) bullets.splice(i,1);
        });

        if(conn && !isSolo) conn.send({ t: 's', x: me.x, y: me.y, a: me.a, hp: me.hp, st: me.state });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(canvas.width / WORLD.w, canvas.height / WORLD.h);
        
        bullets.forEach(b => { 
            ctx.fillStyle = b.owner === 'me' ? "white" : "yellow"; 
            ctx.beginPath(); ctx.arc(b.x, b.y, 10, 0, 7); ctx.fill(); 
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-10, -50, 20, 100); 
            ctx.fillStyle = "#333"; ctx.fillRect(-45, -12, 90, 24);
            ctx.restore();
        };
        drawPlane(me, me.color);
        drawPlane(opp, opp.color);
        ctx.restore();
        
        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = isSolo ? "BOT" : opp.score;
    }

    function respawn(p) {
        p.state = 'alive'; p.hp = 5;
        p.x = Math.random() * (WORLD.w - 400) + 200;
        p.y = Math.random() * (WORLD.h - 400) + 200;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=600)