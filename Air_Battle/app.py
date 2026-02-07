import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AN-2 Ace Combat: Tactical VFX", layout="wide")

game_html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 5px; background: #111; font-family: sans-serif; overflow-x: hidden; color: white; }
    
    #top-bar { 
        background: #222; 
        padding: 6px 12px;
        border-radius: 6px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        gap: 10px; 
        margin-bottom: 3px; 
        font-size: 9px;
        box-sizing: border-box;
    }
    
    #viewport-container { position: relative; width: 100%; margin: 0 auto; touch-action: none; }
    #viewport { 
        position: relative; width: 100%; height: 350px; 
        background: #87CEEB; border: 2px solid #444; overflow: hidden; border-radius: 8px; 
    }
    canvas { width: 100%; height: 100%; display: block; }

    /* START SCREEN */
    #start-screen {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 150;
        border-radius: 8px;
    }
    
    #start-screen h1 {
        font-size: 36px;
        margin-bottom: 20px;
        color: #00d2ff;
        text-shadow: 0 0 20px #00d2ff;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    #start-btn {
        width: 200px;
        height: 60px;
        background: linear-gradient(145deg, #ff4b4b, #ff6b6b);
        color: white;
        border: none;
        border-radius: 30px;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 8px 15px rgba(255, 75, 75, 0.4);
        transition: all 0.3s;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    #start-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px rgba(255, 75, 75, 0.6);
    }
    
    #start-btn:active {
        transform: translateY(0);
        box-shadow: 0 5px 10px rgba(255, 75, 75, 0.4);
    }

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
        touch-action: none;
    }
    #fireBtn:active { transform: translateY(3px); box-shadow: 0 2px #b33030; }

    #hp-zone { 
        flex: 1; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        gap: 5px; 
        padding-bottom: 10px; 
    }
    
    /* Контейнер для кнопки мертвой петли */
    #barrel-roll-container {
        display: flex;
        justify-content: center;
        margin-bottom: 8px;
    }
    
    #barrel-roll-btn {
        background: linear-gradient(145deg, #9b59b6, #8e44ad);
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px #6c3483;
        transition: all 0.2s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    #barrel-roll-btn:hover {
        background: linear-gradient(145deg, #a569bd, #9b59b6);
    }
    
    #barrel-roll-btn:active {
        transform: translateY(2px);
        box-shadow: 0 2px #6c3483;
    }
    
    #barrel-roll-btn:disabled {
        background: #555;
        cursor: not-allowed;
        box-shadow: 0 2px #333;
    }
    
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
        background: #00d2ff;
        color: black;
        border: none;
        padding: 6px 12px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: bold;
        cursor: pointer;
    }
    
    #net-status {
        font-size: 10px;
        color: #888;
        margin-top: 5px;
    }
</style>

<div id="top-bar">
    <div style="flex: 1; display: flex; align-items: center; gap: 6px;">
        <span>⚔️ <span id="sc-me">0</span></span>
        <span>🏆 <span id="sc-opp">0</span></span>
    </div>
    <div style="flex: 1; display: flex; justify-content: center; align-items: center; gap: 8px;">
        <button class="btn-start-pause" id="start-pause-btn">START</button>
        <button class="btn-settings" id="open-sidebar-btn">⚙️ SETTINGS</button>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 4px; font-size: 8px;">
        <span>🎯 <span id="current-mode-label">Classic</span></span>
    </div>
</div>

<div id="viewport-container">
    <div id="viewport">
        <!-- START SCREEN -->
        <div id="start-screen">
            <h1>AN-2 ACE COMBAT</h1>
            <button id="start-btn">START</button>
        </div>
        
        <canvas id="gameCanvas"></canvas>
        <div id="overlay"><h2 id="overlay-text"></h2></div>
    </div>
</div>

<div id="lower-area">
    <div id="fire-zone">
        <button id="fireBtn">🔥<br>FIRE</button>
    </div>
    <div id="hp-zone">
        <div id="barrel-roll-container">
            <button id="barrel-roll-btn">🔄 BARREL ROLL</button>
        </div>
        <div class="hp-label">HP PILOT</div>
        <div id="hp-bar-container">
            <div id="hp-fill"></div>
        </div>
    </div>
    <div id="joy-zone">
        <div id="joystick-zone" id="joystick"></div>
    </div>
</div>

