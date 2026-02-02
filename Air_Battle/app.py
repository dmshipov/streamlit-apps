import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Fullscreen", layout="wide")
st.markdown("""
    <style>
    .main .block-container { padding: 0; max-width: 100%; }
    iframe { display: block; border: none; width: 100vw; height: 100vh; }
    body { overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 0; background: #000; font-family: 'Segoe UI', sans-serif; overflow: hidden; color: white; touch-action: none; }
    
    #top-bar { 
        position: absolute; top: 10px; left: 10px; right: 10px;
        background: rgba(0, 0, 0, 0.5); padding: 12px; border-radius: 12px; 
        display: flex; justify-content: space-between; align-items: center; 
        z-index: 50; backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.1);
    }

    #viewport { position: relative; width: 100vw; height: 100vh; background: #5d8aa8; overflow: hidden; }
    canvas { display: block; width: 100vw; height: 100vh; }

    #controls-container {
        position: absolute; bottom: 30px; left: 0; width: 100%; height: 140px;
        pointer-events: none; z-index: 100;
    }

    #fireBtn { 
        position: absolute; left: 40px; bottom: 10px;
        width: 80px; height: 80px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: 4px solid #b33030; font-weight: bold; font-size: 14px; 
        box-shadow: 0 4px #800; cursor: pointer; pointer-events: auto;
        -webkit-tap-highlight-color: transparent;
    }

    #joystick-wrapper {
        position: absolute; right: 40px; bottom: 10px;
        width: 120px; height: 120px; pointer-events: auto;
    }

    #hp-center {
        position: absolute; left: 50%; bottom: 20px; transform: translateX(-50%);
        display: flex; flex-direction: column; align-items: center; gap: 5px;
    }
    #hp-bar-container { width: 140px; height: 10px; background: #222; border-radius: 5px; overflow: hidden; border: 1px solid #fff; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.2s; }

    #win-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 200;
    }
    #result-card { text-align: center; border: 2px solid #fff; padding: 40px; border-radius: 15px; background: #111; }

    #round-announcer {
        position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
        font-size: 40px; font-weight: bold; color: #fff; text-shadow: 2px 2px #000;
        pointer-events: none; display: none; z-index: 150; text-align: center;
    }
</style>

<div id="top-bar">
    <div id="round-display" style="font-weight: bold;">РАУНД: 1</div>
    <div style="font-size: 20px; font-weight: bold;">
        <span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span>
    </div>
    <div style="font-size: 10px; opacity: 0.7;">ЦЕЛЬ: 3 ПОБЕДЫ</div>
</div>

<div id="viewport">
    <div id="round-announcer"></div>
    <canvas id="gameCanvas"></canvas>
    
    <div id="win-overlay">
        <div id="result-card">
            <h1 id="win-text" style="font-size: 40px;">ПОБЕДА!</h1>
            <p id="final-score"></p>
            <button onclick="location.reload()" style="padding: 12px 30px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">ИГРАТЬ СНОВА</button>
        </div>
    </div>

    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="hp-center">
            <div style="font-size: 10px; font-weight: bold;">ВАШ САМОЛЕТ</div>
            <div id="hp-bar-container"><div id="hp-fill"></div></div>
        </div>
        <div id="joystick-wrapper"><div id="joystick-zone"></div></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    let W, H;
    
    function resize() {
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W;
        canvas.height = H;
    }
    window.onresize = resize;
    resize();

    let scoreLimit = 3;
    let gameOver = false;
    let currentRound = 1;
    let isRoundTransition = false;
    let bullets = [], particles = [], clouds = [];
    
    for(let i=0; i<30; i++) clouds.push({ x: Math.random()*W, y: Math.random()*H, s: 0.5 + Math.random(), op: 0.2 + Math.random()*0.3 });

    let me = { x: 0, y: 0, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 0, y: 0, a: 180, hp: 5, color: '#00d2ff', state: 'alive' };

    resetPositions();

    const joy = nipplejs.create({
        zone: document.getElementById('joystick-zone'),
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: 'white',
        size: 100
    });

    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = () => { if(!gameOver && !isRoundTransition && me.state === 'alive') bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' }); };
    document.getElementById('fireBtn').onclick = fire;

    function createPart(x, y, type) {
        let count = type === 'fire' ? 3 : 1;
        for(let i=0; i<count; i++) {
            particles.push({ x, y, vx:(Math.random()-0.5)*3, vy:(Math.random()-0.5)*3, life:1.0, type });
        }
    }

    function resetPositions() {
        me.x = W * 0.15; me.y = H * 0.5; me.a = 0; me.hp = 5; me.state = 'alive';
        opp.x = W * 0.85; opp.y = H * 0.5; opp.a = 180; opp.hp = 5; opp.state = 'alive';
        bullets = [];
    }

    function startNextRound(winner) {
        isRoundTransition = true;
        const announcer = document.getElementById('round-announcer');
        announcer.innerHTML = winner === 'me' ? "<span style='color:#00ff00'>РАУНД ЗА ВАМИ!</span>" : "<span style='color:#ff4b4b'>РАУНД ЗА ВРАГОМ!</span>";
        announcer.style.display = 'block';

        setTimeout(() => {
            if (me.score >= scoreLimit || opp.score >= scoreLimit) {
                endGame(me.score >= scoreLimit);
            } else {
                currentRound++;
                document.getElementById('round-display').innerText = `РАУНД: ${currentRound}`;
                announcer.style.display = 'none';
                resetPositions();
                isRoundTransition = false;
            }
        }, 2000);
    }

    function update() {
        if(gameOver || isRoundTransition) return;
        
        clouds.forEach(c => { c.x -= 0.5 * c.s; if(c.x < -150) c.x = W + 150; });

        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*5; me.y += Math.sin(r)*5;
            if(me.x < 0) me.x = W; if(me.x > W) me.x = 0;
            if(me.y < 0) me.y = H; if(me.y > H) me.y = 0;
            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { me.state = 'falling'; opp.score++; startNextRound('opp'); }
        }

        if(opp.state === 'alive') {
            let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
            let diff = targetA - opp.a;
            while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
            opp.a += diff * 0.05;
            let r = opp.a * Math.PI/180;
            opp.x += Math.cos(r)*4.5; opp.y += Math.sin(r)*4.5;
            if(opp.x < 0) opp.x = W; if(opp.x > W) opp.x = 0;
            if(opp.y < 0) opp.y = H; if(opp.y > H) opp.y = 0;
            if(Math.random() < 0.02 && Math.abs(diff) < 20) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
            if(opp.hp <= 0) { opp.state = 'falling'; me.score++; startNextRound('me'); }
        }

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180; b.x += Math.cos(r)*12; b.y += Math.sin(r)*12;
            if(b.x < 0 || b.x > W || b.y < 0 || b.y > H) { bullets.splice(i, 1); return; }
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 30) {
                target.hp--; bullets.splice(i, 1);
            }
        });

        particles.forEach((p, i) => { p.life -= 0.03; if(p.life <= 0) particles.splice(i, 1); else { p.x+=p.vx; p.y+=p.vy; } });
    }

    function endGame(win) {
        gameOver = true;
        document.getElementById('win-overlay').style.display = 'flex';
        document.getElementById('win-text').innerText = win ? "ПОБЕДИТЕЛЬ БИТВЫ!" : "ВЫ СБИТЫ!";
        document.getElementById('win-text').style.color = win ? "#00ff00" : "#ff4b4b";
        document.getElementById('final-score').innerText = `ИТОГ: ${me.score} - ${opp.score}`;
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);
        clouds.forEach(c => { ctx.globalAlpha = c.op; ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(c.x, c.y, 40*c.s, 0, 7); ctx.fill(); });
        ctx.globalAlpha = 1.0;

        particles.forEach(p => {
            ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${200*p.life}, 0, ${p.life})` : `rgba(255,255,255,${p.life*0.5})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='fire'?5:8, 0, 7); ctx.fill();
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-12, -25, 24, 50); 
            ctx.fillStyle = "#333"; ctx.fillRect(-40, -5, 80, 15);
            ctx.fillRect(-15, 20, 30, 8);
            ctx.restore();
        };

        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 4, 0, 7); ctx.fill(); });

        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=1000)