/**
 * CloudWalk Agent Swarm - Chat Application
 * Frontend JavaScript for interacting with the Agent Swarm API
 */

// ===========================================
// Configuration
// ===========================================
const API_BASE_URL = 'http://localhost:8000';

// ===========================================
// State
// ===========================================
const state = {
    users: [],
    currentUser: null,
    conversations: {}, // userId -> messages[]
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
    loadUsersFromStorage();
    setupTextareaAutoResize();

    // Check API status every 30 seconds
    setInterval(checkApiStatus, 30000);
});

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
function loadUsersFromStorage() {
    const stored = localStorage.getItem('agentSwarmUsers');
    if (stored) {
        state.users = JSON.parse(stored);
        renderUsersList();
    }

    // Add default users if empty
    if (state.users.length === 0) {
        addDefaultUsers();
    }
}

function saveUsersToStorage() {
    localStorage.setItem('agentSwarmUsers', JSON.stringify(state.users));
}

function addDefaultUsers() {
    const defaults = [
        { id: 'client789', name: 'João Silva', avatar: 'J' },
        { id: 'user_blocked', name: 'Conta Bloqueada', avatar: 'B' }
    ];

    defaults.forEach(user => {
        if (!state.users.find(u => u.id === user.id)) {
            state.users.push(user);
            state.conversations[user.id] = [];
        }
    });

    saveUsersToStorage();
    renderUsersList();
}

function showAddUserModal() {
    elements.addUserModal.style.display = 'flex';
    elements.newUserName.focus();
}

function hideAddUserModal() {
    elements.addUserModal.style.display = 'none';
    elements.newUserName.value = '';
    elements.newUserId.value = '';
}

function addUser() {
    const name = elements.newUserName.value.trim();
    const id = elements.newUserId.value.trim();

    if (!name || !id) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    if (state.users.find(u => u.id === id)) {
        alert('Um usuário com este ID já existe.');
        return;
    }

    const newUser = {
        id: id,
        name: name,
        avatar: name.charAt(0).toUpperCase()
    };

    state.users.push(newUser);
    state.conversations[id] = [];

    saveUsersToStorage();
    renderUsersList();
    hideAddUserModal();

    // Select the new user
    selectUser(id);
}

function selectUser(userId) {
    state.currentUser = state.users.find(u => u.id === userId);

    if (!state.currentUser) return;

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

        // Add assistant message
        const assistantMessage = {
            role: 'assistant',
            content: response.response,
            agent: response.agent_used,
            sources: response.sources || [],
            timestamp: new Date().toISOString()
        };

        state.conversations[state.currentUser.id].push(assistantMessage);

        // Update agent badge
        updateAgentBadge(response.agent_used);

        renderMessages();

    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();

        // Add error message
        const errorMessage = {
            role: 'assistant',
            content: `❌ Erro ao conectar com a API: ${error.message}`,
            agent: 'error',
            timestamp: new Date().toISOString()
        };

        state.conversations[state.currentUser.id].push(errorMessage);
        renderMessages();
    }

    state.isLoading = false;
    elements.sendBtn.disabled = false;
}

// Helper Functions
function getAgentIcon(agent) {
    if (!agent) return '🤖';
    if (agent.includes('knowledge')) return '🧠';
    if (agent.includes('support')) return '🎧';
    return '🤖';
}

function formatAgentName(agent) {
    if (!agent) return 'Agent';
    if (agent === 'knowledge') return 'Knowledge';
    if (agent === 'support') return 'Support';
    return agent;
}

function showSourcesModal(sources) {
    const modal = document.createElement('div');
    modal.className = 'sources-modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>📎 Fontes Utilizadas</h3>
                <button class="close-modal" onclick="this.closest('.sources-modal-overlay').remove()">×</button>
            </div>
            <ul class="source-list">
                ${sources.map(s => `<li><a href="${s}" target="_blank" rel="noopener noreferrer">${s}</a></li>`).join('')}
            </ul>
        </div>
    `;
    // Close on click outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    document.body.appendChild(modal);
}

function addMessage(text, type, metadata = {}) {
    const chatMessages = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    // Markdown Basic Parsing
    let htmlText = text
        .replace(/\n\n/g, '<br><br>') // Better paragraph handling
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    messageDiv.innerHTML = `<div class="message-content">${htmlText}</div>`;

    // Metadata (Sources & Agent) - Only for bot
    if (type === 'bot' && (metadata.agent_used || (metadata.sources && metadata.sources.length > 0))) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        // Agent Badge
        if (metadata.agent_used) {
            const agentSpan = document.createElement('span');
            agentSpan.className = 'meta-tag agent-tag';
            agentSpan.innerHTML = getAgentIcon(metadata.agent_used) + ' ' + formatAgentName(metadata.agent_used);
            metaDiv.appendChild(agentSpan);
        }

        // Sources
        if (metadata.sources && metadata.sources.length > 0) {
            const sourceSpan = document.createElement('span');
            sourceSpan.className = 'meta-tag source-tag';
            sourceSpan.innerHTML = `📎 ${metadata.sources.length} fonte(s)`;
            sourceSpan.title = "Clique para ver as fontes";
            sourceSpan.onclick = () => showSourcesModal(metadata.sources);
            metaDiv.appendChild(sourceSpan);
        }

        messageDiv.appendChild(metaDiv);
    }

    // DEBUG INFO (Only visible in Dev Mode via CSS)
    if (type === 'bot') {
        const debugDiv = document.createElement('div');
        debugDiv.className = 'debug-info';
        debugDiv.innerHTML = `
            <div class="debug-title">🛠️ Debug Info:</div>
            <pre>${JSON.stringify(metadata, null, 2)}</pre>
        `;
        messageDiv.appendChild(debugDiv);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderMessages() {
    // Clear current messages
    const chatMessages = document.getElementById('messagesContainer');
    chatMessages.innerHTML = '';

    const messages = state.conversations[state.currentUser?.id] || [];

    messages.forEach(msg => {
        if (msg.role === 'user') {
            addMessage(msg.content, 'user');
        } else {
            addMessage(msg.content, 'bot', {
                agent_used: msg.agent,
                sources: msg.sources,
                routing: msg.routing
            });
        }
    });
}

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

function updateAgentBadge(agent) {
    const badge = elements.agentBadge;
    badge.textContent = formatAgent(agent);
    badge.className = 'agent-badge ' + getAgentClass(agent);
}

// ===========================================
// Utilities
// ===========================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMarkdown(text) {
    // Basic markdown formatting
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

function formatAgent(agent) {
    if (!agent) return 'Router';

    const map = {
        'knowledge': '🧠 Knowledge',
        'support': '🎧 Support',
        'knowledge+support': '🔄 Ambos',
        'error': '❌ Erro',
        'router': '🔀 Router'
    };

    return map[agent.toLowerCase()] || agent;
}

function getAgentClass(agent) {
    if (!agent) return '';

    if (agent.includes('+') || agent.toLowerCase() === 'both') return 'both';
    if (agent.toLowerCase().includes('knowledge')) return 'knowledge';
    if (agent.toLowerCase().includes('support')) return 'support';

    return '';
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
