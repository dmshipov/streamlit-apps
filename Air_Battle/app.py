import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Network Ace Combat", layout="wide")

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

    .btn-mode { background: #444; color: white; border: 1px solid #666; padding: 5px 10px; border-radius: 4px; font-size: 10px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }
    input { background: #333; color: white; border: 1px solid #555; padding: 4px; border-radius: 4px; width: 80px; font-size: 10px; }
</style>

<div id="top-bar">
    <div style="display:flex; gap:5px; align-items: center;">
        <button id="mode-solo" class="btn-mode active-mode">БОТ</button>
        <button id="mode-net" class="btn-mode">СЕТЬ</button>
        <div id="net-ui" style="display:none; gap:5px;">
            <span id="my-id" style="color:#0f0; font-weight:bold">ID: ...</span>
            <input type="text" id="peer-id-input" placeholder="ID друга">
            <button id="connect-btn" class="btn-mode">OK</button>
        </div>
    </div>
    <div style="font-size: 18px; font-weight: bold;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
</div>

<div id="viewport">
    <canvas id="gameCanvas"></canvas>
    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="hp-center">
            <div style="font-size: 11px; color: #fff; text-shadow: 1px 1px 2px #000;">HP PILOT</div>
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
    
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.onresize = resize;
    resize();

    let isSolo = true;
    let peer, conn;
    let bullets = [], particles = [], clouds = [];
    
    for(let i=0; i<15; i++) clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.5 + Math.random(), op: 0.3 });

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, score: 0, color: '#00d2ff', state: 'alive' };

    // --- СЕТЕВАЯ ЛОГИКА ---
    document.getElementById('mode-solo').onclick = () => location.reload();
    document.getElementById('mode-net').onclick = () => {
        isSolo = false;
        document.getElementById('mode-net').classList.add('active-mode');
        document.getElementById('mode-solo').classList.remove('active-mode');
        document.getElementById('net-ui').style.display = 'flex';
        initPeer();
    };

    function initPeer() {
        peer = new Peer();
        peer.on('open', id => document.getElementById('my-id').innerText = "ID: " + id);
        peer.on('connection', c => { conn = c; setupConn(); });
    }

    document.getElementById('connect-btn').onclick = () => {
        const id = document.getElementById('peer-id-input').value;
        conn = peer.connect(id);
        setupConn();
    };

    function setupConn() {
        conn.on('data', data => {
            if(data.type === 'state') {
                opp.x = data.x; opp.y = data.y; opp.a = data.a; 
                opp.hp = data.hp; opp.state = data.state;
            }
            if(data.type === 'fire') {
                bullets.push({ x: data.x, y: data.y, a: data.a, owner: 'opp' });
            }
        });
    }

    // --- УПРАВЛЕНИЕ ---
    const joy = nipplejs.create({
        zone: document.getElementById('joystick-zone'),
        mode: 'static', position: { left: '50%', top: '50%' },
        color: 'white', size: 100
    });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = () => { 
        if(me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' }); 
        if(conn) conn.send({ type: 'fire', x: me.x, y: me.y, a: me.a });
    };
    document.getElementById('fireBtn').ontouchstart = (e) => { e.preventDefault(); fire(); };
    document.getElementById('fireBtn').onclick = fire;

    function wrap(obj) {
        if (obj.x < 0) obj.x = WORLD.w;
        if (obj.x > WORLD.w) obj.x = 0;
        if (obj.y < 0) obj.y = WORLD.h;
        if (obj.y > WORLD.h) obj.y = 0;
    }

    function update() {
        // Me
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*7.5; me.y += Math.sin(r)*7.5;
            wrap(me);
            if(me.hp <= 0) { me.state = 'falling'; me.dt = 120; opp.score++; }
        } else {
            me.y += 5; me.a += 10;
            if(--me.dt <= 0) { me.state='alive'; me.hp=5; me.x=Math.random()*WORLD.w; me.y=Math.random()*WORLD.h; }
        }

        // Opponent (AI or Net)
        if(isSolo) {
            if(opp.state === 'alive') {
                let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
                let diff = targetA - opp.a;
                while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
                opp.a += diff * 0.05;
                let r = opp.a * Math.PI/180;
                opp.x += Math.cos(r)*6; opp.y += Math.sin(r)*6;
                wrap(opp);
                if(Math.random() < 0.02) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
                if(opp.hp <= 0) { opp.state = 'falling'; opp.dt = 120; me.score++; }
            } else {
                opp.y += 5;
                if(--opp.dt <= 0) { opp.state='alive'; opp.hp=5; opp.x=Math.random()*WORLD.w; opp.y=Math.random()*WORLD.h; }
            }
        }

        if(conn) conn.send({ type: 'state', x: me.x, y: me.y, a: me.a, hp: me.hp, state: me.state });

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180; b.x += Math.cos(r)*22; b.y += Math.sin(r)*22;
            wrap(b);
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 70) {
                target.hp--; bullets.splice(i, 1);
            }
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        let scale = Math.min(canvas.width / WORLD.w, canvas.height / WORLD.h);
        ctx.scale(scale, scale);

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; 
            ctx.fillRect(-30, -90, 60, 180); // Корпус (УВЕЛИЧЕН)
            ctx.fillStyle = "#333"; 
            ctx.fillRect(-80, -25, 160, 50); // Крылья (УВЕЛИЧЕНЫ)
            ctx.restore();
        };

        drawPlane(me, me.color);
        drawPlane(opp, opp.color);

        bullets.forEach(b => { 
            ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 18, 0, 7); ctx.fill(); 
        });

        ctx.restore();
        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=600)