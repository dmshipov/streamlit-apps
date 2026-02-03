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
        gap: 5px; margin-bottom: 5px; font-size: 11px; flex-wrap: wrap;
    }
    #viewport-container { position: relative; width: 100%; margin: 0 auto; touch-action: none; }
    #viewport { 
        position: relative; width: 100%; height: 350px; 
        background: #87CEEB; border: 2px solid #444; overflow: hidden; border-radius: 8px; 
    }
    canvas { width: 100%; height: 100%; display: block; }

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
    
    #help-text { font-size: 9px; color: #888; margin-top: 5px; width: 100%; text-align: center; }
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
    
    <div id="net-controls" style="display: none; flex-direction: column; gap: 4px; align-items: center;">
        <div style="display: flex; gap: 4px; align-items: center;">
            <input type="text" id="remote-id" placeholder="ID противника" style="width: 100px; font-size: 9px; padding: 4px; border-radius: 3px; border: 1px solid #666;">
            <button id="connect-btn" style="background:#28a745; color:white; border:none; padding:5px 10px; font-size:9px; border-radius:3px; cursor:pointer; font-weight: bold;">OK</button>
        </div>
        <span id="connection-status" style="font-size:9px; color:#ffaa00;">Ожидание...</span>
    </div>

    <div style="text-align: center;">
        <div style="font-size: 10px; color: #aaa;">РАУНДЫ</div>
        <div style="font-size: 16px; font-weight: bold; color: #fbff00;"><span id="wins-me">0</span> : <span id="wins-opp">0</span></div>
    </div>

    <div style="text-align: right;">
        <div style="font-size: 9px; color: #aaa;">МОЙ ID:</div>
        <div style="font-size: 11px; font-weight: bold; color:#00d2ff; cursor: pointer; user-select: all;" id="my-peer-id" title="Нажмите чтобы скопировать">...</div>
        <div style="font-size: 18px; font-weight: bold; margin-top: 3px;"><span id="sc-me" style="color:#ff4b4b">0</span> : <span id="sc-opp" style="color:#00d2ff">0</span></div>
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

