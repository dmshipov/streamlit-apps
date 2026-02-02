import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Battle Edition", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 0; background: #111; font-family: sans-serif; overflow: hidden; color: white; touch-action: none; }
    #top-bar { 
        position: absolute; top: 10px; left: 10px; right: 10px;
        background: rgba(34, 34, 34, 0.8); padding: 8px; border-radius: 8px; 
        display: flex; justify-content: space-between; align-items: center; 
        z-index: 50; font-size: 11px;
    }
    #viewport { position: relative; width: 100vw; height: 100vh; background: #87CEEB; overflow: hidden; }
    canvas { width: 100%; height: 100%; display: block; }

    #controls-container { position: absolute; bottom: 20px; left: 0; width: 100%; height: 120px; pointer-events: none; z-index: 100; }
    #fireBtn { 
        position: absolute; left: 30px; bottom: 10px;
        width: 100px; height: 100px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: 4px solid #b33030; font-weight: bold; font-size: 16px; 
        box-shadow: 0 5px #000; cursor: pointer; pointer-events: auto;
    }
    #joystick-wrapper { position: absolute; right: 30px; bottom: 10px; width: 130px; height: 130px; pointer-events: auto; }
    
    #hp-center { position: absolute; left: 50%; bottom: 20px; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; gap: 5px; }
    #hp-bar-container { width: 150px; height: 15px; background: #444; border-radius: 8px; overflow: hidden; border: 1px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }

    .btn-mode { background: #444; color: white; border: 1px solid #666; padding: 5px 8px; border-radius: 4px; font-size: 9px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }
    
    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 200;
    }
</style>

<div id="top-bar">
    <div style="display:flex; gap:3px;">
        <button id="limit-1" class="btn-mode">ДО 1</button>
        <button id="limit-5" class="btn-mode active-mode">ДО 5</button>
        <button id="limit-10" class="btn-mode">ДО 10</button>
        <button id="mode-net" class="btn-mode" style="margin-left: 10px; background: #28a745;">СЕТЬ</button>
    </div>
    <div style="font-size: 18px; font-weight: bold;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
</div>

<div id="viewport">
    <canvas id="gameCanvas"></canvas>
    <div id="overlay">
        <h1 id="win-text">ПОБЕДА!</h1>
        <button onclick="location.reload()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px;">РЕСТАРТ</button>
    </div>
    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="hp-center">
            <div style="font-size: 10px; color: #fff;">HP PILOT</div>
            <div id="hp-bar-container"><div id="hp-fill"></div></div>
        </div>
        <div id="joystick-wrapper"><div id="joystick-zone"></div></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>
<script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 3000, h: 2000 };
    
    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.onresize = resize; resize();

    let scoreLimit = 5;
    let gameOver = false;
    let bullets = [], particles = [], clouds = [];
    let me = { x: 500, y: 500, a: 0, hp: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, score: 0, color: '#00d2ff', state: 'alive' };
    let conn = null;

    // Режимы
    const setLimit = (val, id) => {
        scoreLimit = val;
        document.querySelectorAll('.btn-mode').forEach(b => b.classList.remove('active-mode'));
        document.getElementById(id).classList.add('active-mode');
    };
    document.getElementById('limit-1').onclick = () => setLimit(1, 'limit-1');
    document.getElementById('limit-5').onclick = () => setLimit(5, 'limit-5');
    document.getElementById('limit-10').onclick = () => setLimit(10, 'limit-10');

    // Сеть
    document.getElementById('mode-net').onclick = () => {
        const peer = new Peer();
        peer.on('open', id => {
            const connectId = prompt("Твой ID: " + id + "\\nВведи ID друга для подключения (или оставь пустым, чтобы ждать):");
            if(connectId) {
                conn = peer.connect(connectId);
                setupConn();
            }
        });
        peer.on('connection', c => { conn = c; setupConn(); });
    };

    function setupConn() {
        conn.on('data', d => {
            if(d.type === 'state') { opp.x=d.x; opp.y=d.y; opp.a=d.a; opp.hp=d.hp; opp.state=d.state; opp.score=d.score; }
            if(d.type === 'fire') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
        });
    }

    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'}, color:'white', size:100 });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = () => {
        if(me.state !== 'alive' || gameOver) return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ type: 'fire', x: me.x, y: me.y, a: me.a });
    };
    document.getElementById('fireBtn').ontouchstart = (e) => { e.preventDefault(); fire(); };
    document.getElementById('fireBtn').onclick = fire;

    function checkVictory() {
        if (me.score >= scoreLimit || opp.score >= scoreLimit) {
            gameOver = true;
            document.getElementById('overlay').style.display = 'flex';
            document.getElementById('win-text').innerText = me.score >= scoreLimit ? "ПОБЕДА!" : "ПРОИГРЫШ!";
            document.getElementById('win-text').style.color = me.score >= scoreLimit ? "#00ff00" : "#ff4b4b";
        }
    }

    function update() {
        if(gameOver) return;

        // Полет и телепортация самолетов
        const movePlane = (p) => {
            if(p.state === 'alive') {
                let r = p.a * Math.PI/180; p.x += Math.cos(r)*8; p.y += Math.sin(r)*8;
                if(p.x < 0) p.x = WORLD.w; if(p.x > WORLD.w) p.x = 0;
                if(p.y < 0) p.y = WORLD.h; if(p.y > WORLD.h) p.y = 0;
            } else {
                p.y += 6; p.a += 5;
                if(--p.dt <= 0) { p.state='alive'; p.hp=5; p.x=Math.random()*WORLD.w; p.y=Math.random()*WORLD.h; }
            }
        };

        movePlane(me);
        if(!conn) { // AI
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * 0.05;
            movePlane(opp);
            if(Math.random() < 0.02 && opp.state==='alive') bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
        }

        // Пули (ИСЧЕЗАЮТ У ГРАНИЦ)
        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180; b.x += Math.cos(r)*22; b.y += Math.sin(r)*22;
            if(b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) { bullets.splice(i, 1); return; }
            
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 80) {
                target.hp--; bullets.splice(i, 1);
                if(target.hp <= 0) { 
                    target.state = 'falling'; target.dt = 120; 
                    if(b.owner === 'me') me.score++; else opp.score++;
                    checkVictory();
                }
            }
        });

        if(conn) conn.send({ type: 'state', x: me.x, y: me.y, a: me.a, hp: me.hp, state: me.state, score: me.score });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        let scale = Math.min(canvas.width / WORLD.w, canvas.height / WORLD.h);
        ctx.scale(scale, scale);

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-35, -100, 70, 200); 
            ctx.fillStyle = "#333"; ctx.fillRect(-90, -25, 180, 50);
            ctx.restore();
        };

        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 20, 0, 7); ctx.fill(); });
        ctx.restore();

        document.getElementById('hp-fill').style.width = (me.hp/5*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=600)