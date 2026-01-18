/**
 * CloudWalk Agent Swarm - Chat Application
 * Frontend JavaScript with InfinitePay Visual Identity
 * Features: Persistence, Multi-Agent Pills, Premium UI
 */

// ===========================================
// Configuration
// ===========================================
const API_BASE_URL = 'http://localhost:8080';
const STORAGE_KEYS = {
    users: 'agentSwarmUsers',
    conversations: 'agentSwarmConversations',
    currentUser: 'agentSwarmCurrentUser_v2' // Incremented version to force clear old IDs from localStorage
};

// Test Archetypes - IDs from database
const TEST_ARCHETYPES = {
    'happy_customer': { name: 'Ana Feliz', avatar: 'A', description: '🟢 Cliente satisfeito' },
    'blocked_user': { name: 'Carlos Bloqueado', avatar: 'C', description: '🔴 Conta bloqueada' },
    'struggling_merchant': { name: 'Lojista Corre Corre', avatar: 'L', description: '🟡 Alto giro, saldo baixo' },
    'new_user_onboarding': { name: 'Marina Nova', avatar: 'M', description: '🆕 Pendente verificação' }
};

// ===========================================
// State
// ===========================================
const state = {
    users: [],
    currentUser: null,
    conversations: {},
    isLoading: false
};

// ===========================================
// DOM Elements
// ===========================================
const elements = {
    usersList: document.getElementById('usersList'),
    emptyState: document.getElementById('emptyState'),
    chatContainer: document.getElementById('chatContainer'),
    messagesContainer: document.getElementById('messagesContainer'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    currentUserName: document.getElementById('currentUserName'),
    currentUserId: document.getElementById('currentUserId'),
    currentUserAvatar: document.getElementById('currentUserAvatar'),
    agentBadge: document.getElementById('agentBadge'),
    apiStatus: document.getElementById('apiStatus'),
    addUserModal: document.getElementById('addUserModal'),
    newUserName: document.getElementById('newUserName'),
    newUserId: document.getElementById('newUserId')
};

// ===========================================
// Initialization
// ===========================================
document.addEventListener('DOMContentLoaded', () => {
    checkApiStatus();
    loadAllFromStorage();
    setupTextareaAutoResize();

    // Check API status periodically
    setInterval(checkApiStatus, 30000);
});

// ===========================================
// Storage Functions - Persistence
// ===========================================
function loadAllFromStorage() {
    // Load users
    const storedUsers = localStorage.getItem(STORAGE_KEYS.users);
    if (storedUsers) {
        state.users = JSON.parse(storedUsers);
    }

    // Load conversations
    const storedConversations = localStorage.getItem(STORAGE_KEYS.conversations);
    if (storedConversations) {
        state.conversations = JSON.parse(storedConversations);
    }

    // Add default users if empty
    if (state.users.length === 0) {
        addDefaultUsers();
    }

    renderUsersList();

    // Restore last active user
    const lastUserId = localStorage.getItem(STORAGE_KEYS.currentUser);
    if (lastUserId && state.users.find(u => u.id === lastUserId)) {
        selectUser(lastUserId);
    }
}

function saveUsersToStorage() {
    localStorage.setItem(STORAGE_KEYS.users, JSON.stringify(state.users));
}

function saveConversationsToStorage() {
    localStorage.setItem(STORAGE_KEYS.conversations, JSON.stringify(state.conversations));
}

function saveCurrentUserToStorage() {
    if (state.currentUser) {
        localStorage.setItem(STORAGE_KEYS.currentUser, state.currentUser.id);
    } else {
        localStorage.removeItem(STORAGE_KEYS.currentUser);
    }
}

// ===========================================
// API Functions
// ===========================================
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            elements.apiStatus.classList.add('online');
            elements.apiStatus.querySelector('span:last-child').textContent = 'API Online';
        }
    } catch (error) {
        elements.apiStatus.classList.remove('online');
        elements.apiStatus.querySelector('span:last-child').textContent = 'API Offline';
    }
}

async function sendMessageToAPI(message, userId) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            user_id: userId
        })
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
}

// ===========================================
// User Management
// ===========================================
function addDefaultUsers() {
    // Add all 4 test archetypes by default
    Object.entries(TEST_ARCHETYPES).forEach(([id, info]) => {
        if (!state.users.find(u => u.id === id)) {
            state.users.push({ id, name: info.name, avatar: info.avatar });
            if (!state.conversations[id]) {
                state.conversations[id] = [];
            }
        }
    });

    saveUsersToStorage();
    saveConversationsToStorage();
    renderUsersList();
}

function showAddUserModal() {
    elements.addUserModal.style.display = 'flex';
    elements.newUserId.value = '';
    elements.newUserName.value = '';
    elements.newUserId.focus();
}

