import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Tactical VFX", layout="wide")

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

    /* Оверлей победы */
    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.7); display: none; flex-direction: column;
        justify-content: center; align-items: center; z-index: 100; border-radius: 8px;
    }
    #overlay h2 { font-size: 40px; margin: 0; text-shadow: 0 0 10px red; }

    #lower-area { 
        display: flex; justify-content: space-between; align-items: flex-end; 
        background: #2a2a2a; padding: 15px; margin-top: 10px; border-radius: 12px; border: 1px solid #444; 
    }

    #fire-zone { flex: 1; display: flex; justify-content: flex-start; }
    #fireBtn { 
        width: 90px; height: 90px; border-radius: 50%; background: #ff4b4b; 
        color: white; border: none; font-weight: bold; font-size: 14px; 
        box-shadow: 0 5px #b33030; cursor: pointer; -webkit-tap-highlight-color: transparent;
        user-select: none; -webkit-user-select: none;
    }
    #fireBtn:active { transform: translateY(3px); box-shadow: 0 2px #b33030; }

    #hp-zone { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 5px; padding-bottom: 10px; }
    #hp-bar-container { width: 130px; height: 16px; background: #444; border-radius: 8px; overflow: hidden; border: 1px solid #000; }
    #hp-fill { width: 100%; height: 100%; background: #28a745; transition: 0.3s; }
    .hp-label { font-size: 10px; color: #aaa; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }

    #joy-zone { flex: 1; display: flex; justify-content: flex-end; align-items: flex-end; }
    #joystick-zone { width: 110px; height: 110px; background: rgba(255,255,255,0.05); border-radius: 50%; position: relative; }

    .btn-mode { background: #444; color: white; border: 1px solid #666; padding: 4px 8px; border-radius: 4px; font-size: 9px; cursor: pointer;}
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }
</style>

<div id="top-bar">
    <div style="display:flex; flex-direction: column; gap:2px;">
        <div style="display:flex; gap:5px;">
            <button id="mode-ai-easy" class="btn-mode active-mode">КУРСАНТ</button>
            <button id="mode-ai-hard" class="btn-mode">АС</button>
            <button id="mode-net" class="btn-mode">СЕТЬ</button>
        </div>
        <div style="display:flex; gap:5px; margin-top:3px;">
            <button id="lim-1" class="btn-mode">ДО 1</button>
            <button id="lim-5" class="btn-mode active-mode">ДО 5</button>
            <button id="lim-10" class="btn-mode">ДО 10</button>
        </div>
    </div>
    
    <div id="net-controls" style="display: none; gap: 4px;">
        <input type="text" id="remote-id" placeholder="ID" style="width: 40px; font-size: 9px;">
        <button id="connect-btn" style="background:#28a745; color:white; border:none; padding:2px 5px;">OK</button>
    </div>

    <div style="text-align: center;">
        <div style="font-size: 10px; color: #aaa;">РАУНДЫ</div>
        <div style="font-size: 16px; font-weight: bold; color: #fbff00;"><span id="wins-me">0</span> : <span id="wins-opp">0</span></div>
    </div>

    <div style="text-align: right;">
        <div style="font-size: 10px;">ID: <span id="my-peer-id" style="color:#00d2ff">...</span></div>
        <div style="font-size: 18px; font-weight: bold;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
    </div>
</div>

<div id="viewport-container">
    <div id="viewport">
        <canvas id="gameCanvas" width="1200" height="700"></canvas>
        <div id="overlay">
            <h2 id="result-text">ПОБЕДА!</h2>
            <p>Следующий раунд через 3 сек...</p>
        </div>
    </div>
</div>

<div id="lower-area">
    <div id="fire-zone"><button id="fireBtn">ОГОНЬ</button></div>
    <div id="hp-zone">
        <div class="hp-label">HP PILOT</div>
        <div id="hp-bar-container"><div id="hp-fill"></div></div>
    </div>
    <div id="joy-zone"><div id="joystick-zone"></div></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>
<script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 3000, h: 2000 };
    
    let isSolo = true;
    let difficulty = 'easy';
    let scoreLimit = 5;
    let gameActive = true;
    let totalWinsMe = 0;
    let totalWinsOpp = 0;

    let bullets = [];
    let particles = [];
    let clouds = [];
    
    for(let i=0; i<15; i++) {
        clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.5 + Math.random(), op: 0.3 + Math.random()*0.4 });
    }

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, max: 5, score: 0, color: '#00d2ff', state: 'alive' };

    function updateUI(mode) {
        document.querySelectorAll('#mode-ai-easy, #mode-ai-hard, #mode-net').forEach(b => b.classList.remove('active-mode'));
        document.getElementById('net-controls').style.display = (mode === 'net') ? 'flex' : 'none';
        if(mode === 'easy') document.getElementById('mode-ai-easy').classList.add('active-mode');
        if(mode === 'hard') document.getElementById('mode-ai-hard').classList.add('active-mode');
        if(mode === 'net') document.getElementById('mode-net').classList.add('active-mode');
    }

    function setLimit(val) {
        scoreLimit = val;
        document.querySelectorAll('[id^="lim-"]').forEach(b => b.classList.remove('active-mode'));
        document.getElementById('lim-'+val).classList.add('active-mode');
        resetMatch();
    }

    document.getElementById('lim-1').onclick = () => setLimit(1);
    document.getElementById('lim-5').onclick = () => setLimit(5);
    document.getElementById('lim-10').onclick = () => setLimit(10);

    document.getElementById('mode-ai-easy').onclick = () => { isSolo=true; difficulty='easy'; updateUI('easy'); resetMatch(); };
    document.getElementById('mode-ai-hard').onclick = () => { isSolo=true; difficulty='hard'; updateUI('hard'); resetMatch(); };
    document.getElementById('mode-net').onclick = () => { isSolo=false; updateUI('net'); resetMatch(); };

    let peer = new Peer();
    let conn = null;
    peer.on('open', id => document.getElementById('my-peer-id').innerText = id);
    peer.on('connection', c => { conn = c; isSolo = false; updateUI('net'); setupConn(); });
    document.getElementById('connect-btn').onclick = () => { conn = peer.connect(document.getElementById('remote-id').value); setupConn(); };

    function setupConn() {
        conn.on('data', d => {
            if(d.t === 's') { 
                opp.x = d.x; opp.y = d.y; opp.a = d.a; opp.hp = d.hp; 
                opp.state = d.state; opp.score = d.score;
            }
            if(d.t === 'f') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
        });
    }

    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = (e) => {
        if(e) { e.preventDefault(); e.stopPropagation(); }
        if(!gameActive || me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ t: 'f', x: me.x, y: me.y, a: me.a });
    };

    // Мультитач поддержка
    const fBtn = document.getElementById('fireBtn');
    fBtn.addEventListener('touchstart', fire, {passive: false});
    fBtn.addEventListener('mousedown', (e) => { if(!('ontouchstart' in window)) fire(e); });

    function resetMatch() {
        me.score = 0; opp.score = 0;
        gameActive = true;
        document.getElementById('overlay').style.display = 'none';
        respawn(me); respawn(opp);
    }

    function respawn(p) {
        p.hp = 5; p.state = 'alive';
        if(p === me) { p.x = 500; p.y = 500; p.a = 0; }
        else { p.x = 2500; p.y = 1500; p.a = 180; }
    }

    function checkWin() {
        if(!gameActive) return;
        let winner = null;
        if(me.score >= scoreLimit) winner = "ME";
        if(opp.score >= scoreLimit) winner = "OPP";

        if(winner) {
            gameActive = false;
            const overlay = document.getElementById('overlay');
            const resTxt = document.getElementById('result-text');
            overlay.style.display = 'flex';
            
            if(winner === "ME") {
                resTxt.innerText = "ПОБЕДА В РАУНДЕ!";
                resTxt.style.color = "#00ff00";
                totalWinsMe++;
            } else {
                resTxt.innerText = "ПРОИГРЫШ!";
                resTxt.style.color = "#ff0000";
                totalWinsOpp++;
            }
            
            document.getElementById('wins-me').innerText = totalWinsMe;
            document.getElementById('wins-opp').innerText = totalWinsOpp;
            
            setTimeout(resetMatch, 3000);
        }
    }

    function createPart(x, y, type) {
        let count = type === 'fire' ? 4 : 1;
        for(let i=0; i<count; i++) {
            particles.push({ x, y, vx: (Math.random()-0.5)*3, vy: (Math.random()-0.5)*3, life: 1.0, type: type });
        }
    }

    function update() {
        if(!gameActive) return;
        
        clouds.forEach(c => { c.x -= 0.6 * c.s; if(c.x < -200) c.x = WORLD.w + 200; });

        const wrap = (obj) => {
            if (obj.x < 0) obj.x = WORLD.w; if (obj.x > WORLD.w) obj.x = 0;
            if (obj.y < 0) obj.y = WORLD.h; if (obj.y > WORLD.h) obj.y = 0;
        };

        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*6; me.y += Math.sin(r)*6;
            wrap(me);
            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { me.state = 'falling'; me.dt = 120; opp.score++; checkWin(); }
        } else if (gameActive) {
            me.y += 8; me.a += 12; createPart(me.x, me.y, 'fire');
            if(--me.dt <= 0) respawn(me);
        }

        if(isSolo) {
            if(opp.state === 'alive') {
                let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
                let diff = targetA - opp.a;
                while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
                opp.a += diff * (difficulty==='hard' ? 0.07 : 0.03);
                let r = opp.a * Math.PI/180;
                opp.x += Math.cos(r)*(difficulty==='hard'?6:4.5);
                opp.y += Math.sin(r)*(difficulty==='hard'?6:4.5);
                wrap(opp);
                if(opp.hp < 3) createPart(opp.x, opp.y, 'smoke');
                if(Math.random() < (difficulty==='hard'?0.04:0.015) && Math.abs(diff) < 20) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
                if(opp.hp <= 0) { opp.state = 'falling'; opp.dt = 120; me.score++; checkWin(); }
            } else if (gameActive) {
                opp.y += 8; createPart(opp.x, opp.y, 'fire');
                if(--opp.dt <= 0) respawn(opp);
            }
        }

        particles.forEach((p, i) => {
            p.x += p.vx; p.y += p.vy; p.life -= 0.025;
            if(p.life <= 0) particles.splice(i, 1);
        });

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180;
            b.x += Math.cos(r)*16; b.y += Math.sin(r)*16;
            if (b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) { bullets.splice(i, 1); return; }
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 55) {
                target.hp--;
                bullets.splice(i, 1);
            }
        });

        if(conn && !isSolo) conn.send({ t: 's', x: me.x, y: me.y, a: me.a, hp: me.hp, state: me.state, score: me.score });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(canvas.width / WORLD.w, canvas.height / WORLD.h);
        clouds.forEach(c => {
            ctx.globalAlpha = c.op; ctx.fillStyle = "white";
            ctx.beginPath(); ctx.arc(c.x, c.y, 45*c.s, 0, 7); ctx.arc(c.x+35*c.s, c.y-15*c.s, 40*c.s, 0, 7); ctx.fill();
        });
        ctx.globalAlpha = 1.0;
        particles.forEach(p => {
            ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${120*p.life}, 0, ${p.life})` : `rgba(70,70,70,${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='fire'?10:14, 0, 7); ctx.fill();
        });
        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-15, -65, 30, 130);
            ctx.fillStyle = "#333"; ctx.fillRect(-55, -15, 110, 30);
            ctx.restore();
        };
        drawPlane(me, me.color); drawPlane(opp, opp.color);
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 12, 0, 7); ctx.fill(); });
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