<!-- SIDEBAR -->
<div id="sidebar">
    <button id="close-sidebar">×</button>
    <h3>⚙️ Settings</h3>
    
    <div class="setting-group">
        <span class="setting-label">Camera Zoom</span>
        <div class="slider-container">
            <input type="range" id="zoom-slider" class="slider" min="0.5" max="2.0" step="0.1" value="1.0">
            <span class="slider-value" id="zoom-value">1.0x</span>
        </div>
    </div>
    
    <div class="setting-group">
        <span class="setting-label">Game Mode</span>
        <button class="btn-mode active-mode" data-mode="classic">
            <span class="mode-icon">⚔️</span> Classic Dogfight
        </button>
        <button class="btn-mode" data-mode="paratrooper">
            <span class="mode-icon">🪂</span> Paratrooper Hunt
        </button>
        <button class="btn-mode" data-mode="balloon">
            <span class="mode-icon">🎈</span> Balloon Pop
        </button>
        <button class="btn-mode" data-mode="cargo">
            <span class="mode-icon">📦</span> Cargo Intercept
        </button>
        <button class="btn-mode" data-mode="rings">
            <span class="mode-icon">💍</span> Ring Chase
        </button>
        <button class="btn-mode" data-mode="race">
            <span class="mode-icon">🏁</span> Speed Race
        </button>
        <button class="btn-mode" data-mode="survival">
            <span class="mode-icon">💀</span> Survival Mode
        </button>
        <button class="btn-mode" data-mode="escort">
            <span class="mode-icon">🛡️</span> Escort Mission
        </button>
    </div>
    
    <div class="setting-group">
        <span class="setting-label">Multiplayer (Experimental)</span>
        <button id="toggle-net-btn" class="btn-mode">
            <span class="mode-icon">🌐</span> Enable Network Play
        </button>
        <div id="net-controls">
            <input type="text" id="peer-id-input" placeholder="Your Peer ID">
            <input type="text" id="remote-peer-input" placeholder="Remote Peer ID">
            <button id="connect-btn">Connect</button>
            <div id="net-status">Not connected</div>
        </div>
    </div>
</div>

