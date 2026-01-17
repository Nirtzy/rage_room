// Admin Dashboard JavaScript

const API_BASE = window.location.origin;
let token = localStorage.getItem('access_token');

// Check authentication
if (!token) {
    window.location.href = '/static/login.html';
}

async function checkAdmin() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Authentication failed');
        }

        const user = await response.json();

        if (!user.is_admin) {
            showError('Access denied: Admin privileges required');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }

        document.getElementById('admin-email').textContent = user.email;
        loadStats();
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/static/login.html';
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load stats');

        const stats = await response.json();
        document.getElementById('total-users').textContent = stats.total_users;
        document.getElementById('total-messages').textContent = stats.total_messages;
        document.getElementById('today-messages').textContent = stats.today_messages;
        document.getElementById('current-topic').textContent = stats.current_topic || 'Not set';
    } catch (error) {
        console.error('Failed to load stats:', error);
        showError('Failed to load statistics');
    }
}

document.getElementById('topic-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const topic = document.getElementById('topic-input').value;
    const rules = document.getElementById('rules-input').value;

    try {
        const response = await fetch(`${API_BASE}/api/admin/topic`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ topic, rules })
        });

        if (!response.ok) throw new Error('Failed to update topic');

        const data = await response.json();
        showSuccess('Topic updated successfully!');
        document.getElementById('current-topic').textContent = topic;
        document.getElementById('topic-form').reset();
    } catch (error) {
        console.error('Failed to update topic:', error);
        showError('Failed to update topic');
    }
});

async function loadMessages() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/messages?limit=50`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load messages');

        const messages = await response.json();
        const messageList = document.getElementById('message-list');

        if (messages.length === 0) {
            messageList.innerHTML = '<p style="color: #00aa00;">No messages found</p>';
            return;
        }

        messageList.innerHTML = messages.map(msg => `
            <div class="message-item">
                <div class="message-content">
                    <div class="message-meta">
                        ${msg.user} • ${new Date(msg.timestamp).toLocaleString()}
                    </div>
                    <div>${msg.text}</div>
                </div>
                <button class="delete-btn" onclick="deleteMessage(${msg.id})">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load messages:', error);
        showError('Failed to load messages');
    }
}

async function deleteMessage(messageId) {
    if (!confirm('Delete this message?')) return;

    try {
        const response = await fetch(`${API_BASE}/api/admin/message/${messageId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to delete message');

        showSuccess('Message deleted');
        loadMessages();
        loadStats();
    } catch (error) {
        console.error('Failed to delete message:', error);
        showError('Failed to delete message');
    }
}

async function clearAllMessages() {
    if (!confirm('⚠️ Clear ALL messages? This cannot be undone!')) return;

    try {
        const response = await fetch(`${API_BASE}/api/admin/clear-messages`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to clear messages');

        const data = await response.json();
        showSuccess(data.message);
        loadMessages();
        loadStats();
    } catch (error) {
        console.error('Failed to clear messages:', error);
        showError('Failed to clear messages');
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 5000);
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
}

// Initialize
checkAdmin();
