// Main game entry point

// Screen management
let currentMode = null; // 'prewritten' or 'dynamic'
let generatedWorld = null;

function selectMode(mode) {
    currentMode = mode;

    if (mode === 'prewritten') {
        showScreen('prewritten-intro');
    } else if (mode === 'dynamic') {
        showScreen('dynamic-builder');
    }
}

function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(s => {
        s.classList.remove('active');
    });

    // Show selected screen
    document.getElementById(screenId).classList.add('active');
}

function backToModeSelect() {
    showScreen('mode-select');
    currentMode = null;
}

// Pre-written game
function startPrewrittenGame() {
    // Load game with pre-written prompt
    initGame('prewritten');
    showScreen('game-main');

    // Show intro message
    addMessage('system', `
You stand on the deck of Horizon's Edge as the sun sets over the endless ocean. 
The engine hums beneath your feet. Marcus is in the engine room. Elena studies 
charts on the bridge. The Cook prepares dinner in silence.

What do you do?
  `.trim());
}

// Dynamic world generation
async function generateWorld(event) {
    event.preventDefault();

    const worldSetting = document.getElementById('world-setting').value;
    const charName = document.getElementById('char-name').value;
    const charDesc = document.getElementById('char-desc').value;
    const scenario = document.getElementById('scenario').value;

    // Show loader
    document.getElementById('world-form').style.display = 'none';
    document.getElementById('generating-loader').style.display = 'block';

    // TODO: Call Gemini API to generate world
    // For now, simulate
    await simulateWorldGeneration(worldSetting, charName, charDesc, scenario);

    // Show preview
    showScreen('world-preview');
}

async function simulateWorldGeneration(setting, name, desc, scenario) {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock generated world
    generatedWorld = {
        setting: setting,
        character: { name, description: desc },
        scenario: scenario || 'You begin your journey...',
        npcs: [
            { name: 'Generated NPC 1', role: 'Companion', personality: 'Friendly' },
            { name: 'Generated NPC 2', role: 'Rival', personality: 'Cunning' }
        ],
        summary: `World created based on: ${setting}`
    };

    // Display preview
    document.getElementById('world-summary').textContent = generatedWorld.summary;
    document.getElementById('scenario-preview').textContent = generatedWorld.scenario;

    const npcList = document.getElementById('npc-list');
    npcList.innerHTML = generatedWorld.npcs.map(npc => `
    <div style="margin-bottom: 1rem; padding: 0.5rem; background: var(--bg-dark); border-radius: 5px;">
      <strong>${npc.name}</strong> - ${npc.role}<br>
      <small style="color: var(--text-dim);">${npc.personality}</small>
    </div>
  `).join('');
}

function regenerateWorld() {
    // Go back to form
    showScreen('dynamic-builder');
    document.getElementById('world-form').style.display = 'block';
    document.getElementById('generating-loader').style.display = 'none';
}

function startDynamicGame() {
    // Load game with dynamic world
    initGame('dynamic');
    showScreen('game-main');

    // Show custom intro
    addMessage('system', generatedWorld.scenario);
}

// Game initialization
function initGame(mode) {
    // Initialize game state
    gameState = {
        mode: mode,
        food: 100,
        fuel: 100,
        morale: 50,
        day: 1,
        location: mode === 'prewritten' ? 'Open Sea' : 'Starting Location'
    };

    // Clear chat
    document.getElementById('chat-history').innerHTML = '';

    // Update stats
    updateStats();

    // Reset budget
    budgetRemaining = 200;
    updateBudget();
}

// Game state
let gameState = null;
let budgetRemaining = 200;

function updateStats() {
    if (!gameState) return;

    // Update values
    document.getElementById('food-value').textContent = Math.floor(gameState.food);
    document.getElementById('fuel-value').textContent = Math.floor(gameState.fuel);
    document.getElementById('morale-value').textContent = Math.floor(gameState.morale);
    document.getElementById('day-count').textContent = gameState.day;
    document.getElementById('location').textContent = gameState.location;

    // Update bars
    document.getElementById('food-bar').style.width = `${gameState.food}%`;
    document.getElementById('fuel-bar').style.width = `${gameState.fuel}%`;
    document.getElementById('morale-bar').style.width = `${gameState.morale}%`;
}

function updateBudget() {
    document.getElementById('budget-remaining').textContent = budgetRemaining;

    if (budgetRemaining <= 0) {
        document.getElementById('send-btn').disabled = true;
        addMessage('system', '⚠️ Budget exceeded. Refresh page to continue.');
    }
}

// Chat functions
function addMessage(type, text) {
    const chatHistory = document.getElementById('chat-history');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.textContent = type === 'player' ? 'You:' : 'Game Master:';

    const content = document.createElement('div');
    content.textContent = text;

    messageDiv.appendChild(meta);
    messageDiv.appendChild(content);
    chatHistory.appendChild(messageDiv);

    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendAction() {
    const input = document.getElementById('player-input');
    const action = input.value.trim();

    if (!action) return;

    // Check budget
    if (budgetRemaining <= 0) {
        alert('Budget exceeded!');
        return;
    }

    // Add player message
    addMessage('player', action);

    // Clear input
    input.value = '';

    // Disable input temporarily
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';

    try {
        // TODO: Call AI here
        // For now, echo back
        await new Promise(resolve => setTimeout(resolve, 1000));

        const response = `[AI response to: "${action}"]
    
This is a placeholder. Implement Gemini API integration here.

Testing state changes:
[FOOD: -5]
[MORALE: +2]`;

        addMessage('gm', response);

        // Parse and apply state changes
        applyStateChanges(response);

        // Decrement budget
        budgetRemaining--;
        updateBudget();

    } catch (error) {
        addMessage('system', `Error: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

function applyStateChanges(response) {
    // Parse [STAT: value] tags
    const regex = /\[([A-Z]+):\s*([+-]?\d+)\]/g;
    let match;

    while ((match = regex.exec(response)) !== null) {
        const stat = match[1].toLowerCase();
        const value = parseInt(match[2]);

        if (gameState.hasOwnProperty(stat)) {
            gameState[stat] = Math.max(0, Math.min(100, gameState[stat] + value));
        }
    }

    updateStats();
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌊 The Last Voyage - Initialized');
    console.log('Mode selection ready');
});
