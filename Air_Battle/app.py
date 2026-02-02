import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Fullscreen", layout="wide")

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

    #controls-container { 
        position: absolute; 
        bottom: 60px; /* ПОДНЯТО ВЫШЕ */
        left: 0; 
        width: 100%; 
        height: 140px; 
        pointer-events: none; 
        z-index: 100; 
    }
    #fireBtn { 
        position: absolute; left: 30px; bottom: 0;
        width: 90px; height: 90px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: 4px solid #b33030; font-weight: bold; font-size: 14px; 
        box-shadow: 0 5px #000; cursor: pointer; pointer-events: auto; touch-action: none;
    }
    #joystick-wrapper { 
        position: absolute; right: 30px; bottom: 0; 
        width: 120px; height: 120px; pointer-events: auto; touch-action: none; 
    }
    
    #hp-center { position: absolute; left: 50%; bottom: -30px; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; gap: 5px; }
    #hp-bar-container { width: 120px; height: 12px; background: #444; border-radius: 6px; overflow: hidden; border: 1px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }

    .btn-mode { background: #444; color: white; border: 1px solid #666; padding: 5px 8px; border-radius: 4px; font-size: 9px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }
    
    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 200;
    }
    #net-status { position: absolute; top: 55px; left: 15px; font-size: 10px; color: #0f0; z-index: 60; }
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
<div id="net-status">Режим: AI</div>

<div id="viewport">
    <canvas id="gameCanvas"></canvas>
    <div id="overlay">
        <h1 id="win-text">ПОБЕДА!</h1>
        <button onclick="location.reload()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px;">РЕСТАРТ</button>
    </div>
    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="hp-center">
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
    
    // МИР ТЕПЕРЬ ВСЕГДА РАВЕН ЭКРАНУ
    let WORLD = { w: window.innerWidth, h: window.innerHeight };
    
    function resize() { 
        canvas.width = window.innerWidth; 
        canvas.height = window.innerHeight; 
        WORLD.w = canvas.width;
        WORLD.h = canvas.height;
    }
    window.onresize = resize; resize();

    let scoreLimit = 5;
    let gameOver = false;
    let bullets = [], particles = [], clouds = [];
    let me = { x: 100, y: 100, a: 0, hp: 5, score: 0, color: '#ff4b4b', state: 'alive', dt: 0 };
    let opp = { x: WORLD.w - 100, y: WORLD.h - 100, a: 180, hp: 5, score: 0, color: '#00d2ff', state: 'alive', dt: 0 };
    let conn = null;

    // Генерация облаков под размер экрана
    for(let i=0; i<15; i++) {
        clouds.push({
            x: Math.random() * WORLD.w, y: Math.random() * WORLD.h,
            size: 60 + Math.random() * 80, speed: 0.2 + Math.random() * 0.4, opacity: 0.5
        });
    }

    // --- СЕТЬ ---
    document.getElementById('mode-net').onclick = () => {
        const peer = new Peer();
        const statusEl = document.getElementById('net-status');
        peer.on('open', id => {
            statusEl.innerText = "ID: " + id;
            const targetId = prompt("Твой ID: " + id + "\\nВведи ID друга:");
            if(targetId) { conn = peer.connect(targetId); setupConn(); }
        });
        peer.on('connection', c => { conn = c; setupConn(); });
    };

    function setupConn() {
        document.getElementById('net-status').innerText = "СЕТЬ: ПОДКЛЮЧЕНО";
        conn.on('data', d => {
            if(d.type === 'state') { opp.x=d.x; opp.y=d.y; opp.a=d.a; opp.hp=d.hp; opp.state=d.state; opp.score=d.score; }
            if(d.type === 'fire') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
            if(d.type === 'explode') createExplosion(d.x, d.y);
        });
    }

    // --- УПРАВЛЕНИЕ ---
    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'}, color:'white', size:100 });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fireBtn = document.getElementById('fireBtn');
    fireBtn.onclick = (e) => {
        if(me.state !== 'alive' || gameOver) return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ type: 'fire', x: me.x, y: me.y, a: me.a });
    };

    function createParticle(x, y, type, vx, vy) {
        particles.push({ x, y, vx: vx || (Math.random()-0.5)*2, vy: vy || (Math.random()-0.5)*2, life: 1.0, type });
    }

    function createExplosion(x, y) {
        for(let i=0; i<20; i++) createParticle(x, y, 'fire', (Math.random()-0.5)*10, (Math.random()-0.5)*10);
    }

    function update() {
        if(gameOver) return;
        
        clouds.forEach(c => { c.x += c.speed; if(c.x > WORLD.w) c.x = -c.size; });

        const movePlane = (p, isMe) => {
            if(p.state === 'alive') {
                let r = p.a * Math.PI/180; p.x += Math.cos(r)*5; p.y += Math.sin(r)*5;
                if(p.x < 0) p.x = WORLD.w; if(p.x > WORLD.w) p.x = 0;
                if(p.y < 0) p.y = WORLD.h; if(p.y > WORLD.h) p.y = 0;
                if(p.hp <= 3 && Math.random() > 0.7) createParticle(p.x, p.y, 'smoke');
            } else {
                p.y += 3; p.a += 10; createParticle(p.x, p.y, 'fire'); p.dt--;
                if(p.dt <= 0 && isMe) {
                    createExplosion(p.x, p.y);
                    p.state='alive'; p.hp=5; p.x=Math.random()*WORLD.w; p.y=Math.random()*WORLD.h;
                }
            }
        };

        movePlane(me, true);
        if(!conn) {
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * 0.05;
            movePlane(opp, false);
            if(Math.random() < 0.02) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
        } else { movePlane(opp, false); }

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180; b.x += Math.cos(r)*12; b.y += Math.sin(r)*12;
            if(b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) { bullets.splice(i, 1); return; }
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 40) {
                target.hp--; bullets.splice(i, 1);
                if(target.hp <= 0) { 
                    target.state = 'falling'; target.dt = 120;
                    if(b.owner === 'me') me.score++; else opp.score++;
                    if(me.score >= scoreLimit || opp.score >= scoreLimit) {
                        gameOver = true; document.getElementById('overlay').style.display = 'flex';
                    }
                }
            }
        });

        particles.forEach((p, i) => { p.x += p.vx; p.y += p.vy; p.life -= 0.02; if(p.life <= 0) particles.splice(i, 1); });
        if(conn) conn.send({ type: 'state', x: me.x, y: me.y, a: me.a, hp: me.hp, state: me.state, score: me.score });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        clouds.forEach(c => {
            ctx.fillStyle = `rgba(255,255,255,${c.opacity})`;
            ctx.beginPath(); ctx.arc(c.x, c.y, c.size, 0, 7); ctx.fill();
        });

        particles.forEach(p => {
            ctx.fillStyle = p.type === 'smoke' ? `rgba(150,150,150,${p.life})` : `rgba(255,100,0,${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='smoke'?10:15, 0, 7); ctx.fill();
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-15, -40, 30, 80); // Корпус
            ctx.fillStyle = "#333"; ctx.fillRect(-40, -10, 80, 20); // Крылья
            ctx.restore();
        };

        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 6, 0, 7); ctx.fill(); });

        document.getElementById('hp-fill').style.width = (me.hp/5*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=800)