function hideAddUserModal() {
    elements.addUserModal.style.display = 'none';
    elements.newUserName.value = '';
    elements.newUserId.value = '';
}

function onUserIdInput() {
    const typedId = elements.newUserId.value.trim();

    // Auto-fill name if it's a known archetype
    if (TEST_ARCHETYPES[typedId]) {
        elements.newUserName.value = TEST_ARCHETYPES[typedId].name;
    }
}

async function addUser() {
    const name = elements.newUserName.value.trim();
    const id = elements.newUserId.value.trim() || null; // Allow empty for auto-generation

    if (!name) {
        alert('Por favor, preencha pelo menos o nome do usuário.');
        return;
    }

    // Check if user already exists in local state
    if (id && state.users.find(u => u.id === id)) {
        alert('Um usuário com este ID já existe localmente.');
        return;
    }

    try {
        // Call API to create user in database
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                user_id: id // optional, backend will auto-generate if not provided
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar usuário');
        }

        const createdUser = await response.json();

        // Add to local state
        const newUser = {
            id: createdUser.user_id,
            name: createdUser.name,
            avatar: createdUser.name.charAt(0).toUpperCase()
        };

        state.users.push(newUser);
        state.conversations[newUser.id] = [];

        saveUsersToStorage();
        saveConversationsToStorage();
        renderUsersList();
        hideAddUserModal();

        // Select the new user
        selectUser(newUser.id);

    } catch (error) {
        console.error('Error creating user:', error);
        alert(`Erro ao criar usuário: ${error.message}`);
    }
}

function selectUser(userId) {
    state.currentUser = state.users.find(u => u.id === userId);

    if (!state.currentUser) return;

    // Save current user for persistence
    saveCurrentUserToStorage();

    // Update UI
    elements.emptyState.style.display = 'none';
    elements.chatContainer.style.display = 'flex';

    // Update header
    elements.currentUserName.textContent = state.currentUser.name;
    elements.currentUserId.textContent = `ID: ${state.currentUser.id}`;
    elements.currentUserAvatar.textContent = state.currentUser.avatar;

    // Update active state in sidebar
    document.querySelectorAll('.user-item').forEach(el => {
        el.classList.remove('active');
    });
    document.querySelector(`[data-user-id="${userId}"]`)?.classList.add('active');

    // Reset agent badge
    updateAgentBadge(null);

    // Render messages
    renderMessages();

    // Focus input
    elements.messageInput.focus();
}

function renderUsersList() {
    elements.usersList.innerHTML = state.users.map(user => `
        <div class="user-item ${state.currentUser?.id === user.id ? 'active' : ''}" 
             data-user-id="${user.id}"
             onclick="selectUser('${user.id}')">
            <div class="avatar">${user.avatar}</div>
            <div class="info">
                <div class="name">${user.name}</div>
                <div class="id">${user.id}</div>
            </div>
            <div class="badge"></div>
        </div>
    `).join('');
}

// ===========================================
// Message Handling
// ===========================================
async function sendMessage() {
    const message = elements.messageInput.value.trim();

    if (!message || !state.currentUser || state.isLoading) return;

    state.isLoading = true;
    elements.sendBtn.disabled = true;

    // Add user message
    const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
    };

    if (!state.conversations[state.currentUser.id]) {
        state.conversations[state.currentUser.id] = [];
    }
    state.conversations[state.currentUser.id].push(userMessage);

    // Save immediately after adding user message
    saveConversationsToStorage();

    // Clear input and render
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';
    renderMessages();

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await sendMessageToAPI(message, state.currentUser.id);

        // Remove typing indicator
        hideTypingIndicator();

        // Add assistant message - agent_used is now a list
        const assistantMessage = {
            role: 'assistant',
            content: response.response,
            agents: Array.isArray(response.agent_used) ? response.agent_used : [response.agent_used],
            sources: response.sources || [],
            debug_info: response.debug_info || null, // Capture debug info
            timestamp: new Date().toISOString()
        };

        state.conversations[state.currentUser.id].push(assistantMessage);

        // Save after receiving response
        saveConversationsToStorage();

        // Update agent badge with all agents
        updateAgentBadge(assistantMessage.agents);

        renderMessages();

    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();

        // Add error message
        const errorMessage = {
            role: 'assistant',
            content: `❌ Erro ao conectar com a API: ${error.message}`,
            agents: ['error'],
            timestamp: new Date().toISOString()
        };

        state.conversations[state.currentUser.id].push(errorMessage);
        saveConversationsToStorage();
        renderMessages();
    }

    state.isLoading = false;
    elements.sendBtn.disabled = false;
}

