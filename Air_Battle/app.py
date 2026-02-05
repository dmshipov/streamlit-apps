import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Tactical VFX", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 5px; background: #111; font-family: sans-serif; overflow-x: hidden; color: white; }
    
    #top-bar { 
        background: #222; padding: 4px; border-radius: 6px; 
        display: flex; justify-content: space-between; align-items: center; 
        gap: 3px; margin-bottom: 3px; font-size: 9px;
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

    /* Sidebar */
    #sidebar {
        position: fixed;
        top: 0;
        right: -340px;
        width: 320px;
        height: 100%;
        background: #1a1a1a;
        border-left: 2px solid #444;
        padding: 20px;
        box-shadow: -5px 0 15px rgba(0,0,0,0.5);
        transition: right 0.3s ease;
        z-index: 200;
        overflow-y: auto;
    }
    
    #sidebar.open { right: 0; }
    
    #sidebar h3 {
        color: #00d2ff;
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 18px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }
    
    .setting-group {
        margin-bottom: 25px;
    }
    
    .setting-label {
        display: block;
        color: #aaa;
        font-size: 11px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .slider-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .slider {
        flex: 1;
        -webkit-appearance: none;
        appearance: none;
        height: 6px;
        border-radius: 3px;
        background: #444;
        outline: none;
    }
    
    .slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: #00d2ff;
        cursor: pointer;
    }
    
    .slider::-moz-range-thumb {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: #00d2ff;
        cursor: pointer;
        border: none;
    }
    
    .slider-value {
        min-width: 40px;
        text-align: right;
        color: #00d2ff;
        font-weight: bold;
        font-size: 12px;
    }
    
    .btn-mode { 
        background: #444; 
        color: white; 
        border: 1px solid #666; 
        padding: 8px 12px; 
        border-radius: 4px; 
        font-size: 10px; 
        cursor: pointer;
        width: 100%;
        margin-bottom: 8px;
        transition: all 0.2s;
        text-align: left;
    }
    .btn-mode:hover { background: #555; }
    .active-mode { background: #00d2ff; color: black; font-weight: bold; }
    
    .mode-icon {
        display: inline-block;
        width: 20px;
        text-align: center;
        margin-right: 5px;
    }
    
    .btn-settings {
        background: #444;
        color: white;
        border: 1px solid #666;
        padding: 4px 8px;
        border-radius: 3px;
        font-size: 9px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-settings:hover { background: #555; }
    
    .btn-start-pause {
        background: #28a745;
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 2px #1e7e34;
        transition: all 0.2s;
    }
    .btn-start-pause:hover { background: #218838; }
    .btn-start-pause:active { transform: translateY(1px); box-shadow: 0 1px #1e7e34; }
    .btn-start-pause.paused { background: #ffc107; box-shadow: 0 2px #d39e00; }
    .btn-start-pause.paused:hover { background: #e0a800; }
    
    #close-sidebar {
        position: absolute;
        top: 15px;
        right: 15px;
        background: none;
        border: none;
        color: #888;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        line-height: 30px;
        text-align: center;
    }
    #close-sidebar:hover { color: #fff; }
    
    #net-controls {
        display: none;
        gap: 4px;
        align-items: center;
        background: #2a2a2a;
        padding: 8px;
        border-radius: 4px;
        margin-top: 10px;
    }
    
    #net-controls input {
        width: 100%;
        font-size: 11px;
        padding: 6px;
        background: #333;
        border: 1px solid #555;
        color: white;
        border-radius: 3px;
    }
    
    #net-controls button {
        background: #28a745;
        color: white;
        border: none;
        padding: 6px 12px;
        font-size: 11px;
        border-radius: 3px;
        cursor: pointer;
        margin-top: 5px;
        width: 100%;
    }
    
    #connection-status {
        font-size: 10px;
        color: #aaa;
        margin-top: 5px;
        display: block;
    }
    
    .mode-description {
        font-size: 9px;
        color: #666;
        margin-top: 3px;
        font-style: italic;
        padding-left: 25px;
    }
    
    .game-timer {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.7);
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 18px;
        font-weight: bold;
        color: #ffff00;
        display: none;
        z-index: 50;
    }
    
    .combo-indicator {
        position: absolute;
        top: 50px;
        right: 20px;
        background: rgba(255, 69, 0, 0.8);
        padding: 10px 15px;
        border-radius: 10px;
        font-size: 20px;
        font-weight: bold;
        color: white;
        display: none;
        z-index: 50;
        animation: pulse 0.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
</style>

<div id="sidebar">
    <button id="close-sidebar">×</button>
    <h3>⚙️ НАСТРОЙКИ</h3>
    
    <div class="setting-group">
        <label class="setting-label">🎮 Режимы PvP</label>
        <button id="mode-ai-easy" class="btn-mode active-mode">
            <span class="mode-icon">🎓</span>КУРСАНТ
        </button>
        <div class="mode-description">AI противник (легкий уровень)</div>
        
        <button id="mode-ai-hard" class="btn-mode">
            <span class="mode-icon">⚔️</span>АС
        </button>
        <div class="mode-description">AI противник (сложный уровень)</div>
        
        <button id="mode-net" class="btn-mode">
            <span class="mode-icon">🌐</span>СЕТЕВАЯ ИГРА
        </button>
        <div class="mode-description">Игра против реального игрока</div>
        
        <div id="net-controls">
            <input type="text" id="remote-id" placeholder="ID противника">
            <button id="connect-btn">ПОДКЛЮЧИТЬСЯ</button>
            <span id="connection-status"></span>
        </div>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">🎯 Аркадные режимы</label>
        
        <button id="mode-paratrooper" class="btn-mode">
            <span class="mode-icon">🪂</span>ПАРАШЮТИСТЫ
        </button>
        <div class="mode-description">Сбивайте парашютистов на точной дистанции</div>
        
        <button id="mode-balloon" class="btn-mode">
            <span class="mode-icon">🎈</span>ВОЗДУШНЫЕ ШАРЫ
        </button>
        <div class="mode-description">Лопайте цветные шары на скорость</div>
        
        <button id="mode-cargo" class="btn-mode">
            <span class="mode-icon">📦</span>ГРУЗОВЫЕ ЯЩИКИ
        </button>
        <div class="mode-description">Перехватывайте падающие грузы</div>
        
        <button id="mode-rings" class="btn-mode">
            <span class="mode-icon">⭕</span>ВОЗДУШНЫЕ КОЛЬЦА
        </button>
        <div class="mode-description">Пролетайте через кольца на время</div>
        
        <button id="mode-survival" class="btn-mode">
            <span class="mode-icon">⚡</span>ВЫЖИВАНИЕ
        </button>
        <div class="mode-description">Уничтожайте волны врагов</div>
        
        <button id="mode-escort" class="btn-mode">
            <span class="mode-icon">🛡️</span>ЭСКОРТ
        </button>
        <div class="mode-description">Защитите транспорт от врагов</div>
        
        <button id="mode-race" class="btn-mode">
            <span class="mode-icon">🏁</span>ГОНКА
        </button>
        <div class="mode-description">Пройдите трассу за минимальное время</div>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">Лимит очков (PvP)</label>
        <button id="lim-1" class="btn-mode">ДО 1</button>
        <button id="lim-5" class="btn-mode active-mode">ДО 5</button>
        <button id="lim-10" class="btn-mode">ДО 10</button>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">Скорость самолетов</label>
        <div class="slider-container">
            <input type="range" id="speed-slider" class="slider" min="5" max="25" value="10" step="1">
            <span class="slider-value" id="speed-value">10</span>
        </div>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">Зум камеры</label>
        <div class="slider-container">
            <input type="range" id="zoom-slider" class="slider" min="0.5" max="2.0" value="1.0" step="0.1">
            <span class="slider-value" id="zoom-value">1.0x</span>
        </div>
        <div style="font-size: 9px; color: #666; margin-top: 5px;">
            Приближение/отдаление камеры
        </div>
    </div>
</div>

<div id="top-bar">
    <div style="display: flex; gap: 10px; align-items: center;">
        <button class="btn-settings" id="open-sidebar">⚙️ НАСТРОЙКИ</button>
        <button class="btn-start-pause" id="start-pause-btn">▶ СТАРТ</button>
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
        <div class="game-timer" id="game-timer">60</div>
        <div class="combo-indicator" id="combo-indicator">COMBO x2!</div>
        <div id="overlay">
            <h2 id="result-text">ПОБЕДА!</h2>
            <p id="result-subtext">Следующий раунд через 3 сек...</p>
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
    
    // Game state
    let isSolo = true;
    let difficulty = 'easy';
    let gameMode = 'ai-easy';
    let scoreLimit = 5;
    let gameActive = false;
    let gamePaused = true;
    let totalWinsMe = 0;
    let totalWinsOpp = 0;
    let propellerRotation = 0;
    let screenShake = 0;
    let planeSpeed = 10;
    let cameraZoom = 1.0;
    let precisionDistance = 400;
    let precisionTolerance = 80;

    // Arcade mode variables
    let arcadeTargets = [];
    let gameTimer = 0;
    let comboCounter = 0;
    let lastHitTime = 0;
    let rings = [];
    let enemies = [];
    let waveNumber = 1;
    let escortTarget = null;
    let checkpoints = [];

    let bullets = [];
    let particles = [];
    let clouds = [];
    
    for(let i=0; i<15; i++) {
        clouds.push({ x: Math.random()*WORLD.w, y: Math.random()*WORLD.h, s: 0.5 + Math.random(), op: 0.3 + Math.random()*0.4 });
    }

    let me = { x: 500, y: 500, a: 0, hp: 5, max: 5, score: 0, color: '#ff4b4b', state: 'alive' };
    let opp = { x: 2500, y: 1500, a: 180, hp: 5, max: 5, score: 0, color: '#00d2ff', state: 'alive' };

    let peer = null;
    let conn = null;
    let myPeerId = '';

    // Sidebar controls
    document.getElementById('open-sidebar').addEventListener('click', () => {
        document.getElementById('sidebar').classList.add('open');
    });
    
    document.getElementById('close-sidebar').addEventListener('click', () => {
        document.getElementById('sidebar').classList.remove('open');
    });

    // Start/Pause button
    const startPauseBtn = document.getElementById('start-pause-btn');
    startPauseBtn.addEventListener('click', () => {
        gamePaused = !gamePaused;
        gameActive = !gamePaused;
        
        if (gamePaused) {
            startPauseBtn.textContent = '▶ СТАРТ';
            startPauseBtn.classList.add('paused');
        } else {
            startPauseBtn.textContent = '⏸ ПАУЗА';
            startPauseBtn.classList.remove('paused');
            if (isArcadeMode()) initArcadeMode();
        }
    });

    // Speed slider
    const speedSlider = document.getElementById('speed-slider');
    const speedValue = document.getElementById('speed-value');
    speedSlider.addEventListener('input', (e) => {
        planeSpeed = parseInt(e.target.value);
        speedValue.textContent = planeSpeed;
    });

    // Zoom slider
    const zoomSlider = document.getElementById('zoom-slider');
    const zoomValue = document.getElementById('zoom-value');
    zoomSlider.addEventListener('input', (e) => {
        cameraZoom = parseFloat(e.target.value);
        zoomValue.textContent = cameraZoom.toFixed(1) + 'x';
    });

    // Mode buttons
    const modes = ['ai-easy', 'ai-hard', 'net', 'paratrooper', 'balloon', 'cargo', 'rings', 'survival', 'escort', 'race'];
    modes.forEach(mode => {
        const btn = document.getElementById('mode-' + mode);
        if (btn) {
            btn.addEventListener('click', () => {
                setGameMode(mode);
                updateUI(mode);
            });
        }
    });

    function isArcadeMode() {
        return ['paratrooper', 'balloon', 'cargo', 'rings', 'survival', 'escort', 'race'].includes(gameMode);
    }

    function setGameMode(mode) {
        gameMode = mode;
        isSolo = (mode !== 'net');
        
        if (mode === 'ai-easy') difficulty = 'easy';
        else if (mode === 'ai-hard') difficulty = 'hard';
        
        // Show/hide timer
        document.getElementById('game-timer').style.display = 
            (['balloon', 'rings', 'race'].includes(mode)) ? 'block' : 'none';
        
        resetRound();
    }

    function updateUI(mode) {
        modes.forEach(m => {
            const btn = document.getElementById('mode-' + m);
            if (btn) btn.classList.remove('active-mode');
        });
        const activeBtn = document.getElementById('mode-' + mode);
        if (activeBtn) activeBtn.classList.add('active-mode');
        
        document.getElementById('net-controls').style.display = (mode === 'net') ? 'block' : 'none';
    }

    // Score limit buttons
    [1, 5, 10].forEach(lim => {
        document.getElementById('lim-' + lim).addEventListener('click', () => {
            scoreLimit = lim;
            ['lim-1', 'lim-5', 'lim-10'].forEach(id => {
                document.getElementById(id).classList.remove('active-mode');
            });
            document.getElementById('lim-' + lim).classList.add('active-mode');
        });
    });

    // Network controls
    document.getElementById('connect-btn').addEventListener('click', () => {
        const remoteId = document.getElementById('remote-id').value.trim();
        if (!remoteId) {
            alert('Введите ID противника');
            return;
        }
        connectToPeer(remoteId);
    });

    function showStatus(msg, color = '#ffaa00') {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.innerText = msg;
            statusEl.style.color = color;
        }
        console.log('📡', msg);
    }

    function initPeer() {
        try {
            peer = new Peer({
                config: {
                    iceServers: [
                        { urls: 'stun:stun.l.google.com:19302' },
                        { urls: 'stun:global.stun.twilio.com:3478' }
                    ]
                }
            });
            
            peer.on('open', id => {
                myPeerId = id;
                document.getElementById('my-peer-id').innerText = id;
                console.log('My peer ID:', id);
                showStatus('Готов');
            });
            
            peer.on('error', err => {
                console.error('❌ Peer error:', err.type, err);
                if (err.type === 'peer-unavailable') {
                    showStatus('ID не найден!', '#ff0000');
                    alert('Игрок не найден. Проверьте ID.');
                } else {
                    showStatus('Ошибка: ' + err.type, '#ff0000');
                }
            });
            
            peer.on('connection', c => {
                console.log('Incoming connection from:', c.peer);
                conn = c;
                isSolo = false;
                gameMode = 'net';
                updateUI('net');
                setupConn();
                showStatus('Подключен: ' + c.peer.substring(0, 8));
            });
        } catch(e) {
            console.error('Failed to initialize PeerJS:', e);
        }
    }

    function connectToPeer(remoteId) {
        if (!peer) {
            alert('PeerJS не инициализирован');
            return;
        }
        showStatus('Подключение...', '#ffaa00');
        conn = peer.connect(remoteId);
        setupConn();
    }

    function setupConn() {
        if (!conn) return;
        
        conn.on('open', () => {
            console.log('✅ Connection opened');
            isSolo = false;
            gameMode = 'net';
            showStatus('Подключен!', '#00ff00');
        });
        
        conn.on('data', data => {
            if (data.t === 's') {
                opp.x = data.x; opp.y = data.y; opp.a = data.a; 
                opp.hp = data.hp; opp.state = data.state; opp.score = data.score;
            } else if (data.t === 'b') {
                bullets.push({x: data.x, y: data.y, a: data.a, owner: 'opp'});
            } else if (data.t === 'reset') {
                resetRound();
            }
        });
        
        conn.on('close', () => {
            console.log('Connection closed');
            isSolo = true;
            gameMode = 'ai-easy';
            updateUI('ai-easy');
            showStatus('Отключен', '#ff0000');
        });
        
        conn.on('error', err => {
            console.error('Connection error:', err);
            showStatus('Ошибка соединения', '#ff0000');
        });
    }

    const manager = nipplejs.create({
        zone: document.getElementById('joystick-zone'),
        mode: 'static', position: {left: '50%', top: '50%'},
        color: '#00d2ff', size: 100
    });

    manager.on('move', (evt, data) => {
        if (!gameActive) return;
        // Инвертируем угол чтобы верх был вверх
        // nipplejs возвращает угол где 0° = право, 90° = верх
        // Нам нужно: 0° = верх, 90° = право, 180° = низ, 270° = лево
        me.a = data.angle.degree - 90;
        if (me.a < 0) me.a += 360;
    });

    document.getElementById('fireBtn').addEventListener('click', () => {
        if (!gameActive || me.state !== 'alive') return;
        
        bullets.push({x: me.x, y: me.y, a: me.a, owner: 'me'});
        
        if (conn && conn.open) {
            conn.send({t: 'b', x: me.x, y: me.y, a: me.a});
        }
    });

    function initArcadeMode() {
        arcadeTargets = [];
        rings = [];
        enemies = [];
        checkpoints = [];
        me.score = 0;
        comboCounter = 0;
        waveNumber = 1;
        
        switch(gameMode) {
            case 'paratrooper':
                gameTimer = 60;
                spawnParatroopers();
                break;
            case 'balloon':
                gameTimer = 45;
                spawnBalloons();
                break;
            case 'cargo':
                gameTimer = 60;
                spawnCargo();
                break;
            case 'rings':
                gameTimer = 60;
                spawnRings();
                break;
            case 'survival':
                spawnEnemyWave();
                break;
            case 'escort':
                spawnEscortTarget();
                spawnEnemyWave();
                break;
            case 'race':
                gameTimer = 90;
                spawnCheckpoints();
                break;
        }
    }

    function spawnParatroopers() {
        for(let i=0; i<5; i++) {
            arcadeTargets.push({
                x: Math.random() * WORLD.w,
                y: -50,
                vx: (Math.random() - 0.5) * 2,
                vy: 3,
                type: 'paratrooper',
                hp: 1
            });
        }
    }

    function spawnBalloons() {
        const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff'];
        for(let i=0; i<8; i++) {
            arcadeTargets.push({
                x: Math.random() * WORLD.w,
                y: 300 + Math.random() * 1000,
                vx: (Math.random() - 0.5) * 3,
                vy: -1,
                type: 'balloon',
                color: colors[Math.floor(Math.random() * colors.length)],
                size: 30 + Math.random() * 20,
                hp: 1
            });
        }
    }

    function spawnCargo() {
        for(let i=0; i<6; i++) {
            arcadeTargets.push({
                x: Math.random() * WORLD.w,
                y: -50,
                vx: 0,
                vy: 5,
                type: 'cargo',
                hp: 1,
                rotation: 0
            });
        }
    }

    function spawnRings() {
        for(let i=0; i<10; i++) {
            rings.push({
                x: 300 + i * 250,
                y: 500 + Math.sin(i) * 400,
                size: 80,
                hit: false,
                order: i
            });
        }
    }

    function spawnEnemyWave() {
        const count = 3 + waveNumber;
        for(let i=0; i<count; i++) {
            enemies.push({
                x: Math.random() * WORLD.w,
                y: Math.random() * WORLD.h,
                a: Math.random() * 360,
                hp: 2,
                color: '#800080',
                state: 'alive'
            });
        }
    }

    function spawnEscortTarget() {
        escortTarget = {
            x: 200,
            y: WORLD.h / 2,
            a: 0,
            vx: 5,
            hp: 10,
            maxHp: 10,
            color: '#00ff00',
            state: 'alive'
        };
    }

    function spawnCheckpoints() {
        for(let i=0; i<15; i++) {
            checkpoints.push({
                x: 200 + i * 180,
                y: 400 + Math.sin(i * 0.5) * 300,
                hit: false,
                order: i
            });
        }
    }

    function resetRound() {
        me.x = 500; me.y = 500; me.a = 0; me.hp = me.max; me.state = 'alive';
        opp.x = 2500; opp.y = 1500; opp.a = 180; opp.hp = opp.max; opp.state = 'alive';
        bullets = [];
        
        if (isArcadeMode() && gameActive) {
            initArcadeMode();
        }
        
        if (conn && conn.open) {
            conn.send({t: 'reset'});
        }
    }

    function checkWin() {
        if (me.score >= scoreLimit) {
            endGame('ПОБЕДА!', ''); totalWinsMe++;
        } else if (opp.score >= scoreLimit) {
            endGame('ПОРАЖЕНИЕ!', ''); totalWinsOpp++;
        }
    }

    function endGame(msg, submsg = 'Следующий раунд через 3 сек...') {
        gameActive = false;
        gamePaused = true;
        startPauseBtn.textContent = '▶ СТАРТ';
        startPauseBtn.classList.add('paused');
        
        document.getElementById('result-text').innerText = msg;
        document.getElementById('result-subtext').innerText = submsg;
        document.getElementById('overlay').style.display = 'flex';
        document.getElementById('wins-me').innerText = totalWinsMe;
        document.getElementById('wins-opp').innerText = totalWinsOpp;
        
        setTimeout(() => {
            document.getElementById('overlay').style.display = 'none';
            if (!isArcadeMode()) {
                me.score = 0; opp.score = 0;
            }
            resetRound();
        }, 3000);
    }

    function respawn(obj) {
        obj.state = 'alive';
        obj.hp = obj.max;
        if (obj === me) { obj.x = 500; obj.y = 500; obj.a = 0; }
        else { obj.x = 2500; obj.y = 1500; obj.a = 180; }
    }

    function createPart(x, y, type, color = null) {
        if (type === 'explode') {
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

    function updateCombo() {
        const now = Date.now();
        if (now - lastHitTime < 2000) {
            comboCounter++;
            if (comboCounter > 1) {
                const comboEl = document.getElementById('combo-indicator');
                comboEl.textContent = `COMBO x${comboCounter}!`;
                comboEl.style.display = 'block';
                setTimeout(() => comboEl.style.display = 'none', 1000);
            }
        } else {
            comboCounter = 1;
        }
        lastHitTime = now;
    }

    function update() {
        if(!gameActive || gamePaused) return;
        propellerRotation += 0.9; 

        // Update timer for timed modes
        if (['balloon', 'rings', 'race'].includes(gameMode)) {
            gameTimer -= 1/60;
            document.getElementById('game-timer').textContent = Math.ceil(gameTimer);
            if (gameTimer <= 0) {
                endGame('ВРЕМЯ ВЫШЛО!', `Ваш счет: ${me.score}`);
                return;
            }
        }

        clouds.forEach(c => { c.x -= 0.6 * c.s; if(c.x < -200) c.x = WORLD.w + 200; });
        
        const wrap = (obj) => {
            if (obj.x < 0) obj.x = WORLD.w; if (obj.x > WORLD.w) obj.x = 0;
            if (obj.y < 0) obj.y = WORLD.h; if (obj.y > WORLD.h) obj.y = 0;
        };

        if(me.state === 'alive') {
            let r = me.a * Math.PI/180;
            me.x += Math.cos(r) * planeSpeed;
            me.y += Math.sin(r) * planeSpeed;
            wrap(me);
            if(me.hp < 3) createPart(me.x, me.y, 'smoke');
            if(me.hp <= 0) { 
                me.state = 'falling'; 
                me.dt = 90;
                if (!isArcadeMode()) {
                    opp.score++; 
                    checkWin();
                }
            }
        } else if (gameActive) {
            me.y += 10; me.a += 12; createPart(me.x, me.y, 'fire');
            if(--me.dt <= 0) { 
                createPart(me.x, me.y, 'explode', me.color);
                if (isArcadeMode()) {
                    endGame('ПОРАЖЕНИЕ!', `Ваш счет: ${me.score}`);
                } else {
                    respawn(me);
                }
            }
        }

        // Arcade mode updates
        if (gameMode === 'paratrooper') {
            arcadeTargets.forEach((t, i) => {
                t.x += t.vx;
                t.y += t.vy;
                if (t.y > WORLD.h + 100) {
                    arcadeTargets.splice(i, 1);
                    if (arcadeTargets.length < 3) spawnParatroopers();
                }
            });
        } else if (gameMode === 'balloon') {
            arcadeTargets.forEach((t, i) => {
                t.x += t.vx;
                t.y += t.vy;
                if (t.y < -100) {
                    arcadeTargets.splice(i, 1);
                    if (arcadeTargets.length < 5) spawnBalloons();
                }
            });
        } else if (gameMode === 'cargo') {
            arcadeTargets.forEach((t, i) => {
                t.y += t.vy;
                t.rotation += 2;
                if (t.y > WORLD.h + 100) {
                    arcadeTargets.splice(i, 1);
                    if (arcadeTargets.length < 4) spawnCargo();
                }
            });
        } else if (gameMode === 'rings') {
            rings.forEach(ring => {
                const dist = Math.hypot(me.x - ring.x, me.y - ring.y);
                if (dist < ring.size && !ring.hit) {
                    ring.hit = true;
                    me.score += 10;
                    updateCombo();
                    createPart(ring.x, ring.y, 'smoke');
                }
            });
            if (rings.filter(r => r.hit).length === rings.length) {
                endGame('ПОБЕДА!', `Время: ${(60 - gameTimer).toFixed(1)}с`);
            }
        } else if (gameMode === 'survival') {
            enemies.forEach((e, i) => {
                if (e.state === 'alive') {
                    let targetA = Math.atan2(me.y - e.y, me.x - e.x) * 180 / Math.PI;
                    let diff = targetA - e.a;
                    while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
                    e.a += diff * 0.08;
                    let r = e.a * Math.PI/180;
                    e.x += Math.cos(r) * 12;
                    e.y += Math.sin(r) * 12;
                    wrap(e);
                    
                    if (Math.random() < 0.02 && Math.abs(diff) < 30) {
                        bullets.push({x: e.x, y: e.y, a: e.a, owner: 'enemy'});
                    }
                    
                    if (e.hp <= 0) {
                        e.state = 'dead';
                        createPart(e.x, e.y, 'explode', e.color);
                        me.score += 10;
                        updateCombo();
                    }
                }
            });
            
            if (enemies.filter(e => e.state === 'alive').length === 0) {
                waveNumber++;
                spawnEnemyWave();
            }
        } else if (gameMode === 'escort') {
            if (escortTarget && escortTarget.state === 'alive') {
                escortTarget.x += escortTarget.vx;
                if (escortTarget.x > WORLD.w) {
                    endGame('ПОБЕДА!', `Транспорт доставлен! Счет: ${me.score}`);
                    return;
                }
                
                if (escortTarget.hp <= 0) {
                    escortTarget.state = 'dead';
                    createPart(escortTarget.x, escortTarget.y, 'explode', escortTarget.color);
                    endGame('ПОРАЖЕНИЕ!', 'Транспорт уничтожен!');
                    return;
                }
            }
            
            enemies.forEach((e, i) => {
                if (e.state === 'alive') {
                    let targetA = Math.atan2(escortTarget.y - e.y, escortTarget.x - e.x) * 180 / Math.PI;
                    let diff = targetA - e.a;
                    while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
                    e.a += diff * 0.08;
                    let r = e.a * Math.PI/180;
                    e.x += Math.cos(r) * 10;
                    e.y += Math.sin(r) * 10;
                    wrap(e);
                    
                    if (Math.random() < 0.03) {
                        bullets.push({x: e.x, y: e.y, a: e.a, owner: 'enemy'});
                    }
                    
                    if (e.hp <= 0) {
                        e.state = 'dead';
                        createPart(e.x, e.y, 'explode', e.color);
                        me.score += 10;
                    }
                }
            });
            
            if (enemies.filter(e => e.state === 'alive').length === 0) {
                spawnEnemyWave();
            }
        } else if (gameMode === 'race') {
            checkpoints.forEach(cp => {
                const dist = Math.hypot(me.x - cp.x, me.y - cp.y);
                if (dist < 60 && !cp.hit) {
                    cp.hit = true;
                    me.score += 10;
                    createPart(cp.x, cp.y, 'smoke');
                }
            });
            
            if (checkpoints.filter(cp => cp.hit).length === checkpoints.length) {
                endGame('ФИНИШ!', `Время: ${(90 - gameTimer).toFixed(1)}с`);
            }
        }

        // Network game updates
        if(conn && conn.open && !isSolo) {
            conn.send({ t: 's', x: me.x, y: me.y, a: me.a, hp: me.hp, state: me.state, score: me.score });
        }

        if(isSolo && !isArcadeMode()) {
            if(opp.state === 'alive') {
                let targetA = Math.atan2(me.y - opp.y, me.x - opp.x) * 180 / Math.PI;
                let diff = targetA - opp.a;
                while(diff < -180) diff += 360; while(diff > 180) diff -= 360;
                
                let turnSpeed = (difficulty === 'hard' ? 0.12 : 0.06);
                opp.a += diff * turnSpeed; 
                let r = opp.a * Math.PI/180;
                let oppSpeed = (difficulty === 'hard' ? planeSpeed : planeSpeed * 0.8);
                
                opp.x += Math.cos(r) * oppSpeed;
                opp.y += Math.sin(r) * oppSpeed;
                wrap(opp);
                if(opp.hp < 3) createPart(opp.x, opp.y, 'smoke');
                
                let shootChance = (difficulty==='hard'?0.04:0.015);
                if(Math.random() < shootChance && Math.abs(diff) < 20) {
                    bullets.push({x:opp.x, y:opp.y, a:opp.a, owner:'opp'});
                }
                
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
            
            // Check arcade targets
            if (b.owner === 'me' && isArcadeMode()) {
                arcadeTargets.forEach((t, ti) => {
                    const dist = Math.hypot(b.x - t.x, b.y - t.y);
                    let hitRange = 50;
                    
                    if (gameMode === 'paratrooper' || gameMode === 'cargo') {
                        const targetDist = Math.hypot(me.x - t.x, me.y - t.y);
                        const inRange = Math.abs(targetDist - precisionDistance) <= precisionTolerance;
                        hitRange = inRange ? 80 : 40;
                    }
                    
                    if (dist < hitRange) {
                        t.hp--;
                        bullets.splice(i, 1);
                        if (t.hp <= 0) {
                            let points = 5;
                            if (gameMode === 'paratrooper' || gameMode === 'cargo') {
                                const targetDist = Math.hypot(me.x - t.x, me.y - t.y);
                                const inRange = Math.abs(targetDist - precisionDistance) <= precisionTolerance;
                                points = inRange ? 15 : 5;
                            }
                            me.score += points * (comboCounter || 1);
                            updateCombo();
                            createPart(t.x, t.y, 'explode', t.color || '#ffaa00');
                            arcadeTargets.splice(ti, 1);
                        }
                    }
                });
                
                // Check enemies
                enemies.forEach((e, ei) => {
                    if (e.state === 'alive' && Math.hypot(b.x - e.x, b.y - e.y) < 65) {
                        e.hp--;
                        bullets.splice(i, 1);
                    }
                });
            }
            
            // Check PvP targets
            if (!isArcadeMode()) {
                let target = b.owner === 'me' ? opp : me;
                if(target.state === 'alive' && Math.hypot(b.x-target.x, b.y-target.y) < 65) {
                    target.hp--;
                    bullets.splice(i, 1);
                }
            }
            
            // Check escort target and enemies hitting player/escort
            if (gameMode === 'escort') {
                if (b.owner === 'enemy') {
                    if (escortTarget && escortTarget.state === 'alive' && Math.hypot(b.x - escortTarget.x, b.y - escortTarget.y) < 70) {
                        escortTarget.hp--;
                        bullets.splice(i, 1);
                    }
                    if (me.state === 'alive' && Math.hypot(b.x - me.x, b.y - me.y) < 65) {
                        me.hp--;
                        bullets.splice(i, 1);
                    }
                }
            }
            
            if (gameMode === 'survival' && b.owner === 'enemy') {
                if (me.state === 'alive' && Math.hypot(b.x - me.x, b.y - me.y) < 65) {
                    me.hp--;
                    bullets.splice(i, 1);
                }
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

        // Применяем зум камеры
        const baseScale = canvas.width / WORLD.w;
        ctx.scale(baseScale * cameraZoom, (canvas.height / WORLD.h) * cameraZoom);
        
        // Центрируем камеру на игроке при зуме
        if (cameraZoom !== 1.0) {
            const offsetX = (WORLD.w / 2 - me.x) * (cameraZoom - 1.0) / cameraZoom;
            const offsetY = (WORLD.h / 2 - me.y) * (cameraZoom - 1.0) / cameraZoom;
            ctx.translate(offsetX, offsetY);
        }
        
        // Draw clouds
        clouds.forEach(c => {
            ctx.globalAlpha = c.op; ctx.fillStyle = "white";
            ctx.beginPath(); ctx.arc(c.x, c.y, 45*c.s, 0, 7); ctx.fill();
        });
        ctx.globalAlpha = 1.0;

        // Draw particles
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

        // Draw arcade targets
        if (gameMode === 'paratrooper') {
            arcadeTargets.forEach(t => {
                // Parachute
                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.beginPath();
                ctx.arc(t.x, t.y - 40, 35, 0, Math.PI * 2);
                ctx.fill();
                
                // Lines
                ctx.strokeStyle = '#666';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(t.x - 30, t.y - 40);
                ctx.lineTo(t.x, t.y);
                ctx.moveTo(t.x + 30, t.y - 40);
                ctx.lineTo(t.x, t.y);
                ctx.stroke();
                
                // Person
                ctx.fillStyle = '#ff6600';
                ctx.fillRect(t.x - 8, t.y, 16, 25);
                ctx.beginPath();
                ctx.arc(t.x, t.y - 10, 10, 0, Math.PI * 2);
                ctx.fill();
            });
        } else if (gameMode === 'balloon') {
            arcadeTargets.forEach(t => {
                ctx.fillStyle = t.color;
                ctx.beginPath();
                ctx.arc(t.x, t.y, t.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.3)';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // String
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(t.x, t.y + t.size);
                ctx.lineTo(t.x, t.y + t.size + 30);
                ctx.stroke();
            });
        } else if (gameMode === 'cargo') {
            arcadeTargets.forEach(t => {
                ctx.save();
                ctx.translate(t.x, t.y);
                ctx.rotate(t.rotation * Math.PI / 180);
                
                // Box
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(-25, -25, 50, 50);
                ctx.strokeStyle = '#654321';
                ctx.lineWidth = 3;
                ctx.strokeRect(-25, -25, 50, 50);
                
                // Parachute above
                ctx.restore();
                ctx.fillStyle = 'rgba(255, 100, 0, 0.7)';
                ctx.beginPath();
                ctx.arc(t.x, t.y - 50, 30, 0, Math.PI * 2);
                ctx.fill();
            });
        } else if (gameMode === 'rings') {
            rings.forEach(r => {
                if (!r.hit) {
                    ctx.strokeStyle = '#00ff00';
                    ctx.lineWidth = 8;
                    ctx.beginPath();
                    ctx.arc(r.x, r.y, r.size, 0, Math.PI * 2);
                    ctx.stroke();
                }
            });
        } else if (gameMode === 'race') {
            checkpoints.forEach(cp => {
                if (!cp.hit) {
                    ctx.strokeStyle = '#ff00ff';
                    ctx.lineWidth = 6;
                    ctx.setLineDash([10, 10]);
                    ctx.beginPath();
                    ctx.moveTo(cp.x, cp.y - 100);
                    ctx.lineTo(cp.x, cp.y + 100);
                    ctx.stroke();
                    ctx.setLineDash([]);
                }
            });
        }

        // Draw escort target
        if (gameMode === 'escort' && escortTarget && escortTarget.state === 'alive') {
            drawPlane({x: escortTarget.x, y: escortTarget.y, a: escortTarget.a, state: 'alive'}, escortTarget.color);
            
            // HP bar
            ctx.fillStyle = '#444';
            ctx.fillRect(escortTarget.x - 50, escortTarget.y - 100, 100, 10);
            ctx.fillStyle = '#00ff00';
            ctx.fillRect(escortTarget.x - 50, escortTarget.y - 100, 100 * (escortTarget.hp / escortTarget.maxHp), 10);
        }

        // Draw enemies
        enemies.forEach(e => {
            if (e.state === 'alive') {
                drawPlane(e, e.color);
            }
        });

        const drawPlane = (p, col) => {
            if(p.state !== 'alive' && (!p.dt || p.dt <= 0)) return;
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

        drawPlane(me, me.color);
        if (!isArcadeMode()) drawPlane(opp, opp.color);
        
        bullets.forEach(b => { 
            ctx.fillStyle = b.owner === 'enemy' ? '#ff00ff' : 'yellow'; 
            ctx.beginPath(); 
            ctx.arc(b.x, b.y, 12, 0, 7); 
            ctx.fill(); 
        });
        ctx.restore();

        document.getElementById('hp-fill').style.width = (me.hp/me.max*100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        if (!isArcadeMode()) {
            document.getElementById('sc-opp').innerText = opp.score;
        }
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    
    initPeer();
    loop();
</script>
"""

components.html(game_html, height=600)