<script src="https://unpkg.com/peerjs@1.4.7/dist/peerjs.min.js"></script>
<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const WORLD = { w: 2000, h: 1200 };
    canvas.width = WORLD.w;
    canvas.height = WORLD.h;

    let gameStarted = false;
    let gamePaused = false;
    let gameMode = 'classic';
    let cameraZoom = 1.0;
    let screenShake = 0;
    let propellerRotation = 0;

    // Barrel roll variables
    let isBarrelRolling = false;
    let barrelRollProgress = 0;
    let barrelRollCooldown = 0;
    const BARREL_ROLL_DURATION = 60; // frames
    const BARREL_ROLL_COOLDOWN = 180; // frames (3 seconds at 60fps)

    let me = { x: WORLD.w/2 - 200, y: WORLD.h/2, vx: 0, vy: 0, a: 0, hp: 100, max: 100, score: 0, state: 'alive', color: "#ffcc00", dt: 0 };
    let opp = { x: WORLD.w/2 + 200, y: WORLD.h/2, vx: 0, vy: 0, a: 180, hp: 100, max: 100, score: 0, state: 'alive', color: "#ff4444", dt: 0 };
    let bullets = [];
    let particles = [];
    let clouds = [];
    let enemies = [];
    let arcadeTargets = [];
    let rings = [];
    let checkpoints = [];
    let escortTarget = null;

    // Multiplayer
    let peer = null;
    let conn = null;
    let isHost = false;
    let netEnabled = false;

    // Controls
    let joyActive = false, joyX = 0, joyY = 0;
    const fireBtn = document.getElementById('fireBtn');
    const joyZone = document.getElementById('joystick-zone');

    // START SCREEN
    const startScreen = document.getElementById('start-screen');
    const startBtn = document.getElementById('start-btn');
    const startPauseBtn = document.getElementById('start-pause-btn');

    startBtn.addEventListener('click', () => {
        startScreen.style.display = 'none';
        gameStarted = true;
        gamePaused = false;
        startPauseBtn.innerText = 'PAUSE';
        startPauseBtn.classList.remove('paused');
    });

    startPauseBtn.addEventListener('click', () => {
        if (!gameStarted) {
            startScreen.style.display = 'none';
            gameStarted = true;
            gamePaused = false;
            startPauseBtn.innerText = 'PAUSE';
            startPauseBtn.classList.remove('paused');
        } else {
            gamePaused = !gamePaused;
            if (gamePaused) {
                startPauseBtn.innerText = 'RESUME';
                startPauseBtn.classList.add('paused');
            } else {
                startPauseBtn.innerText = 'PAUSE';
                startPauseBtn.classList.remove('paused');
            }
        }
    });

    // BARREL ROLL BUTTON
    const barrelRollBtn = document.getElementById('barrel-roll-btn');
    barrelRollBtn.addEventListener('click', () => {
        if (!isBarrelRolling && barrelRollCooldown === 0 && me.state === 'alive' && gameStarted && !gamePaused) {
            isBarrelRolling = true;
            barrelRollProgress = 0;
            barrelRollCooldown = BARREL_ROLL_COOLDOWN;
        }
    });

    // SIDEBAR
    const sidebar = document.getElementById('sidebar');
    const openSidebarBtn = document.getElementById('open-sidebar-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar');

    openSidebarBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
    });

    closeSidebarBtn.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });

    // ZOOM SLIDER
    const zoomSlider = document.getElementById('zoom-slider');
    const zoomValue = document.getElementById('zoom-value');

    zoomSlider.addEventListener('input', (e) => {
        cameraZoom = parseFloat(e.target.value);
        zoomValue.innerText = cameraZoom.toFixed(1) + 'x';
    });

    // MODE BUTTONS
    document.querySelectorAll('.btn-mode[data-mode]').forEach(btn => {
        btn.addEventListener('click', () => {
            const newMode = btn.getAttribute('data-mode');
            if (newMode !== gameMode) {
                gameMode = newMode;
                document.querySelectorAll('.btn-mode[data-mode]').forEach(b => b.classList.remove('active-mode'));
                btn.classList.add('active-mode');
                document.getElementById('current-mode-label').innerText = btn.innerText.trim();
                resetGame();
                sidebar.classList.remove('open');
            }
        });
    });

    // NETWORK TOGGLE
    const toggleNetBtn = document.getElementById('toggle-net-btn');
    const netControls = document.getElementById('net-controls');
    toggleNetBtn.addEventListener('click', () => {
        netEnabled = !netEnabled;
        netControls.style.display = netEnabled ? 'block' : 'none';
        toggleNetBtn.classList.toggle('active-mode', netEnabled);
    });

    // Initialize clouds
    for (let i = 0; i < 20; i++) {
        clouds.push({ x: Math.random() * WORLD.w, y: Math.random() * WORLD.h, s: 0.5 + Math.random(), op: 0.3 + Math.random() * 0.4 });
    }

    function isArcadeMode() {
        return ['paratrooper', 'balloon', 'cargo', 'rings', 'race'].includes(gameMode);
    }

    function resetGame() {
        me = { x: WORLD.w/2 - 200, y: WORLD.h/2, vx: 0, vy: 0, a: 0, hp: 100, max: 100, score: 0, state: 'alive', color: "#ffcc00", dt: 0 };
        opp = { x: WORLD.w/2 + 200, y: WORLD.h/2, vx: 0, vy: 0, a: 180, hp: 100, max: 100, score: 0, state: 'alive', color: "#ff4444", dt: 0 };
        bullets = [];
        particles = [];
        enemies = [];
        arcadeTargets = [];
        rings = [];
        checkpoints = [];
        escortTarget = null;
        isBarrelRolling = false;
        barrelRollProgress = 0;
        barrelRollCooldown = 0;
        document.getElementById('overlay').style.display = 'none';

        if (gameMode === 'paratrooper') {
            for (let i = 0; i < 10; i++) {
                arcadeTargets.push({
                    x: Math.random() * (WORLD.w - 200) + 100,
                    y: -100 - Math.random() * 500,
                    vy: 1 + Math.random()
                });
            }
        } else if (gameMode === 'balloon') {
            for (let i = 0; i < 15; i++) {
                arcadeTargets.push({
                    x: Math.random() * (WORLD.w - 200) + 100,
                    y: Math.random() * WORLD.h,
                    size: 30 + Math.random() * 20,
                    color: `hsl(${Math.random() * 360}, 80%, 60%)`
                });
            }
        } else if (gameMode === 'cargo') {
            for (let i = 0; i < 8; i++) {
                arcadeTargets.push({
                    x: Math.random() * (WORLD.w - 200) + 100,
                    y: -100 - Math.random() * 400,
                    vy: 1.5,
                    rotation: 0
                });
            }
        } else if (gameMode === 'rings') {
            for (let i = 0; i < 10; i++) {
                rings.push({
                    x: 200 + i * 180,
                    y: 300 + Math.sin(i) * 200,
                    size: 60,
                    hit: false
                });
            }
        } else if (gameMode === 'race') {
            for (let i = 0; i < 8; i++) {
                checkpoints.push({
                    x: 300 + i * 220,
                    y: WORLD.h / 2,
                    hit: false
                });
            }
        } else if (gameMode === 'survival') {
            // Spawn initial enemies for survival mode
            spawnEnemyWave();
        } else if (gameMode === 'escort') {
            // Create escort target
            escortTarget = {
                x: WORLD.w / 2,
                y: WORLD.h / 2 - 150,
                a: 90,
                vx: 2,
                vy: 0,
                hp: 50,
                maxHp: 50,
                state: 'alive',
                color: '#00ff00'
            };
            // Spawn initial enemies for escort mode
            spawnEnemyWave();
        }
    }

    function spawnEnemyWave() {
        const count = gameMode === 'survival' ? 3 : 2;
        for (let i = 0; i < count; i++) {
            const side = Math.random() > 0.5;
            enemies.push({
                x: side ? -100 : WORLD.w + 100,
                y: Math.random() * WORLD.h,
                vx: side ? 3 : -3,
                vy: 0,
                a: side ? 0 : 180,
                hp: 30,
                state: 'alive',
                color: '#ff00ff',
                shootTimer: Math.random() * 60
            });
        }
    }

    resetGame();

    // Touch/mouse for joystick
    function handleJoyStart(e) {
        if (!gameStarted || gamePaused) return;
        joyActive = true;
        handleJoyMove(e);
    }
    function handleJoyMove(e) {
        if (!joyActive) return;
        const rect = joyZone.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const touch = e.touches ? e.touches[0] : e;
        const dx = touch.clientX - centerX;
        const dy = touch.clientY - centerY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = rect.width / 2;
        if (dist > maxDist) {
            joyX = (dx / dist) * maxDist;
            joyY = (dy / dist) * maxDist;
        } else {
            joyX = dx;
            joyY = dy;
        }
    }
    function handleJoyEnd() {
        joyActive = false;
        joyX = 0;
        joyY = 0;
    }

    joyZone.addEventListener('mousedown', handleJoyStart);
    joyZone.addEventListener('mousemove', handleJoyMove);
    joyZone.addEventListener('mouseup', handleJoyEnd);
    joyZone.addEventListener('mouseleave', handleJoyEnd);
    joyZone.addEventListener('touchstart', handleJoyStart);
    joyZone.addEventListener('touchmove', handleJoyMove);
    joyZone.addEventListener('touchend', handleJoyEnd);

    // Fire button
    let fireReady = true;
    fireBtn.addEventListener('mousedown', fireBullet);
    fireBtn.addEventListener('touchstart', (e) => { e.preventDefault(); fireBullet(); });

    function fireBullet() {
        if (!gameStarted || gamePaused || me.state !== 'alive') return;
        if (!fireReady) return;
        fireReady = false;
        setTimeout(() => fireReady = true, 200);
        
        const rad = me.a * Math.PI / 180;
        bullets.push({
            x: me.x + Math.cos(rad) * 50,
            y: me.y + Math.sin(rad) * 50,
            vx: Math.cos(rad) * 20 + me.vx,
            vy: Math.sin(rad) * 20 + me.vy,
            owner: 'me'
        });
        
        if (conn && netEnabled) {
            conn.send({ type: 'fire', x: me.x, y: me.y, a: me.a, vx: me.vx, vy: me.vy });
        }
    }

    function update() {
        if (!gameStarted || gamePaused) return;

        propellerRotation += 0.5;

        // Update barrel roll cooldown
        if (barrelRollCooldown > 0) {
            barrelRollCooldown--;
            barrelRollBtn.disabled = true;
            barrelRollBtn.innerText = `🔄 ${Math.ceil(barrelRollCooldown / 60)}s`;
        } else {
            barrelRollBtn.disabled = false;
            barrelRollBtn.innerText = '🔄 BARREL ROLL';
        }

        // Update barrel roll
        if (isBarrelRolling) {
            barrelRollProgress++;
            if (barrelRollProgress >= BARREL_ROLL_DURATION) {
                isBarrelRolling = false;
                barrelRollProgress = 0;
            }
        }

        // Player movement
        if (me.state === 'alive') {
            const speed = isBarrelRolling ? 12 : 8;
            const turnRate = isBarrelRolling ? 8 : 5;
            
            if (joyActive) {
                const joyAngle = Math.atan2(joyY, joyX) * 180 / Math.PI;
                let diff = joyAngle - me.a;
                while (diff > 180) diff -= 360;
                while (diff < -180) diff += 360;
                me.a += Math.sign(diff) * Math.min(Math.abs(diff), turnRate);
            }

            const rad = me.a * Math.PI / 180;
            me.vx = Math.cos(rad) * speed;
            me.vy = Math.sin(rad) * speed;
            me.x += me.vx;
            me.y += me.vy;

            // Keep player in bounds
            me.x = Math.max(100, Math.min(WORLD.w - 100, me.x));
            me.y = Math.max(100, Math.min(WORLD.h - 100, me.y));

            if (me.hp <= 0) {
                me.state = 'dead';
                me.dt = 60;
                for (let i = 0; i < 30; i++) {
                    particles.push({
                        x: me.x, y: me.y,
                        vx: (Math.random() - 0.5) * 10,
                        vy: (Math.random() - 0.5) * 10,
                        life: 1, type: 'fire'
                    });
                }
                showGameOver('GAME OVER');
            }
        } else if (me.dt > 0) {
            me.dt--;
        }

        // Opponent AI (classic mode only)
        if (gameMode === 'classic' && opp.state === 'alive') {
            const dx = me.x - opp.x, dy = me.y - opp.y;
            const targetAngle = Math.atan2(dy, dx) * 180 / Math.PI;
            let diff = targetAngle - opp.a;
            while (diff > 180) diff -= 360;
            while (diff < -180) diff += 360;
            opp.a += Math.sign(diff) * 3;

            const rad = opp.a * Math.PI / 180;
            opp.vx = Math.cos(rad) * 6;
            opp.vy = Math.sin(rad) * 6;
            opp.x += opp.vx;
            opp.y += opp.vy;

            opp.x = Math.max(100, Math.min(WORLD.w - 100, opp.x));
            opp.y = Math.max(100, Math.min(WORLD.h - 100, opp.y));

            if (Math.random() < 0.02) {
                bullets.push({
                    x: opp.x + Math.cos(rad) * 50,
                    y: opp.y + Math.sin(rad) * 50,
                    vx: Math.cos(rad) * 18 + opp.vx,
                    vy: Math.sin(rad) * 18 + opp.vy,
                    owner: 'opp'
                });
            }

            if (opp.hp <= 0) {
                opp.state = 'dead';
                opp.dt = 60;
                me.score++;
                for (let i = 0; i < 30; i++) {
                    particles.push({
                        x: opp.x, y: opp.y,
                        vx: (Math.random() - 0.5) * 10,
                        vy: (Math.random() - 0.5) * 10,
                        life: 1, type: 'fire'
                    });
                }
                showGameOver('VICTORY!');
            }
        } else if (gameMode === 'classic' && opp.dt > 0) {
            opp.dt--;
        }

        // Enemy AI for survival and escort modes
        if ((gameMode === 'survival' || gameMode === 'escort') && me.state === 'alive') {
            enemies.forEach((e, idx) => {
                if (e.state !== 'alive') return;

                // Choose target based on mode
                let target = me;
                if (gameMode === 'escort' && escortTarget && escortTarget.state === 'alive') {
                    // 50% chance to target escort, 50% player
                    if (Math.random() < 0.5) {
                        target = escortTarget;
                    }
                }

                const dx = target.x - e.x;
                const dy = target.y - e.y;
                const targetAngle = Math.atan2(dy, dx) * 180 / Math.PI;
                let diff = targetAngle - e.a;
                while (diff > 180) diff -= 360;
                while (diff < -180) diff += 360;
                e.a += Math.sign(diff) * 4;

                const rad = e.a * Math.PI / 180;
                e.vx = Math.cos(rad) * 5;
                e.vy = Math.sin(rad) * 5;
                e.x += e.vx;
                e.y += e.vy;

                // Keep enemies in bounds
                if (e.x < -200 || e.x > WORLD.w + 200 || e.y < -200 || e.y > WORLD.h + 200) {
                    e.x = Math.max(100, Math.min(WORLD.w - 100, e.x));
                    e.y = Math.max(100, Math.min(WORLD.h - 100, e.y));
                }

                // Enemy shooting
                e.shootTimer--;
                if (e.shootTimer <= 0) {
                    e.shootTimer = 40 + Math.random() * 60;
                    bullets.push({
                        x: e.x + Math.cos(rad) * 50,
                        y: e.y + Math.sin(rad) * 50,
                        vx: Math.cos(rad) * 18 + e.vx,
                        vy: Math.sin(rad) * 18 + e.vy,
                        owner: 'enemy'
                    });
                }

                // Check if enemy destroyed
                if (e.hp <= 0) {
                    e.state = 'dead';
                    me.score++;
                    for (let i = 0; i < 20; i++) {
                        particles.push({
                            x: e.x, y: e.y,
                            vx: (Math.random() - 0.5) * 10,
                            vy: (Math.random() - 0.5) * 10,
                            life: 1, type: 'fire'
                        });
                    }
                    enemies.splice(idx, 1);
                }
            });

            // Spawn new enemies periodically
            if (Math.random() < 0.01) {
                spawnEnemyWave();
            }
        }

        // Update escort target
        if (gameMode === 'escort' && escortTarget && escortTarget.state === 'alive') {
            escortTarget.x += escortTarget.vx;
            
            // Bounce escort target at edges
            if (escortTarget.x < 200 || escortTarget.x > WORLD.w - 200) {
                escortTarget.vx *= -1;
                escortTarget.a = escortTarget.vx > 0 ? 90 : -90;
            }

            if (escortTarget.hp <= 0) {
                escortTarget.state = 'dead';
                for (let i = 0; i < 30; i++) {
                    particles.push({
                        x: escortTarget.x, y: escortTarget.y,
                        vx: (Math.random() - 0.5) * 10,
                        vy: (Math.random() - 0.5) * 10,
                        life: 1, type: 'fire'
                    });
                }
                showGameOver('MISSION FAILED');
            }
        }

        // Arcade targets
        if (gameMode === 'paratrooper') {
            arcadeTargets.forEach((t, i) => {
                t.y += t.vy;
                if (t.y > WORLD.h + 100) {
                    t.y = -100;
                    t.x = Math.random() * (WORLD.w - 200) + 100;
                }
            });
        } else if (gameMode === 'cargo') {
            arcadeTargets.forEach(t => {
                t.y += t.vy;
                t.rotation += 2;
                if (t.y > WORLD.h + 100) {
                    t.y = -100;
                    t.x = Math.random() * (WORLD.w - 200) + 100;
                }
            });
        }

        // Rings
        if (gameMode === 'rings') {
            rings.forEach(r => {
                if (!r.hit && Math.hypot(me.x - r.x, me.y - r.y) < r.size) {
                    r.hit = true;
                    me.score += 10;
                    for (let i = 0; i < 10; i++) {
                        particles.push({
                            x: r.x, y: r.y,
                            vx: (Math.random() - 0.5) * 8,
                            vy: (Math.random() - 0.5) * 8,
                            life: 1, type: 'smoke'
                        });
                    }
                }
            });
            if (rings.every(r => r.hit)) {
                showGameOver('ALL RINGS COLLECTED!');
            }
        }

        // Checkpoints
        if (gameMode === 'race') {
            checkpoints.forEach(cp => {
                if (!cp.hit && Math.abs(me.x - cp.x) < 50) {
                    cp.hit = true;
                    me.score += 100;
                }
            });
            if (checkpoints.every(cp => cp.hit)) {
                showGameOver('RACE COMPLETE!');
            }
        }

        // Particles
        particles = particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.2;
            p.life -= 0.02;
            if (p.type === 'debris') {
                p.a += p.spin || 5;
            }
            return p.life > 0;
        });

        // Bullets
        bullets = bullets.filter((b, i) => {
            b.x += b.vx;
            b.y += b.vy;
            if (b.x < 0 || b.x > WORLD.w || b.y < 0 || b.y > WORLD.h) return false;

            // Hit detection
            if (gameMode === 'classic') {
                if (b.owner === 'me' && opp.state === 'alive' && Math.hypot(b.x - opp.x, b.y - opp.y) < 65) {
                    opp.hp -= 10;
                    screenShake = 8;
                    for (let j = 0; j < 5; j++) {
                        particles.push({
                            x: b.x, y: b.y,
                            vx: (Math.random() - 0.5) * 6,
                            vy: (Math.random() - 0.5) * 6,
                            life: 1, type: 'fire', size: 8
                        });
                    }
                    return false;
                }
                if (b.owner === 'opp' && me.state === 'alive' && Math.hypot(b.x - me.x, b.y - me.y) < 65) {
                    // Barrel roll invincibility
                    if (!isBarrelRolling) {
                        me.hp -= 10;
                        screenShake = 8;
                    }
                    return false;
                }
            }

            // Arcade targets
            if (isArcadeMode()) {
                for (let j = arcadeTargets.length - 1; j >= 0; j--) {
                    const t = arcadeTargets[j];
                    const hitDist = gameMode === 'balloon' ? t.size : 50;
                    if (b.owner === 'me' && Math.hypot(b.x - t.x, b.y - t.y) < hitDist) {
                        arcadeTargets.splice(j, 1);
                        me.score += 10;
                        for (let k = 0; k < 10; k++) {
                            particles.push({
                                x: t.x, y: t.y,
                                vx: (Math.random() - 0.5) * 8,
                                vy: (Math.random() - 0.5) * 8,
                                life: 1, type: 'fire'
                            });
                        }
                        return false;
                    }
                }
            }

            // Enemy hits
            if ((gameMode === 'survival' || gameMode === 'escort') && b.owner === 'me') {
                for (let j = enemies.length - 1; j >= 0; j--) {
                    const e = enemies[j];
                    if (e.state === 'alive' && Math.hypot(b.x - e.x, b.y - e.y) < 65) {
                        e.hp -= 10;
                        screenShake = 6;
                        for (let k = 0; k < 5; k++) {
                            particles.push({
                                x: b.x, y: b.y,
                                vx: (Math.random() - 0.5) * 6,
                                vy: (Math.random() - 0.5) * 6,
                                life: 1, type: 'fire', size: 8
                            });
                        }
                        return false;
                    }
                }
            }
            
            // Check escort target and enemies hitting player/escort
            if (gameMode === 'escort') {
                if (b.owner === 'enemy') {
                    if (escortTarget && escortTarget.state === 'alive' && Math.hypot(b.x - escortTarget.x, b.y - escortTarget.y) < 70) {
                        escortTarget.hp -= 10;
                        return false;
                    }
                    if (me.state === 'alive' && Math.hypot(b.x - me.x, b.y - me.y) < 65) {
                        // Barrel roll invincibility
                        if (!isBarrelRolling) {
                            me.hp -= 10;
                            screenShake = 8;
                        }
                        return false;
                    }
                }
            }
            
            if (gameMode === 'survival' && b.owner === 'enemy') {
                if (me.state === 'alive' && Math.hypot(b.x - me.x, b.y - me.y) < 65) {
                    // Barrel roll invincibility
                    if (!isBarrelRolling) {
                        me.hp -= 10;
                        screenShake = 8;
                    }
                    return false;
                }
            }
            
            return true;
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        
        if (screenShake > 1) {
            ctx.translate((Math.random() - 0.5) * screenShake, (Math.random() - 0.5) * screenShake);
            screenShake *= 0.9;
        }

        // Improved camera zoom with better centering
        const baseScale = canvas.width / WORLD.w;
        const vertScale = canvas.height / WORLD.h;
        
        // Apply zoom
        ctx.scale(baseScale * cameraZoom, vertScale * cameraZoom);
        
        // Center camera on player when zoomed
        if (cameraZoom !== 1.0) {
            // Calculate offset to keep player centered
            const playerScreenX = me.x * baseScale * cameraZoom;
            const playerScreenY = me.y * vertScale * cameraZoom;
            const targetScreenX = canvas.width / 2;
            const targetScreenY = canvas.height / 2;
            
            const offsetX = (targetScreenX - playerScreenX) / (baseScale * cameraZoom);
            const offsetY = (targetScreenY - playerScreenY) / (vertScale * cameraZoom);
            
            ctx.translate(offsetX, offsetY);
        }
        
        // Draw clouds
        clouds.forEach(c => {
            ctx.globalAlpha = c.op;
            ctx.fillStyle = "white";
            ctx.beginPath();
            ctx.arc(c.x, c.y, 45 * c.s, 0, 7);
            ctx.fill();
        });
        ctx.globalAlpha = 1.0;

        // Draw particles
        particles.forEach(p => {
            if (p.type === 'debris') {
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.a * Math.PI / 180);
                ctx.fillStyle = p.color;
                ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size / 3);
                ctx.restore();
            } else {
                ctx.fillStyle = p.type === 'fire' ? `rgba(255, ${150 * p.life}, 0, ${p.life})` : `rgba(100,100,100,${p.life})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, (p.size || 10) * p.life, 0, 7);
                ctx.fill();
            }
        });

        // Draw arcade targets
        if (gameMode === 'paratrooper') {
            arcadeTargets.forEach(t => {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.beginPath();
                ctx.arc(t.x, t.y - 40, 35, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.strokeStyle = '#666';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(t.x - 30, t.y - 40);
                ctx.lineTo(t.x, t.y);
                ctx.moveTo(t.x + 30, t.y - 40);
                ctx.lineTo(t.x, t.y);
                ctx.stroke();
                
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
                
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(-25, -25, 50, 50);
                ctx.strokeStyle = '#654321';
                ctx.lineWidth = 3;
                ctx.strokeRect(-25, -25, 50, 50);
                
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
            drawPlane({ x: escortTarget.x, y: escortTarget.y, a: escortTarget.a, state: 'alive' }, escortTarget.color);
            
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
            if (p.state !== 'alive' && (!p.dt || p.dt <= 0)) return;
            ctx.save();
            ctx.translate(p.x, p.y);
            
            // Apply barrel roll rotation for player
            if (p === me && isBarrelRolling) {
                const rollAngle = (barrelRollProgress / BARREL_ROLL_DURATION) * 360;
                ctx.rotate(rollAngle * Math.PI / 180);
            }
            
            ctx.rotate(p.a * Math.PI / 180);
            
            ctx.fillStyle = "rgba(0,0,0,0.2)";
            ctx.beginPath();
            ctx.ellipse(0, 15, 50, 15, 0, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = col;
            ctx.beginPath();
            ctx.moveTo(-35, 0);
            ctx.lineTo(-55, -25);
            ctx.lineTo(-55, 25);
            ctx.fill();

            let grad = ctx.createLinearGradient(0, -15, 0, 15);
            grad.addColorStop(0, col);
            grad.addColorStop(0.5, "#fff");
            grad.addColorStop(1, col);
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.moveTo(-45, -8);
            ctx.quadraticCurveTo(0, -22, 45, -15);
            ctx.lineTo(45, 15);
            ctx.quadraticCurveTo(0, 22, -45, 8);
            ctx.fill();

            ctx.fillStyle = "#333";
            ctx.fillRect(5, -10, 15, 20);
            ctx.fillStyle = "#88e1ff";
            ctx.fillRect(7, -8, 12, 16);

            ctx.fillStyle = col;
            ctx.beginPath();
            ctx.roundRect(-8, -65, 25, 130, 8);
            ctx.fill();

            if (p.state === 'alive') {
                ctx.save();
                ctx.translate(45, 0);
                ctx.rotate(propellerRotation);
                ctx.fillStyle = "rgba(255, 255, 255, 0.2)";
                ctx.beginPath();
                ctx.arc(0, 0, 40, 0, Math.PI * 2);
                ctx.fill();
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

        document.getElementById('hp-fill').style.width = (me.hp / me.max * 100) + "%";
        document.getElementById('sc-me').innerText = me.score;
        if (!isArcadeMode()) {
            document.getElementById('sc-opp').innerText = opp.score;
        }
    }

    function showGameOver(text) {
        const overlay = document.getElementById('overlay');
        document.getElementById('overlay-text').innerText = text;
        overlay.style.display = 'flex';
        setTimeout(() => {
            overlay.style.display = 'none';
            resetGame();
        }, 3000);
    }

    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }

    // Multiplayer functions (stub)
    function initPeer() {
        // Network code placeholder
    }

    loop();
</script>
"""

components.html(game_html, height=600)