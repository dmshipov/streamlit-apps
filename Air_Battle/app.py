import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Battle Modes", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 5px; background: #111; font-family: sans-serif; overflow-x: hidden; color: white; }
    #top-bar { 
        background: #222; padding: 8px; border-radius: 8px; 
        display: flex; justify-content: space-between; align-items: center; 
        gap: 5px; margin-bottom: 5px; font-size: 11px;
    }
    #viewport-container { position: relative; width: 100%; margin: 0 auto; touch-action: none; }
    #viewport { 
        position: relative; width: 100%; height: 350px; 
        background: #87CEEB; border: 2px solid #444; overflow: hidden; border-radius: 8px; 
    }
    canvas { width: 100%; height: 100%; display: block; }

    /* Панель управления */
    #lower-area { 
        display: flex; justify-content: space-between; align-items: center; 
        background: #2a2a2a; padding: 15px; margin-top: 10px; 
        border-radius: 12px; border: 1px solid #444; 
    }

    #fireBtn { 
        width: 90px; height: 90px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: none; font-weight: bold; font-size: 14px; 
        box-shadow: 0 5px #b33030; cursor: pointer; -webkit-tap-highlight-color: transparent;
    }

    #hp-zone { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 5px; }
    #hp-bar-container { width: 130px; height: 16px; background: #444; border-radius: 8px; overflow: hidden; border: 1px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }

    /* Джойстик в углу */
    #joystick-zone { width: 110px; height: 110px; background: rgba(255,255,255,0.05); border-radius: 50%; }
    
    .btn-mode { background: #444; color: white; border: 1px solid #666; padding: 4px 8px; border-radius: 4px; font-size: 9px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }

    #win-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 100;
    }
</style>

<div id="top-bar">
    <div style="display:flex; gap:3px;">
        <button id="limit-1" class="btn-mode">ДО 1</button>
        <button id="limit-5" class="btn-mode active-mode">ДО 5</button>
        <button id="limit-10" class="btn-mode">ДО 10</button>
    </div>
    <div style="display:flex; gap:3px;">
        <button id="mode-ai-easy" class="btn-mode active-mode">КУРСАНТ</button>
        <button id="mode-ai-hard" class="btn-mode">АС</button>
    </div>
    <div style="font-size: 14px; font-weight: bold;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
</div>

<div id="viewport-container">
    <div id="viewport">
        <canvas id="gameCanvas" width="1200" height="700"></canvas>
        <div id="win-overlay">
            <h1 id="win-text">ПОБЕДА!</h1>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px;">ИГРАТЬ СНОВА</button>
        </div>
    </div>
</div>

