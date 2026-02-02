import streamlit as st
import streamlit.components.v1 as components

# Настройка страницы для максимального заполнения
st.set_page_config(page_title="AN-2 Ace Combat: Fullscreen", layout="wide")
st.markdown("""
    <style>
    .main .block-container { padding: 0; max-width: 100%; }
    iframe { display: block; border: none; }
    </style>
    """, unsafe_allow_html=True)

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 0; background: #111; font-family: 'Segoe UI', sans-serif; overflow: hidden; color: white; touch-action: none; }
    
    #top-bar { 
        position: absolute; top: 10px; left: 10px; right: 10px;
        background: rgba(0, 0, 0, 0.6); padding: 10px; border-radius: 12px; 
        display: flex; justify-content: space-between; align-items: center; 
        z-index: 50; backdrop-filter: blur(5px);
    }

    #viewport { position: relative; width: 100vw; height: 100vh; background: #87CEEB; overflow: hidden; }
    canvas { display: block; }

    #controls-container {
        position: absolute; bottom: 30px; left: 0; width: 100%; height: 140px;
        pointer-events: none; z-index: 100;
    }

    #fireBtn { 
        position: absolute; left: 40px; bottom: 10px;
        width: 100px; height: 100px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: 5px solid #b33030; font-weight: bold; font-size: 16px; 
        box-shadow: 0 6px #800; cursor: pointer; pointer-events: auto;
        -webkit-tap-highlight-color: transparent;
    }

    #joystick-wrapper {
        position: absolute; right: 40px; bottom: 10px;
        width: 130px; height: 130px; pointer-events: auto;
    }

    #hp-center {
        position: absolute; left: 50%; bottom: 10px; transform: translateX(-50%);
        display: flex; flex-direction: column; align-items: center; gap: 5px;
    }
    #hp-bar-container { width: 150px; height: 16px; background: #333; border-radius: 8px; overflow: hidden; border: 2px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.2s; }

    .btn-mode { background: #444; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 10px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }

    #win-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 200;
    }
    #result-card {
        background: #222; padding: 40px; border-radius: 20px; border: 4px solid #fff;
        text-align: center; box-shadow: 0 0 50px rgba(0,0,0,0.5);
    }
</style>

<div id="top-bar">
    <div style="display:flex; gap:5px;">
        <button id="limit-1" class="btn-mode">ДО 1</button>
        <button id="limit-5" class="btn-mode active-mode">ДО 5</button>
        <button id="limit-10" class="btn-mode">ДО 10</button>
    </div>
    <div style="font-size: 22px; font-weight: bold; letter-spacing: 2px;">
        <span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span>
    </div>
</div>