// ===========================================
// Agent Helpers - Premium Design
// ===========================================
function getAgentIcon(agent) {
    if (!agent) return '🤖';
    const agentLower = agent.toLowerCase();
    if (agentLower.includes('knowledge')) return '🧠';
    if (agentLower.includes('support')) return '🎧';
    if (agentLower.includes('router')) return '🔀';
    if (agentLower.includes('error')) return '❌';
    return '🤖';
}

function formatAgentName(agent) {
    if (!agent) return 'Agent';
    const agentLower = agent.toLowerCase();
    if (agentLower === 'knowledge') return 'Knowledge';
    if (agentLower === 'support') return 'Support';
    if (agentLower === 'router') return 'Router';
    return agent.charAt(0).toUpperCase() + agent.slice(1);
}

function getAgentClass(agent) {
    if (!agent) return '';
    const agentLower = agent.toLowerCase();
    if (agentLower.includes('knowledge')) return 'knowledge';
    if (agentLower.includes('support')) return 'support';
    if (agentLower.includes('router')) return 'router';
    if (agentLower.includes('error')) return 'error';
    return '';
}

function renderAgentPills(agents) {
    if (!agents || agents.length === 0) return '';

    const pills = agents.map(agent => {
        const icon = getAgentIcon(agent);
        const name = formatAgentName(agent);
        const className = getAgentClass(agent);
        return `<span class="agent-pill ${className}"><span class="agent-icon">${icon}</span> ${name}</span>`;
    }).join('');

    return `<div class="agent-pills-container">${pills}</div>`;
}

function renderSourcesTag(sources) {
    if (!sources || sources.length === 0) return '';

    return `<span class="meta-tag source-tag" onclick="showSourcesModal(${JSON.stringify(sources).replace(/"/g, '&quot;')})">
        📎 ${sources.length} fonte${sources.length > 1 ? 's' : ''}
    </span>`;
}

