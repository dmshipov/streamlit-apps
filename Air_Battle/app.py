import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Full Field View", layout="wide")

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

    #viewport { 
        position: relative; width: 100vw; height: 100vh; 
        background: #87CEEB; overflow: hidden; 
    }
    canvas { width: 100%; height: 100%; display: block; }

    #controls-container {
        position: absolute; bottom: 20px; left: 0; width: 100%; height: 120px;
        pointer-events: none; z-index: 100;
    }

    #fireBtn { 
        position: absolute; left: 30px; bottom: 10px;
        width: 90px; height: 90px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: 4px solid #b33030; font-weight: bold; font-size: 14px; 
        box-shadow: 0 5px #000; cursor: pointer; pointer-events: auto;
        -webkit-tap-highlight-color: transparent;
    }

    #joystick-wrapper {
        position: absolute; right: 30px; bottom: 10px;
        width: 120px; height: 120px; pointer-events: auto;
    }

    #hp-center {
        position: absolute; left: 50%; bottom: 20px; transform: translateX(-50%);
        display: flex; flex-direction: column; align-items: center; gap: 5px;
    }
    #hp-bar-container { width: 120px; height: 12px; background: #444; border-radius: 6px; overflow: hidden; border: 1px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }

    .btn-mode { background: #444; color: white; border: 1px solid #666; padding: 4px 8px; border-radius: 4px; font-size: 9px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }

    #win-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 200;
    }
</style>

<div id="top-bar">
    <div style="display:flex; gap:3px;">
        <button id="limit-1" class="btn-mode">ДО 1</button>
        <button id="limit-5" class="btn-mode active-mode">ДО 5</button>
        <button id="limit-10" class="btn-mode">ДО 10</button>
        <button id="mode-ai-hard" class="btn-mode">РЕЖИМ: АС</button>
    </div>
    <div style="font-size: 16px; font-weight: bold;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
</div>