<div id="viewport">
    <canvas id="gameCanvas"></canvas>
    
    <div id="win-overlay">
        <div id="result-card">
            <h1 id="win-text" style="font-size: 48px; margin-bottom: 20px;">ПОБЕДА!</h1>
            <p id="final-score" style="font-size: 20px; margin-bottom: 30px;"></p>
            <button onclick="location.reload()" style="padding: 15px 40px; background: #28a745; color: white; border: none; border-radius: 10px; font-size: 20px; font-weight: bold; cursor: pointer;">В БОЙ!</button>
        </div>
    </div>

    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="hp-center">
            <div style="font-size: 12px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px #000;">ПИЛОТ: HP</div>
            <div id="hp-bar-container"><div id="hp-fill"></div></div>
        </div>
        <div id="joystick-wrapper"><div id="joystick-zone"></div></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    let WORLD = { w: window.innerWidth, h: window.innerHeight };
    
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        WORLD.w = canvas.width;
        WORLD.h = canvas.height;
    }
    window.onresize = resize;
    resize();

    let scoreLimit = 5;
    let gameOver = false;
    let bullets = [], particles = [], clouds = [];
    
    for(let i=0; i<20; i++) clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.8 + Math.random(), op: 0.3 + Math.random()*0.3 });

    let me = { x: 200, y: 200, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: WORLD.w - 200, y: WORLD.h - 200, a: 180, hp: 5, color: '#00d2ff', state: 'alive' };

    const joy = nipplejs.create({
        zone: document.getElementById('joystick-zone'),
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: 'white',
        size: 110
    });

    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = () => { if(!gameOver && me.state === 'alive') bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' }); };
    document.getElementById('fireBtn').addEventListener('touchstart', (e) => { e.preventDefault(); fire(); });
    document.getElementById('fireBtn').onclick = fire;

    function createPart(x, y, type) {
        let count = type === 'fire' ? 5 : 1;
        for(let i=0; i<count; i++) {
            particles.push({ x, y, vx:(Math.random()-0.5)*4, vy:(Math.random()-0.5)*4, life:1.0, type });
        }
    }

    function update() {
        if(gameOver) return;
        
        clouds.forEach(c => { c.x -= 0.7 * c.s; if(c.x < -200) c.x = WORLD.w + 200; });

        // Игрок
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*7; me.y += Math.sin(r)*7;
            if(me.x < 0) me.x = WORLD.w; if(me.x > WORLD.w) me.x = 0;
            if(me.y < 0) me.y = WORLD.h; if(me.y > WORLD.h) me.y = 0;
            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { 
                me.state = 'falling'; me.dt = 120; opp.score++; 
                if(opp.score >= scoreLimit) endGame(false); 
            }
        } else {
            me.y += 6; me.a += 10; createPart(me.x, me.y, 'fire');
            if(--me.dt <= 0) { me.state='alive'; me.hp=5; me.x=Math.random()*WORLD.w; me.y=Math.random()*WORLD.h; }
        }

        // Бот
        if(opp.state === 'alive') {
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * 0.06;
            let r = opp.a * Math.PI/180;
            opp.x += Math.cos(r)*6; opp.y += Math.sin(r)*6;
            if(opp.x < 0) opp.x = WORLD.w; if(opp.x > WORLD.w) opp.x = 0;
            if(opp.y < 0) opp.y = WORLD.h; if(opp.y > WORLD.h) opp.y = 0;
            if(Math.random() < 0.03 && Math.abs(diff) < 30) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
            if(opp.hp <= 0) { 
                opp.state = 'falling'; opp.dt = 120; me.score++; 
                if(me.score >= scoreLimit) endGame(true); 
            }
        } else {
            opp.y += 6; createPart(opp.x, opp.y, 'fire');
            if(--opp.dt <= 0) { opp.state='alive'; opp.hp=5; opp.x=Math.random()*WORLD.w; opp.y=Math.random()*WORLD.h; }
        }

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180; b.x += Math.cos(r)*18; b.y += Math.sin(r)*18;
            if(b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) { bullets.splice(i, 1); return; }
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 50) {
                target.hp--; bullets.splice(i, 1);
            }
        });

        particles.forEach((p, i) => { p.life -= 0.02; if(p.life <= 0) particles.splice(i, 1); else { p.x+=p.vx; p.y+=p.vy; } });
    }

    function endGame(win) {
        gameOver = true;
        document.getElementById('win-overlay').style.display = 'flex';
        const winText = document.getElementById('win-text');
        winText.innerText = win ? "ПОБЕДА В КОНУ!" : "ВЫ ПРОИГРАЛИ!";
        winText.style.color = win ? "#28a745" : "#ff4b4b";
        document.getElementById('final-score').innerText = `Счёт боя: ${me.score} - ${opp.score}`;
        document.getElementById('result-card').style.borderColor = win ? "#28a745" : "#ff4b4b";
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        clouds.forEach(c => { ctx.globalAlpha = c.op; ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(c.x, c.y, 70*c.s, 0, 7); ctx.fill(); });
        ctx.globalAlpha = 1.0;

        particles.forEach(p => {
            ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${150*p.life}, 0, ${p.life})` : `rgba(60,60,60,${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='fire'?10:15, 0, 7); ctx.fill();
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            // Фюзеляж (чуть больше)
            ctx.fillStyle = col; ctx.fillRect(-25, -80, 50, 160); 
            // Крылья
            ctx.fillStyle = "#222"; ctx.fillRect(-70, -25, 140, 50);
            ctx.restore();
        };

        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 8, 0, 7); ctx.fill(); });

        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=800)