<div id="lower-area">
    <button id="fireBtn">ОГОНЬ</button>
    <div id="hp-zone">
        <div style="font-size: 10px; color: #aaa;">HP PILOT</div>
        <div id="hp-bar-container"><div id="hp-fill"></div></div>
    </div>
    <div id="joystick-zone"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 3000, h: 2000 };
    
    let difficulty = 'easy';
    let scoreLimit = 5;
    let gameOver = false;
    let bullets = [];
    let particles = [];
    let clouds = [];
    
    for(let i=0; i<15; i++) clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.5 + Math.random(), op: 0.3 + Math.random()*0.4 });

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, color: '#00d2ff', state: 'alive' };

    // Настройка режимов
    document.getElementById('limit-1').onclick = () => setLimit(1, 'limit-1');
    document.getElementById('limit-5').onclick = () => setLimit(5, 'limit-5');
    document.getElementById('limit-10').onclick = () => setLimit(10, 'limit-10');
    
    function setLimit(num, id) {
        scoreLimit = num;
        ['limit-1', 'limit-5', 'limit-10'].forEach(b => document.getElementById(b).classList.remove('active-mode'));
        document.getElementById(id).classList.add('active-mode');
    }

    document.getElementById('mode-ai-easy').onclick = () => { difficulty='easy'; toggleAI('mode-ai-easy'); };
    document.getElementById('mode-ai-hard').onclick = () => { difficulty='hard'; toggleAI('mode-ai-hard'); };

    function toggleAI(id) {
        ['mode-ai-easy', 'mode-ai-hard'].forEach(b => document.getElementById(b).classList.remove('active-mode'));
        document.getElementById(id).classList.add('active-mode');
    }

    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {right:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = () => { if(!gameOver && me.state === 'alive') bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' }); };
    document.getElementById('fireBtn').ontouchstart = (e) => { e.preventDefault(); fire(); };
    document.getElementById('fireBtn').onclick = fire;

    function createPart(x, y, type) {
        for(let i=0; i<(type==='fire'?4:1); i++) particles.push({ x, y, vx:(Math.random()-0.5)*3, vy:(Math.random()-0.5)*3, life:1.0, type });
    }

    function checkWin() {
        if(me.score >= scoreLimit || opp.score >= scoreLimit) {
            gameOver = true;
            document.getElementById('win-overlay').style.display = 'flex';
            document.getElementById('win-text').innerText = me.score >= scoreLimit ? "ВЫ ПОБЕДИЛИ!" : "БОТ ПОБЕДИЛ!";
            document.getElementById('win-text').style.color = me.score >= scoreLimit ? "#ff4b4b" : "#00d2ff";
        }
    }

    function update() {
        if(gameOver) return;
        clouds.forEach(c => { c.x -= 0.6 * c.s; if(c.x < -200) c.x = WORLD.w + 200; });

        // Me
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*6.5; me.y += Math.sin(r)*6.5;
            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { me.state = 'falling'; me.dt = 120; opp.score++; checkWin(); }
        } else {
            me.y += 8; me.a += 12; createPart(me.x, me.y, 'fire');
            if(--me.dt <= 0 && !gameOver) { me.state='alive'; me.hp=5; me.x=Math.random()*1000; me.y=Math.random()*1000; }
        }

        // AI
        if(opp.state === 'alive') {
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * (difficulty==='hard' ? 0.08 : 0.04);
            let r = opp.a * Math.PI/180;
            opp.x += Math.cos(r)*(difficulty==='hard'?7:5);
            opp.y += Math.sin(r)*(difficulty==='hard'?7:5);
            if(opp.hp < 3) createPart(opp.x, opp.y, 'smoke');
            if(Math.random() < (difficulty==='hard'?0.05:0.02) && Math.abs(diff) < 25) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
            if(opp.hp <= 0) { opp.state = 'falling'; opp.dt = 120; me.score++; checkWin(); }
        } else {
            opp.y += 8; createPart(opp.x, opp.y, 'fire');
            if(--opp.dt <= 0 && !gameOver) { opp.state='alive'; opp.hp=5; opp.x=2500; opp.y=1500; }
        }

        particles.forEach((p, i) => { p.life -= 0.03; if(p.life <= 0) particles.splice(i, 1); else { p.x+=p.vx; p.y+=p.vy; } });
        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180;
            b.x += Math.cos(r)*18; b.y += Math.sin(r)*18;
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 60) {
                target.hp--; bullets.splice(i, 1);
            }
            if(b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) bullets.splice(i, 1);
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(canvas.width / WORLD.w, canvas.height / WORLD.h);
        clouds.forEach(c => { ctx.globalAlpha = c.op; ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(c.x, c.y, 50*c.s, 0, 7); ctx.fill(); });
        ctx.globalAlpha = 1.0;
        particles.forEach(p => {
            ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${150*p.life}, 0, ${p.life})` : `rgba(80,80,80,${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='fire'?12:15, 0, 7); ctx.fill();
        });
        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-15, -65, 30, 130); ctx.fillStyle = "#333"; ctx.fillRect(-55, -15, 110, 30);
            ctx.restore();
        };
        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 14, 0, 7); ctx.fill(); });
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