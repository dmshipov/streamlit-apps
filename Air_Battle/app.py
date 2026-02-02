import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Multi-Touch & Shake", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 0; background: #111; font-family: sans-serif; overflow: hidden; color: white; touch-action: none; }
    #viewport { position: relative; width: 100vw; height: 100vh; background: #87CEEB; overflow: hidden; }
    canvas { width: 100%; height: 100%; display: block; }

    /* Панель управления */
    #controls-container { 
        position: absolute; bottom: 0; left: 0; width: 100%; height: 200px; 
        pointer-events: none; z-index: 100; 
    }
    
    #fireBtn { 
        position: absolute; left: 40px; bottom: 40px;
        width: 100px; height: 100px; border-radius: 50%; background: rgba(255, 75, 75, 0.8); 
        color: white; border: 4px solid #b33030; font-weight: bold; font-size: 16px; 
        pointer-events: auto; touch-action: none;
    }
    
    #joystick-wrapper { 
        position: absolute; right: 40px; bottom: 40px; 
        width: 150px; height: 150px; pointer-events: auto; touch-action: none;
    }

    #top-bar { 
        position: absolute; top: 10px; left: 10px; right: 10px;
        background: rgba(34, 34, 34, 0.8); padding: 8px; border-radius: 8px; 
        display: flex; justify-content: space-between; z-index: 50; 
    }
</style>

<div id="top-bar">
    <div style="font-size: 18px; font-weight: bold;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
    <div style="color: #eee; font-size: 12px;">Мультитач активен 📱</div>
</div>

<div id="viewport">
    <canvas id="gameCanvas"></canvas>
    <div id="controls-container">
        <button id="fireBtn">ОГОНЬ</button>
        <div id="joystick-wrapper"><div id="joystick-zone"></div></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.1/nipplejs.min.js"></script>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 3000, h: 2000 };
    
    let shakePower = 0;
    let bullets = [], particles = [], clouds = [];
    let me = { x: 500, y: 500, a: 0, hp: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, score: 0, color: '#00d2ff', state: 'alive' };

    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.onresize = resize; resize();

    // Мультитач-управление
    const joy = nipplejs.create({ 
        zone: document.getElementById('joystick-zone'), 
        mode: 'static', position: {left:'50%', top:'50%'}, color:'white', size:120 
    });

    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    // Кнопка огня с поддержкой касаний без блокировки
    const fireBtn = document.getElementById('fireBtn');
    const shoot = (e) => {
        if(e) e.preventDefault(); // Важно для мультитача
        if(me.state === 'alive') bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
    };
    fireBtn.addEventListener('touchstart', shoot, {passive: false});
    fireBtn.addEventListener('mousedown', shoot);

    function createExplosion(x, y) {
        shakePower = 20; // Запуск тряски
        for(let i=0; i<40; i++) {
            let angle = Math.random() * Math.PI * 2;
            let speed = 2 + Math.random() * 15;
            particles.push({
                x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed,
                life: 1.0, size: 30, type: 'fire'
            });
        }
    }

    function update() {
        if (shakePower > 0) shakePower *= 0.9; // Затухание тряски

        // Логика самолетов (как в прошлом коде)
        const movePlane = (p) => {
            if(p.state === 'alive') {
                let r = p.a * Math.PI/180; p.x += Math.cos(r)*8; p.y += Math.sin(r)*8;
                if(p.x < 0) p.x = WORLD.w; if(p.x > WORLD.w) p.x = 0;
                if(p.y < 0) p.y = WORLD.h; if(p.y > WORLD.h) p.y = 0;
            } else {
                p.y += 4; p.dt--;
                if(p.dt <= 0) {
                    createExplosion(p.x, p.y);
                    p.state='alive'; p.hp=5; p.x=Math.random()*WORLD.w; p.y=Math.random()*WORLD.h;
                }
            }
        };

        movePlane(me);
        // AI простая логика
        let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
        opp.a += (targetA - opp.a) * 0.05;
        movePlane(opp);

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180; b.x += Math.cos(r)*22; b.y += Math.sin(r)*22;
            if(b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) bullets.splice(i, 1);
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 80) {
                target.hp--; bullets.splice(i, 1);
                if(target.hp <= 0) { target.state = 'falling'; target.dt = 200; me.score++; }
            }
        });

        particles.forEach((p, i) => {
            p.x += p.vx; p.y += p.vy; p.life -= 0.02;
            if(p.life <= 0) particles.splice(i, 1);
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        
        // ЭФФЕКТ ТРЯСКИ
        if (shakePower > 0.5) {
            ctx.translate((Math.random()-0.5)*shakePower, (Math.random()-0.5)*shakePower);
        }

        let scale = Math.min(canvas.width / WORLD.w, canvas.height / WORLD.h);
        ctx.scale(scale, scale);

        // Самолеты
        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = col; ctx.fillRect(-35, -100, 70, 200);
            ctx.restore();
        };
        drawPlane(me, me.color); drawPlane(opp, opp.color);

        // Пули и частицы
        bullets.forEach(b => { ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 15, 0, 7); ctx.fill(); });
        particles.forEach(p => {
            ctx.fillStyle = `rgba(255, ${Math.floor(255*p.life)}, 0, ${p.life})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.size * p.life, 0, 7); ctx.fill();
        });

        ctx.restore();
        document.getElementById('sc-me').innerText = me.score;
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    loop();
</script>
"""

components.html(game_html, height=600)