<div id="viewport">
    <canvas id="gameCanvas"></canvas>
    <div id="win-overlay">
        <h1 id="win-text">ПОБЕДА!</h1>
        <button onclick="location.reload()" style="padding: 15px 30px; background: #28a745; color: white; border: none; border-radius: 8px; font-size: 18px;">ИГРАТЬ СНОВА</button>
    </div>

    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="hp-center">
            <div style="font-size: 10px; color: #fff; text-shadow: 1px 1px 2px #000;">HP PILOT</div>
            <div id="hp-bar-container"><div id="hp-fill"></div></div>
        </div>
        <div id="joystick-wrapper"><div id="joystick-zone"></div></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>

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

    let difficulty = 'hard';
    let scoreLimit = 5;
    let gameOver = false;
    let bullets = [];
    let particles = [];
    let clouds = [];
    
    for(let i=0; i<15; i++) clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.5 + Math.random(), op: 0.2 + Math.random()*0.3 });

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, color: '#00d2ff', state: 'alive' };

    const setLimit = (n, id) => {
        scoreLimit = n;
        ['limit-1', 'limit-5', 'limit-10'].forEach(b => document.getElementById(b).classList.remove('active-mode'));
        document.getElementById(id).classList.add('active-mode');
    };
    document.getElementById('limit-1').onclick = () => setLimit(1, 'limit-1');
    document.getElementById('limit-5').onclick = () => setLimit(5, 'limit-5');
    document.getElementById('limit-10').onclick = () => setLimit(10, 'limit-10');

    document.getElementById('mode-ai-hard').onclick = function() {
        difficulty = (difficulty === 'easy' ? 'hard' : 'easy');
        this.innerText = difficulty === 'hard' ? "РЕЖИМ: АС" : "РЕЖИМ: КУРСАНТ";
        this.classList.toggle('active-mode');
    };

    const joy = nipplejs.create({
        zone: document.getElementById('joystick-zone'),
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: 'white',
        size: 100
    });

    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = () => { if(!gameOver && me.state === 'alive') bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' }); };
    document.getElementById('fireBtn').ontouchstart = (e) => { e.preventDefault(); fire(); };
    document.getElementById('fireBtn').onclick = fire;

    function createPart(x, y, type) {
        for(let i=0; i<(type==='fire'?3:1); i++) particles.push({ x, y, vx:(Math.random()-0.5)*3, vy:(Math.random()-0.5)*3, life:1.0, type });
    }

    function update() {
        if(gameOver) return;
        clouds.forEach(c => { c.x -= 0.5 * c.s; if(c.x < -200) c.x = WORLD.w + 200; });

        // Me Logic
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*6.5; me.y += Math.sin(r)*6.5;
            
            if(me.x < 0) me.x = WORLD.w; if(me.x > WORLD.w) me.x = 0;
            if(me.y < 0) me.y = WORLD.h; if(me.y > WORLD.h) me.y = 0;

            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { me.state = 'falling'; me.dt = 120; opp.score++; if(opp.score>=scoreLimit) endGame(false); }
        } else {
            me.y += 8; me.a += 15; createPart(me.x, me.y, 'fire');
            if(--me.dt <= 0) { me.state='alive'; me.hp=5; me.x=Math.random()*WORLD.w; me.y=Math.random()*WORLD.h; }
        }

        // AI Logic
        if(opp.state === 'alive') {
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * (difficulty === 'hard' ? 0.08 : 0.04);
            let r = opp.a * Math.PI/180;
            opp.x += Math.cos(r)*(difficulty === 'hard' ? 7.5 : 5);
            opp.y += Math.sin(r)*(difficulty === 'hard' ? 7.5 : 5);

            if(opp.x < 0) opp.x = WORLD.w; if(opp.x > WORLD.w) opp.x = 0;
            if(opp.y < 0) opp.y = WORLD.h; if(opp.y > WORLD.h) opp.y = 0;

            if(opp.hp < 3) createPart(opp.x, opp.y, 'smoke');
            if(Math.random() < (difficulty === 'hard' ? 0.05 : 0.02) && Math.abs(diff) < 25) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
            if(opp.hp <= 0) { opp.state = 'falling'; opp.dt = 120; me.score++; if(me.score>=scoreLimit) endGame(true); }
        } else {
            opp.y += 8; createPart(opp.x, opp.y, 'fire');
            if(--opp.dt <= 0) { opp.state='alive'; opp.hp=5; opp.x=WORLD.w-500; opp.y=WORLD.h-500; }
        }

        particles.forEach((p, i) => { p.life -= 0.03; if(p.life <= 0) particles.splice(i, 1); else { p.x+=p.vx; p.y+=p.vy; } });
        
        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i];
            let r = b.a * Math.PI/180;
            b.x += Math.cos(r)*20; 
            b.y += Math.sin(r)*20;
            
            // ПУЛИ УДАЛЯЮТСЯ ПРИ ВЫХОДЕ ЗА ГРАНИЦЫ
            if(b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) {
                bullets.splice(i, 1);
                continue;
            }

            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 60) {
                target.hp--; 
                bullets.splice(i, 1);
            }
        }
    }

    function endGame(win) {
        gameOver = true;
        document.getElementById('win-overlay').style.display = 'flex';
        document.getElementById('win-text').innerText = win ? "ПОБЕДА!" : "ВЫ СБИТЫ!";
        document.getElementById('win-text').style.color = win ? "#00ff00" : "#ff4b4b";
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        
        let scale = Math.min(canvas.width / WORLD.w, canvas.height / WORLD.h);
        ctx.scale(scale, scale);
        ctx.translate((canvas.width/scale - WORLD.w)/2, (canvas.height/scale - WORLD.h)/2);

        clouds.forEach(c => { ctx.globalAlpha = c.op; ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(c.x, c.y, 60*c.s, 0, 7); ctx.fill(); });
        ctx.globalAlpha = 1.0;

        particles.forEach(p => {
            ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${200*p.life}, 0, ${p.life})` : `rgba(80,80,80,${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='fire'?15:20, 0, 7); ctx.fill();
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-20, -70, 40, 140); 
            ctx.fillStyle = "#333"; ctx.fillRect(-60, -20, 120, 40);
            ctx.restore();
        };
        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 15, 0, 7); ctx.fill(); });
        
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