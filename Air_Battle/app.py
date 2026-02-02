import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Total Destruction", layout="wide")

game_html = """
<div id="top-bar" style="background: #222; color: white; padding: 12px; border-radius: 10px; font-family: sans-serif; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 11px; color: #aaa;">ВАШ ID:</span>
        <strong id="my-peer-id" style="color: #00d2ff; font-size: 13px;">...</strong>
        <button id="copy-btn" style="padding: 2px 8px; font-size: 10px; cursor: pointer; background: #444; color: #fff; border: 1px solid #666; border-radius: 4px;">Копировать</button>
    </div>
    
    <div style="display: flex; gap: 5px;">
        <input type="text" id="remote-id" placeholder="ID host" style="width: 100px; font-size: 12px; border-radius: 4px; border: none; padding: 4px;">
        <button id="connect-btn" style="background: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; padding: 4px 10px;">СЕТЬ</button>
    </div>

    <div style="display: flex; gap: 10px; align-items: center;">
        <select id="game-mode-select" style="background: #444; color: white; border: 1px solid #777; padding: 4px; border-radius: 5px; font-size: 12px; cursor: pointer;">
            <option value="classic">Классика (5 HP)</option>
            <option value="tournament">Турнир (До 10 побед)</option>
            <option value="free">Свободный полет</option>
            <option value="hardcore">Хардкор (1 HP)</option>
        </select>
        <button id="pause-btn" style="background: #f39c12; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">ПАУЗА / СТАРТ</button>
        <button id="view-mode-btn" style="padding: 5px 10px; background: #555; color: white; border-radius: 5px; cursor: pointer; border: 1px solid #777; font-size: 12px;">РЕЖИМ: ВЕСЬ ЭКРАН</button>
    </div>

    <div style="font-weight: bold; font-size: 20px; background: #333; padding: 5px 15px; border-radius: 8px;">
        МАТЧ: <span id="sc-me" style="color: #ff4b4b;">0</span> <span style="color:#777">vs</span> <span id="sc-opp" style="color: #00d2ff;">0</span>
    </div>
</div>

<div id="viewport-container" style="position: relative; width: 1000px; margin: 0 auto;">
    <div id="viewport" style="position: relative; width: 1000px; height: 600px; background: #87CEEB; border: 3px solid #333; overflow: hidden; border-radius: 8px;">
        <canvas id="gameCanvas" width="1000" height="600"></canvas>
        <div id="pause-overlay" style="position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.4); display: none; justify-content: center; align-items: center; z-index: 50; color: white; font-family: sans-serif; font-size: 40px; font-weight: bold;">ПАУЗА</div>
        <div id="win-screen" style="position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.85); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 100;">
            <h1 id="winner-text">ПОБЕДА!</h1>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">НОВАЯ ИГРА</button>
        </div>
        <div id="radar" style="position: absolute; top: 10px; right: 10px; width: 150px; height: 100px; background: rgba(0,0,0,0.5); border: 1px solid white; display: none; border-radius: 4px;">
            <div id="radar-me" style="position: absolute; width: 4px; height: 4px; background: #ff4b4b; border-radius: 50%;"></div>
            <div id="radar-opp" style="position: absolute; width: 4px; height: 4px; background: #00d2ff; border-radius: 50%;"></div>
        </div>
    </div>
</div>

<div id="lower-area" style="display: flex; width: 1000px; margin: 15px auto; gap: 20px; font-family: sans-serif;">
    <div id="chat-box" style="flex: 1; background: #fff; border: 1px solid #ddd; border-radius: 10px; display: flex; flex-direction: column; height: 200px;">
        <div id="chat-messages" style="flex: 1; overflow-y: auto; padding: 10px; font-size: 13px;"></div>
        <div style="display: flex; border-top: 1px solid #ddd; padding: 5px;">
            <input type="text" id="chat-input" placeholder="Написать игроку..." style="flex: 1; border: none; padding: 5px; outline: none;">
            <button id="send-chat" style="background: #00d2ff; border: none; padding: 5px 15px; border-radius: 5px; color: white; cursor: pointer;">▶</button>
        </div>
    </div>
    <div id="controls" style="flex: 1; display: flex; justify-content: space-around; align-items: center; background: #f8f9fa; border-radius: 10px; border: 1px solid #ddd; padding: 10px;">
        <div id="joystick-zone" style="width: 130px; height: 130px;"></div>
        <div style="text-align: center;">
            <div id="hp-bar" style="width: 150px; height: 15px; background: #333; border-radius: 10px; margin-bottom: 10px; overflow: hidden; border: 1px solid #000;">
                <div id="hp-fill" style="width: 100%; height: 100%; background: #28a745; transition: 0.2s;"></div>
            </div>
            <button id="fireBtn" style="width: 100px; height: 100px; border-radius: 50%; background: #ff4b4b; color: white; border: none; font-weight: bold; font-size: 18px; box-shadow: 0 6px #b33030; cursor: pointer; -webkit-tap-highlight-color: transparent;">ОГОНЬ</button>
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
    let gameMode = 'classic';
    
    let peer = new Peer();
    let conn = null;
    let particles = [];
    let bullets = [];
    
    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive', deathTimer: 0 };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, active: false, color: '#00d2ff', state: 'alive' };

    const clouds = [];
    for(let i=0; i<25; i++) clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, w: 200, h: 80, opacity: 0.4 });

    function createParticle(x, y, type, speed) {
        particles.push({
            x, y, vx: (Math.random()-0.5)*speed, vy: (Math.random()-0.5)*speed,
            life: 1.0, type: type
        });
    }

    // --- BUTTON LOGIC ---
    document.getElementById('copy-btn').onclick = () => {
        navigator.clipboard.writeText(document.getElementById('my-peer-id').innerText);
        const b = document.getElementById('copy-btn'); b.innerText = "OK!"; setTimeout(()=>b.innerText="Копировать", 1000);
    };

    document.getElementById('view-mode-btn').onclick = function() {
        isCamera = !isCamera;
        this.innerText = isCamera ? "РЕЖИМ: КАМЕРА" : "РЕЖИМ: ВЕСЬ ЭКРАН";
        document.getElementById('radar').style.display = isCamera ? "block" : "none";
    };

    document.getElementById('game-mode-select').onchange = (e) => {
        gameMode = e.target.value;
        applyModeSettings();
        if(conn) conn.send({ t: 'mode', val: gameMode });
    };

    function applyModeSettings() {
        if(gameMode === 'hardcore') { me.max = 1; me.hp = 1; }
        else if(gameMode === 'free') { me.max = 999; me.hp = 999; }
        else { me.max = 5; me.hp = 5; }
        me.state = 'alive';
    }

    document.getElementById('pause-btn').onclick = () => {
        isPaused = !isPaused;
        togglePause(isPaused);
        if(conn) conn.send({ t: 'pause', val: isPaused });
    };

    function togglePause(val) {
        isPaused = val;
        document.getElementById('pause-overlay').style.display = isPaused ? "flex" : "none";
    }

    // --- PEERJS ---
    peer.on('open', id => document.getElementById('my-peer-id').innerText = id);
    peer.on('connection', c => { conn = c; setupConn(); });
    document.getElementById('connect-btn').onclick = () => { conn = peer.connect(document.getElementById('remote-id').value); setupConn(); };

    function setupConn() {
        conn.on('data', d => {
            if(d.t === 's') { opp.x = d.x; opp.y = d.y; opp.a = d.a; opp.hp = d.hp; opp.active = true; opp.state = d.st; }
            if(d.t === 'f') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
            if(d.t === 'sc') { me.score = d.me; opp.score = d.opp; checkWin(); }
            if(d.t === 'chat') addMsg("Друг: " + d.msg, opp.color);
            if(d.t === 'pause') togglePause(d.val);
            if(d.t === 'mode') { gameMode = d.val; document.getElementById('game-mode-select').value = d.val; applyModeSettings(); }
        });
    }

    function checkWin() {
        if(gameMode === 'tournament' && (me.score >= 10 || opp.score >= 10)) {
            document.getElementById('win-screen').style.display = 'flex';
            document.getElementById('winner-text').innerText = me.score >= 10 ? "ВЫ ПОБЕДИЛИ!" : "ВЫ ПРОИГРАЛИ";
        }
    }

    // --- CHAT ---
    function addMsg(text, color) {
        const d = document.createElement('div'); d.style.color = color; d.innerText = text;
        const c = document.getElementById('chat-messages'); c.appendChild(d); c.scrollTop = c.scrollHeight;
    }
    document.getElementById('send-chat').onclick = sendChat;
    document.getElementById('chat-input').onkeydown = (e) => { if(e.key==='Enter') sendChat(); };
    function sendChat() {
        const inp = document.getElementById('chat-input');
        if(!inp.value.trim()) return;
        addMsg("Я: " + inp.value, me.color);
        if(conn) conn.send({ t: 'chat', msg: inp.value });
        inp.value = "";
    }

    // --- CORE LOOP ---
    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    document.getElementById('fireBtn').onclick = () => {
        if(isPaused || me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn) conn.send({ t: 'f', x: me.x, y: me.y, a: me.a });
    };

    function loop() {
        if(!isPaused) update();
        draw();
        requestAnimationFrame(loop);
    }

    function update() {
        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r)*5; me.y += Math.sin(r)*5;
            if(gameMode !== 'free') {
                if(me.hp <= 4) createParticle(me.x, me.y, 'smoke', 2);
                if(me.hp <= 2) createParticle(me.x, me.y, 'fire', 3);
                if(me.hp <= 0) { me.state = 'falling'; me.deathTimer = 120; }
            }
        } else {
            // ЛОГИКА ШТОПОРА: Падение + Хаотичное вращение + Тряска по X
            me.y += 7; 
            me.a += 20; 
            me.x += (Math.random() - 0.5) * 15; 
            createParticle(me.x, me.y, 'smoke', 4);
            createParticle(me.x, me.y, 'fire', 5);
            me.deathTimer--;
            if(me.deathTimer <= 0 || me.y > WORLD.h) respawn();
        }

        if(me.x<0) me.x=WORLD.w; if(me.x>WORLD.w) me.x=0;
        if(me.y<0) me.y=WORLD.h; if(me.y>WORLD.h) me.y=0;

        bullets.forEach((b, i) => {
            let br = b.a * Math.PI/180;
            b.x += Math.cos(br)*12; b.y += Math.sin(br)*12;
            let t = b.owner === 'me' ? opp : me;
            if(t.active && t.state === 'alive' && Math.hypot(b.x-t.x, b.y-t.y) < 35) {
                if(gameMode !== 'free') {
                    if(b.owner === 'me') {
                        opp.hp--;
                        if(opp.hp <= 0) { me.score++; if(conn) conn.send({t:'sc', me:opp.score, opp:me.score}); checkWin(); }
                    }
                    createParticle(b.x, b.y, 'spark', 6);
                    bullets.splice(i, 1);
                }
            }
            if(Math.abs(b.x - me.x) > 2000) bullets.splice(i,1);
        });

        particles.forEach((p, i) => {
            p.x += p.vx; p.y += p.vy; p.life -= 0.02;
            if(p.life <= 0) particles.splice(i, 1);
        });

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
            ctx.fillStyle = p.type === 'smoke' ? `rgba(80,80,80,${p.life})` : (p.type === 'fire' ? `rgba(255,69,0,${p.life})` : `rgba(255,255,255,${p.life})`);
            ctx.beginPath(); ctx.arc(p.x, p.y, p.type==='smoke'?14:6, 0, 7); ctx.fill();
        });

        bullets.forEach(b => {
            ctx.fillStyle = "yellow"; ctx.beginPath(); ctx.arc(b.x, b.y, 5, 0, 7); ctx.fill();
        });

        const drawPlane = (p, col) => {
            ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a * Math.PI/180);
            ctx.fillStyle = "#333"; ctx.fillRect(-30, -8, 60, 16);
            ctx.fillStyle = col; ctx.fillRect(-8, -45, 16, 90);
            // Визуальный эффект при падении
            if(p.state === 'falling') {
                ctx.fillStyle = "orange";
                ctx.beginPath(); ctx.arc(0,0, 20, 0, 7); ctx.fill();
            }
            ctx.restore();
        };
        drawPlane(me, me.color);
        if(opp.active) drawPlane(opp, opp.color);
        ctx.restore();
        
        document.getElementById('hp-fill').style.width = (gameMode === 'free' ? 100 : (me.hp/me.max*100)) + "%";
        document.getElementById('sc-me').innerText = me.score;
        document.getElementById('sc-opp').innerText = opp.score;
        
        if(isCamera) {
            document.getElementById('radar-me').style.left = (me.x/WORLD.w*100) + "%";
            document.getElementById('radar-me').style.top = (me.y/WORLD.h*100) + "%";
            document.getElementById('radar-opp').style.left = (opp.x/WORLD.w*100) + "%";
            document.getElementById('radar-opp').style.top = (opp.y/WORLD.h*100) + "%";
        }
    }

    function respawn() {
        me.state = 'alive'; 
        applyModeSettings(); 
        me.x = Math.random()*(WORLD.w-400)+200; me.y = Math.random()*(WORLD.h-400)+200;
    }

    loop();
</script>
"""

components.html(game_html, height=1100)