// ===========================================
// Sources Modal - Premium
// ===========================================
function showSourcesModal(sources) {
    const modal = document.createElement('div');
    modal.className = 'sources-modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>📎 Fontes Consultadas</h3>
                <button class="close-modal" onclick="this.closest('.sources-modal-overlay').remove()">×</button>
            </div>
            <ul class="source-list">
                ${sources.map(s => `<li><a href="${s}" target="_blank" rel="noopener noreferrer">${formatSourceUrl(s)}</a></li>`).join('')}
            </ul>
        </div>
    `;

    // Close on click outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });

    // Close on Escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);

    document.body.appendChild(modal);
}

function formatSourceUrl(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname + urlObj.pathname.slice(0, 40) + (urlObj.pathname.length > 40 ? '...' : '');
    } catch {
        return url.slice(0, 50) + (url.length > 50 ? '...' : '');
    }
}

// ===========================================
// Message Rendering
// ===========================================
function addMessage(text, type, metadata = {}) {
    const chatMessages = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    // Markdown Basic Parsing
    let htmlText = text
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Avatar
    const avatar = type === 'user'
        ? (state.currentUser?.avatar || 'U')
        : '∞';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${htmlText}</div>
    `;

    // Metadata (Agents & Sources) - Only for bot
    if (type === 'bot' && (metadata.agents || (metadata.sources && metadata.sources.length > 0))) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        // Agent Pills
        if (metadata.agents && metadata.agents.length > 0) {
            metaDiv.innerHTML += renderAgentPills(metadata.agents);
        }

        // Sources Tag
        if (metadata.sources && metadata.sources.length > 0) {
            metaDiv.innerHTML += renderSourcesTag(metadata.sources);
        }

        messageDiv.querySelector('.message-content').appendChild(metaDiv);
    }

    // DEBUG INFO BUTTON
    if (type === 'bot' && metadata.debug_info) {
        const contentDiv = messageDiv.querySelector('.message-content');

        // Ensure metaDiv exists or create a container for actions
        let metaDiv = messageDiv.querySelector('.message-meta');
        if (!metaDiv) {
            metaDiv = document.createElement('div');
            metaDiv.className = 'message-meta';
            contentDiv.appendChild(metaDiv);
        }

        // Add Debug Button
        const debugBtn = document.createElement('button');
        debugBtn.className = 'debug-btn';
        debugBtn.innerHTML = '⚙️';
        debugBtn.title = 'View Debug Info';
        debugBtn.onclick = (e) => {
            e.stopPropagation();
            showDebugModal(metadata.debug_info);
        };

        metaDiv.appendChild(debugBtn);
    }

    // DEBUG INFO (Only visible in Dev Mode via CSS)
    if (type === 'bot') {
        const debugDiv = document.createElement('div');
        debugDiv.className = 'debug-info';
        debugDiv.innerHTML = `
            <div class="debug-title">🛠️ Debug Info:</div>
            <pre>${JSON.stringify(metadata, null, 2)}</pre>
        `;
        messageDiv.querySelector('.message-content').appendChild(debugDiv);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderMessages() {
    const chatMessages = document.getElementById('messagesContainer');
    chatMessages.innerHTML = '';

    const messages = state.conversations[state.currentUser?.id] || [];

    messages.forEach(msg => {
        if (msg.role === 'user') {
            addMessage(msg.content, 'user');
        } else {
            // Support both old 'agent' and new 'agents' format
            const agents = msg.agents || (msg.agent ? [msg.agent] : []);
            addMessage(msg.content, 'bot', {
                agents: agents,
                sources: msg.sources,
                debug_info: msg.debug_info // Pass debug info to render
            });
        }
    });
}

// ===========================================
// Typing Indicator
// ===========================================
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message assistant typing';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="message-avatar">∞</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    elements.messagesContainer.appendChild(indicator);
    elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// ===========================================
// Agent Badge in Header
// ===========================================
function updateAgentBadge(agents) {
    const badge = elements.agentBadge;

    if (!agents || agents.length === 0) {
        badge.textContent = '-';
        badge.className = 'agent-badge';
        return;
    }

    // Always show the first agent (primary)
    const primaryAgent = agents[0];
    badge.textContent = formatAgent(primaryAgent);
    badge.className = 'agent-badge ' + getAgentClass(primaryAgent);
}

function formatAgent(agent) {
    if (!agent) return 'Router';

    const map = {
        'knowledge': '🧠 Knowledge',
        'support': '🎧 Support',
        'router': '🔀 Router',
        'error': '❌ Erro'
    };

    return map[agent.toLowerCase()] || agent;
}

// ===========================================
// Clear Chat
// ===========================================
function clearCurrentChat() {
    if (!state.currentUser) return;

    if (confirm(`Limpar todas as mensagens de ${state.currentUser.name}?`)) {
        state.conversations[state.currentUser.id] = [];
        saveConversationsToStorage();
        renderMessages();
        updateAgentBadge(null);
    }
}

// ===========================================
// Utilities
// ===========================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function setupTextareaAutoResize() {
    elements.messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// ===========================================
// Debug Modal Logic
// ===========================================
function showDebugModal(debugInfo) {
    const modal = document.getElementById('debugModal');
    const content = document.getElementById('debugContent');

    // Render Content
    content.innerHTML = renderDebugContent(debugInfo);

    // Show Modal
    modal.classList.add('active');
    modal.style.display = 'flex';
}

function closeDebug() {
    const modal = document.getElementById('debugModal');
    modal.classList.remove('active');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// Close on outside click
document.getElementById('debugModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'debugModal') closeDebug();
});

function renderDebugContent(info) {
    if (!info) return '<div class="debug-section">No debug info available</div>';

    return `
        <div class="debug-grid">
            <div class="debug-card">
                <span class="debug-label">ROUTING DECISION</span>
                <span class="debug-value">${info.routing || 'Unknown'}</span>
            </div>
            <div class="debug-card">
                <span class="debug-label">DETECTED LANGUAGE</span>
                <span class="debug-value">${info.language || 'Unknown'}</span>
            </div>
            <div class="debug-card">
                <span class="debug-label">A.I. GUARDRAILS</span>
                <span class="debug-value" style="color: ${info.guardrail === 'BLOCKED' ? '#ff4444' : '#00c851'}">
                    ${info.guardrail || 'Passed'}
                </span>
            </div>
            <div class="debug-card">
                <span class="debug-label">EXECUTION TIME</span>
                <span class="debug-value">${info.total_time_ms} ms</span>
            </div>
        </div>
        
        <div class="debug-section" style="margin-top: 30px;">
            <h4>🔍 Tools Execution Log</h4>
            ${renderExecutionLogs(info.logs)}
        </div>
    `;
}

function renderExecutionLogs(logs) {
    if (!logs || logs.length === 0) return '<div class="log-entry">No tools used.</div>';

    return logs.map(log => {
        if (log.type === 'tool_usage') {
            return `
                <div class="log-entry">
                    <div class="log-meta">
                        <strong>🛠️ ${log.tool}</strong>
                        <span>+${log.timestamp_ms}ms</span>
                    </div>
                    <div class="log-io">
                        <div>
                            <div class="log-label">INPUT</div>
                            <div class="log-data">${escapeHtml(log.input)}</div>
                        </div>
                        <div>
                            <div class="log-label">OUTPUT</div>
                            <div class="log-data">${escapeHtml(log.output)}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        return '';
    }).join('');
}
