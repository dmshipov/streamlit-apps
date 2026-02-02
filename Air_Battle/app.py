import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Mobile", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 5px; background: #111; font-family: sans-serif; overflow-x: hidden; }
    
    /* Контейнер верхней панели */
    #top-bar { 
        background: #222; color: white; padding: 8px; border-radius: 8px; 
        display: flex; justify-content: space-between; align-items: center; 
        flex-wrap: wrap; gap: 5px; margin-bottom: 5px; font-size: 12px;
    }

    /* Игровое поле */
    #viewport-container { position: relative; width: 100%; margin: 0 auto; touch-action: none; }
    #viewport { 
        position: relative; width: 100%; height: 350px; /* Уменьшено для мобильных */
        background: #87CEEB; border: 2px solid #333; overflow: hidden; border-radius: 8px; 
    }
    canvas { width: 100%; height: 100%; display: block; }

    /* Нижняя область (Чат и Управление) */
    #lower-area { 
        display: flex; flex-direction: column; /* Вертикально на мобильных */
        width: 100%; margin: 10px auto; gap: 10px; 
    }

    /* Адаптация для десктопа (если экран широкий) */
    @media (min-width: 800px) {
        #lower-area { flex-direction: row; }
        #viewport { height: 500px; }
    }

    #chat-box { 
        flex: 1; background: #fff; border-radius: 8px; display: flex; 
        flex-direction: column; height: 150px; min-width: 200px;
    }
    #chat-messages { flex: 1; overflow-y: auto; padding: 8px; font-size: 12px; color: #333; }
    
    #controls { 
        flex: 1.2; display: flex; justify-content: space-around; align-items: center; 
        background: #f0f0f0; border-radius: 8px; padding: 10px; min-height: 140px;
    }

    #fireBtn { 
        width: 80px; height: 80px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: none; font-weight: bold; font-size: 14px; 
        box-shadow: 0 4px #b33030; cursor: pointer; -webkit-tap-highlight-color: transparent;
    }
    
    .status-item { background: #333; padding: 4px 8px; border-radius: 4px; }
</style>

<div id="top-bar">
    <div class="status-item">
        ID: <strong id="my-peer-id" style="color: #00d2ff;">...</strong>
        <button id="copy-btn" style="font-size: 10px; margin-left: 5px;">Copy</button>
    </div>
    
    <div style="display: flex; gap: 4px;">
        <input type="text" id="remote-id" placeholder="ID host" style="width: 70px; font-size: 11px;">
        <button id="connect-btn" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px;">СЕТЬ</button>
    </div>

    <div style="font-weight: bold; font-size: 14px;">
        <span id="sc-me" style="color: #ff4b4b;">0</span> : <span id="sc-opp" style="color: #00d2ff;">0</span>
    </div>
</div>

<div id="viewport-container">
    <div id="viewport">
        <canvas id="gameCanvas" width="1000" height="600"></canvas>
        <div id="pause-overlay" style="position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.4); display: none; justify-content: center; align-items: center; z-index: 50; color: white; font-size: 30px; font-weight: bold;">ПАУЗА</div>
        <div id="radar" style="position: absolute; top: 5px; right: 5px; width: 80px; height: 50px; background: rgba(0,0,0,0.5); border: 1px solid white; display: none; border-radius: 4px;">
            <div id="radar-me" style="position: absolute; width: 3px; height: 3px; background: #ff4b4b;"></div>
            <div id="radar-opp" style="position: absolute; width: 3px; height: 3px; background: #00d2ff;"></div>
        </div>
    </div>
</div>

<div id="lower-area">
    <div id="controls">
        <div id="joystick-zone" style="width: 100px; height: 100px;"></div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <div id="hp-bar" style="width: 100px; height: 10px; background: #333; border-radius: 5px; overflow: hidden;">
                <div id="hp-fill" style="width: 100%; height: 100%; background: #28a745;"></div>
            </div>
            <button id="fireBtn">ОГОНЬ</button>
        </div>
        <div style="display: flex; flex-direction: column; gap: 5px;">
             <button id="pause-btn" style="font-size: 10px; padding: 5px; background: #f39c12; color: white; border: none; border-radius: 4px;">PAUSE</button>
             <button id="view-mode-btn" style="font-size: 10px; padding: 5px; background: #555; color: white; border: none; border-radius: 4px;">CAM</button>
        </div>
    </div>

    <div id="chat-box">
        <div id="chat-messages"></div>
        <div style="display: flex; border-top: 1px solid #ddd; padding: 4px;">
            <input type="text" id="chat-input" placeholder="Чат..." style="flex: 1; border: none; font-size: 12px; outline: none;">
            <button id="send-chat" style="background: #00d2ff; border: none; padding: 0 10px; border-radius: 4px; color: white;">▶</button>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>
<script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 3000, h: 2000 };
    let isCamera = false;
    let isPaused = false;
    
    let peer = new Peer();
    let conn = null;
    let particles = [];
    let bullets = [];
    
    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive', deathTimer: 0 };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, active: false, color: '#00d2ff', state: 'alive' };

    const clouds = [];
    for(let i=0; i<15; i++) clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, w: 180, h: 60, opacity: 0.3 });

    function createParticle(x, y, type, speed) {
        particles.push({
            x, y, vx: (Math.random()-0.5)*speed, vy: (Math.random()-0.5)*speed,
            life: 1.0, type: type
        });
    }

    peer.on('open', id => document.getElementById('my-peer-id').innerText = id);
    peer.on('connection', c => { conn = c; setupConn(); });
    document.getElementById('connect-btn').onclick = () => { conn = peer.connect(document.getElementById('remote-id').value); setupConn(); };

    function setupConn() {
        conn.on('data', d => {
            if(d.t === 's') { opp.x = d.x; opp.y = d.y; opp.a = d.a; opp.hp = d.hp; opp.active = true; opp.state = d.st; }
            if(d.t === 'f') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
            if(d.t === 'sc') { me.score = d.me; opp.score = d.opp; }
            if(d.t === 'chat') addMsg("Друг: " + d.msg, opp.color);
        });
    }

    function addMsg(text, color) {
        const d = document.createElement('div'); d.style.color = color; d.innerText = text;
        const c = document.getElementById('chat-messages'); c.appendChild(d); c.scrollTop = c.scrollHeight;
    }

    document.getElementById('send-chat').onclick = sendChat;
    function sendChat() {
        const inp = document.getElementById('chat-input');
        if(!inp.value.trim()) return;
        addMsg("Я: " + inp.value, me.color);
        if(conn) conn.send({ t: 'chat', msg: inp.value });
        inp.value = "";
    }

    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    document.getElementById('fireBtn').onclick = () => {
        if(isPaused || me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ t: 'f', x: me.x, y: me.y, a: me.a });
    };

    document.getElementById('view-mode-btn').onclick = () => {
        isCamera = !isCamera;
        document.getElementById('radar').style.display = isCamera ? "block" : "none";
    };

    function update() {
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*5; me.y += Math.sin(r)*5;
            if(me.hp <= 0) { me.state = 'falling'; me.deathTimer = 100; }
        } else {
            me.y += 6; me.a += 15; me.x += (Math.random()-0.5)*10;
            createParticle(me.x, me.y, 'smoke', 3);
            me.deathTimer--;
            if(me.deathTimer <= 0 || me.y > WORLD.h) { me.state='alive'; me.hp=5; me.x=500; me.y=500; }
        }

        bullets.forEach((b, i) => {
            let br = b.a * Math.PI/180;
            b.x += Math.cos(br)*12; b.y += Math.sin(br)*12;
            let target = b.owner === 'me' ? opp : me;
            if(target.active && target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 40) {
                if(b.owner === 'me') { opp.hp--; if(opp.hp<=0) me.score++; }
                bullets.splice(i, 1);
            }
        });
        
        particles.forEach((p, i) => { p.life -= 0.02; if(p.life <= 0) particles.splice(i, 1); });
        if(conn) conn.send({ t: 's', x: me.x, y: me.y, a: me.a, hp: me.hp, st: me.state });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        if(isCamera) ctx.translate(canvas.width/2 - me.x, canvas.height/2 - me.y);
        else ctx.scale(canvas.width / WORLD.w, canvas.height / WORLD.h);

        clouds.forEach(c => {
            ctx.fillStyle = `rgba(255, 255, 255, ${c.opacity})`;
            ctx.beginPath(); ctx.ellipse(c.x, c.y, c.w/2, c.h/2, 0, 0, 7); ctx.fill();
        });

        particles.forEach(p => {
            ctx.fillStyle = `rgba(100,100,100,${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, 10, 0, 7); ctx.fill();
        });

        bullets.forEach(b => {
            ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 5, 0, 7); ctx.fill();
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = "#333"; ctx.fillRect(-30, -8, 60, 16);
            ctx.fillStyle = col; ctx.fillRect(-8, -45, 16, 90);
            ctx.restore();
        };
        drawPlane(me, me.color);
        if(opp.active) drawPlane(opp, opp.color);
        ctx.restore();
        
        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
        
        if(isCamera) {
            document.getElementById('radar-me').style.left = (me.x/WORLD.w*100) + "%";
            document.getElementById('radar-me').style.top = (me.y/WORLD.h*100) + "%";
            document.getElementById('radar-opp').style.left = (opp.x/WORLD.w*100) + "%";
            document.getElementById('radar-opp').style.top = (opp.y/WORLD.h*100) + "%";
        }
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

# Изменили высоту здесь, чтобы streamlit не обрезал нижнюю часть
components.html(game_html, height=800)