<div id="help-text">
    💡 Для сетевой игры: 1) Скопируйте свой ID 2) Отправьте другу 3) Друг вводит ваш ID и нажимает OK
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
    let propellerRotation = 0;
    let screenShake = 0;

    let bullets = [];
    let particles = [];
    let clouds = [];
    
    for(let i=0; i<15; i++) {
        clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.5 + Math.random(), op: 0.3 + Math.random()*0.4 });
    }

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, max: 5, score: 0, color: '#00d2ff', state: 'alive' };

    // PeerJS setup with multiple server options
    let peer = null;
    let conn = null;
    let myPeerId = '';
    let connectionAttempts = 0;

    function showStatus(msg, color = '#ffaa00') {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.innerText = msg;
            statusEl.style.color = color;
        }
        console.log('Status:', msg);
    }

    function initPeer() {
        try {
            // Use cloud PeerJS server with config
            const config = {
                host: '0.peerjs.com',
                port: 443,
                path: '/',
                secure: true,
                config: {
                    iceServers: [
                        { urls: 'stun:stun.l.google.com:19302' },
                        { urls: 'stun:global.stun.twilio.com:3478' }
                    ]
                },
                debug: 2 // Enable detailed logs
            };

            peer = new Peer(config);
            
            peer.on('open', id => {
                myPeerId = id;
                const idElement = document.getElementById('my-peer-id');
                idElement.innerText = id;
                idElement.title = 'Нажмите чтобы скопировать: ' + id;
                console.log('✅ My peer ID:', id);
                showStatus('Готов к игре', '#00ff00');
                
                // Click to copy ID
                idElement.onclick = () => {
                    navigator.clipboard.writeText(id).then(() => {
                        showStatus('ID скопирован!', '#00ff00');
                        setTimeout(() => showStatus('Готов к игре', '#00ff00'), 2000);
                    });
                };
            });
            
            peer.on('error', err => {
                console.error('❌ Peer error:', err.type, err);
                
                if (err.type === 'peer-unavailable') {
                    showStatus('Игрок не найден! Проверьте ID', '#ff0000');
                    alert('Игрок с таким ID не найден.\n\nПричины:\n- ID введен неправильно\n- Игрок не в сети\n- Игрок закрыл страницу\n\nПроверьте ID и попробуйте снова.');
                } else if (err.type === 'network') {
                    showStatus('Ошибка сети', '#ff0000');
                    alert('Ошибка сети. Проверьте интернет-соединение.');
                } else if (err.type === 'server-error') {
                    showStatus('Ошибка сервера', '#ff0000');
                    alert('Ошибка сервера PeerJS. Попробуйте позже.');
                } else {
                    showStatus('Ошибка: ' + err.type, '#ff0000');
                }
            });
            
            peer.on('disconnected', () => {
                console.warn('⚠️ Peer disconnected, attempting reconnect...');
                showStatus('Переподключение...', '#ffaa00');
                setTimeout(() => {
                    if (!peer.destroyed) {
                        peer.reconnect();
                    }
                }, 1000);
            });
            
            peer.on('connection', c => {
                console.log('📞 Incoming connection from:', c.peer);
                
                // Close existing connection if any
                if (conn && conn.open) {
                    conn.close();
                }
                
                conn = c;
                isSolo = false;
                updateUI('net');
                setupConn();
                showStatus('Подключен: ' + c.peer.substring(0, 8) + '...', '#00ff00');
            });
        } catch(e) {
            console.error('💥 Failed to initialize PeerJS:', e);
            showStatus('Ошибка инициализации', '#ff0000');
            alert('Не удалось инициализировать PeerJS: ' + e.message);
        }
    }

    function setupConn() {
        if (!conn) return;
        
        conn.on('open', () => {
            console.log('✅ Connection fully established');
            showStatus('Подключено! Играем...', '#00ff00');
            connectionAttempts = 0;
        });
        
        conn.on('data', d => {
            if(d.t === 's') { 
                opp.x = d.x; opp.y = d.y; opp.a = d.a; opp.hp = d.hp; 
                opp.state = d.state; opp.score = d.score;
            }
            if(d.t === 'f') bullets.push({ x: d.x, y: d.y, a: d.a, owner: 'opp' });
        });
        
        conn.on('close', () => {
            console.log('🔌 Connection closed');
            showStatus('Противник отключился', '#ff6600');
            isSolo = true;
            updateUI('easy');
            setTimeout(() => {
                alert('Противник отключился. Переход в одиночный режим.');
            }, 500);
        });
        
        conn.on('error', err => {
            console.error('❌ Connection error:', err);
            showStatus('Ошибка связи', '#ff0000');
        });
    }

    document.getElementById('connect-btn').onclick = () => {
        const remoteId = document.getElementById('remote-id').value.trim();
        
        if (!remoteId) {
            alert('Введите ID противника');
            return;
        }
        
        if (remoteId === myPeerId) {
            alert('Нельзя подключиться к самому себе!');
            return;
        }
        
        if (!peer || peer.destroyed) {
            alert('PeerJS не инициализирован. Перезагрузите страницу.');
            return;
        }
        
        if (conn && conn.open) {
            const confirm = window.confirm('Уже есть подключение. Подключиться к новому игроку?');
            if (!confirm) return;
            conn.close();
        }
        
        console.log('🔗 Connecting to:', remoteId);
        showStatus('Подключение к ' + remoteId.substring(0, 8) + '...', '#ffaa00');
        connectionAttempts++;
        
        try {
            conn = peer.connect(remoteId, {
                reliable: true,
                serialization: 'json'
            });
            
            // Connection timeout
            const timeout = setTimeout(() => {
                if (conn && !conn.open) {
                    console.error('⏱️ Connection timeout');
                    showStatus('Таймаут подключения', '#ff0000');
                    conn.close();
                    alert('Не удалось подключиться.\n\nПричины:\n- Неверный ID\n- Игрок не в сети\n- Проблемы с сетью\n\nПопробуйте еще раз.');
                }
            }, 10000);
            
            conn.on('open', () => {
                clearTimeout(timeout);
                console.log('✅ Connection opened!');
                isSolo = false;
                updateUI('net');
                setupConn();
                showStatus('Подключено! Играем...', '#00ff00');
                resetMatch();
            });
            
            conn.on('error', err => {
                clearTimeout(timeout);
                console.error('❌ Connection error:', err);
                showStatus('Ошибка подключения', '#ff0000');
                
                if (connectionAttempts >= 3) {
                    alert('Несколько неудачных попыток.\n\nСоветы:\n1. Проверьте, что ID скопирован полностью\n2. Убедитесь, что оба игрока онлайн\n3. Попробуйте другой браузер\n4. Проверьте интернет-соединение');
                    connectionAttempts = 0;
                }
            });
        } catch(e) {
            console.error('💥 Failed to connect:', e);
            showStatus('Ошибка!', '#ff0000');
            alert('Не удалось подключиться: ' + e.message);
        }
    };

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

    document.getElementById('mode-ai-easy').onclick = () => { 
        isSolo=true; 
        difficulty='easy'; 
        updateUI('easy'); 
        if(conn && conn.open) conn.close();
        resetMatch(); 
    };
    document.getElementById('mode-ai-hard').onclick = () => { 
        isSolo=true; 
        difficulty='hard'; 
        updateUI('hard'); 
        if(conn && conn.open) conn.close();
        resetMatch(); 
    };
    document.getElementById('mode-net').onclick = () => { 
        updateUI('net'); 
    };

    const joy = nipplejs.create({ zone: document.getElementById('joystick-zone'), mode: 'static', position: {left:'50%', top:'50%'} });
    joy.on('move', (e, d) => { if(d.angle && me.state === 'alive') me.a = -d.angle.degree; });

    const fire = (e) => {
        if(e) { e.preventDefault(); e.stopPropagation(); }
        if(!gameActive || me.state !== 'alive') return;
        bullets.push({ x: me.x, y: me.y, a: me.a, owner: 'me' });
        if(conn && conn.open) {
            try {
                conn.send({ t: 'f', x: me.x, y: me.y, a: me.a });
            } catch(e) {
                console.error('Failed to send fire:', e);
            }
        }
    };

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
            if(winner === "ME") { resTxt.innerText = "ПОБЕДА В РАУНДЕ!"; resTxt.style.color = "#00ff00"; totalWinsMe++; }
            else { resTxt.innerText = "ПРОИГРЫШ!"; resTxt.style.color = "#ff0000"; totalWinsOpp++; }
            document.getElementById('wins-me').innerText = totalWinsMe;
            document.getElementById('wins-opp').innerText = totalWinsOpp;
            setTimeout(resetMatch, 3000);
        }
    }

    function createPart(x, y, type, color = null) {
        if(type === 'explode') { 
            screenShake = 25;
            for(let i=0; i<60; i++) {
                particles.push({
                    x, y, 
                    vx: (Math.random()-0.5)*30, 
                    vy: (Math.random()-0.5)*30, 
                    life: 1.0 + Math.random(), 
                    type: Math.random() > 0.3 ? 'fire' : 'smoke',
                    size: 10 + Math.random()*35
                });
            }
            for(let i=0; i<10; i++) {
                particles.push({
                    x, y, 
                    vx: (Math.random()-0.5)*15, 
                    vy: (Math.random()-0.5)*15, 
                    life: 2.5, 
                    type: 'debris',
                    color: color,
                    a: Math.random()*360,
                    va: (Math.random()-0.5)*25,
                    size: 15 + Math.random()*25
                });
            }
            return;
        }
        
        let count = type === 'fire' ? 4 : 1;
        for(let i=0; i<count; i++) {
            particles.push({ 
                x, y, 
                vx: (Math.random()-0.5)*5, 
                vy: (Math.random()-0.5)*5, 
                life: 1.0, 
                type: type,
                size: type === 'fire' ? 12 : 15
            });
        }
    }

    function update() {
        if(!gameActive) return;
        propellerRotation += 0.9; 

        clouds.forEach(c => { c.x -= 0.6 * c.s; if(c.x < -200) c.x = WORLD.w + 200; });
        
        const wrap = (obj) => {
            if (obj.x < 0) obj.x = WORLD.w; if (obj.x > WORLD.w) obj.x = 0;
            if (obj.y < 0) obj.y = WORLD.h; if (obj.y > WORLD.h) obj.y = 0;
        };

        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r) * 15;
            me.y += Math.sin(r) * 15;
            wrap(me);
            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { me.state = 'falling'; me.dt = 90; opp.score++; checkWin(); }
        } else if (gameActive) {
            me.y += 10; me.a += 12; createPart(me.x, me.y, 'fire');
            if(--me.dt <= 0) { 
                createPart(me.x, me.y, 'explode', me.color); 
                respawn(me); 
            }
        }

        // Send state to opponent if connected
        if(conn && conn.open && !isSolo) {
            try {
                conn.send({ t: 's', x: me.x, y: me.y, a: me.a, hp: me.hp, state: me.state, score: me.score });
            } catch(e) {
                console.error('Failed to send state:', e);
            }
        }

        if(isSolo) {
            if(opp.state === 'alive') {
                let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
                let diff = targetA - opp.a;
                while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
                opp.a += diff * (difficulty === 'hard' ? 0.12 : 0.06); 
                let r = opp.a * Math.PI/180;
                opp.x += Math.cos(r) * (difficulty === 'hard' ? 15 : 12);
                opp.y += Math.sin(r) * (difficulty === 'hard' ? 15 : 12);
                wrap(opp);
                if(opp.hp < 3) createPart(opp.x, opp.y, 'smoke');
                if(Math.random() < (difficulty==='hard'?0.04:0.015) && Math.abs(diff) < 20) bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
                if(opp.hp <= 0) { opp.state = 'falling'; opp.dt = 90; me.score++; checkWin(); }
            } else if (gameActive) {
                opp.y += 10; createPart(opp.x, opp.y, 'fire');
                if(--opp.dt <= 0) { 
                    createPart(opp.x, opp.y, 'explode', opp.color); 
                    respawn(opp); 
                }
            }
        }

        particles.forEach((p, i) => {
            p.x += p.vx; p.y += p.vy; 
            if(p.type === 'debris') { p.a += p.va; p.vy += 0.4; }
            p.life -= (p.type === 'debris' ? 0.015 : 0.04);
            if(p.life <= 0) particles.splice(i, 1);
        });

        bullets.forEach((b, i) => {
            let r = b.a * Math.PI/180;
            b.x += Math.cos(r) * 35; b.y += Math.sin(r) * 35;
            if (b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) { bullets.splice(i, 1); return; }
            let target = b.owner === 'me' ? opp : me;
            if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 65) {
                target.hp--; bullets.splice(i, 1);
            }
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        
        if(screenShake > 1) {
            ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);
            screenShake *= 0.9;
        }

        ctx.scale(canvas.width / WORLD.w, canvas.height / WORLD.h);
        clouds.forEach(c => {
            ctx.globalAlpha = c.op; ctx.fillStyle = "white";
            ctx.beginPath(); ctx.arc(c.x, c.y, 45*c.s, 0, 7); ctx.fill();
        });
        ctx.globalAlpha = 1.0;

        particles.forEach(p => {
            if(p.type === 'debris') {
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.a * Math.PI/180);
                ctx.fillStyle = p.color;
                ctx.fillRect(-p.size/2, -p.size/2, p.size, p.size/3);
                ctx.restore();
            } else {
                ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${150*p.life}, 0, ${p.life})` : `rgba(100,100,100,${p.life})`;
                ctx.beginPath(); ctx.arc(p.x, p.y, (p.size || 10) * p.life, 0, 7); ctx.fill();
            }
        });

        const drawPlane = (p, col) => {
            if(p.state !== 'alive' && p.dt <= 0) return;
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.a * Math.PI / 180);
            
            ctx.fillStyle = "rgba(0,0,0,0.2)";
            ctx.beginPath(); ctx.ellipse(0, 15, 50, 15, 0, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = col;
            ctx.beginPath(); ctx.moveTo(-35, 0); ctx.lineTo(-55, -25); ctx.lineTo(-55, 25); ctx.fill();

            let grad = ctx.createLinearGradient(0, -15, 0, 15);
            grad.addColorStop(0, col); grad.addColorStop(0.5, "#fff"); grad.addColorStop(1, col);
            ctx.fillStyle = grad;
            ctx.beginPath(); ctx.moveTo(-45, -8); ctx.quadraticCurveTo(0, -22, 45, -15); ctx.lineTo(45, 15); ctx.quadraticCurveTo(0, 22, -45, 8); ctx.fill();

            ctx.fillStyle = "#333"; ctx.fillRect(5, -10, 15, 20);
            ctx.fillStyle = "#88e1ff"; ctx.fillRect(7, -8, 12, 16);

            ctx.fillStyle = col;
            ctx.beginPath(); ctx.roundRect(-8, -65, 25, 130, 8); ctx.fill();

            if (p.state === 'alive') {
                ctx.save();
                ctx.translate(45, 0); ctx.rotate(propellerRotation);
                ctx.fillStyle = "rgba(255, 255, 255, 0.2)";
                ctx.beginPath(); ctx.arc(0, 0, 40, 0, Math.PI * 2); ctx.fill();
                ctx.restore();
            }
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
    
    // Initialize PeerJS on load
    initPeer();
    loop();
</script>
"""

components.html(game_html, height=650)