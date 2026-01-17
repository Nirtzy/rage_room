// Login/Register Page JavaScript

const API_BASE = window.location.origin;

function switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabs = document.querySelectorAll('.tab');

    tabs.forEach(t => t.classList.remove('active'));

    if (tab === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        tabs[1].classList.add('active');
    }

    hideMessages();
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
}

function hideMessages() {
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('success-message').style.display = 'none';
}

// Login handler
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        let data;
        try {
            data = await response.json();
        } catch (e) {
            // If response is not JSON, show generic error
            showError(`Login failed: ${response.status} ${response.statusText}`);
            console.error('Failed to parse response:', e);
            return;
        }

        if (response.ok) {
            // Save token and user info
            localStorage.setItem('access_token', data.access_token);

            // Get user info
            try {
                const userResponse = await fetch(`${API_BASE}/api/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });

                if (!userResponse.ok) {
                    let errorText = '';
                    try {
                        const errorData = await userResponse.json();
                        errorText = errorData.detail || `Status: ${userResponse.status}`;
                    } catch (parseError) {
                        errorText = `Status: ${userResponse.status} ${userResponse.statusText}`;
                    }
                    console.error('Failed to get user info:', errorText, 'Response:', userResponse);
                    
                    // If it's a 401/403, token might be invalid - don't redirect
                    if (userResponse.status === 401 || userResponse.status === 403) {
                        throw new Error(`Authentication failed: ${errorText}`);
                    }
                    
                    // For other errors, try to continue anyway (user might still be able to access)
                    console.warn('User info fetch failed, but token is valid. Attempting redirect...');
                    showSuccess('Login successful! Redirecting...');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                    return;
                }

                const userData = await userResponse.json();
                localStorage.setItem('user', JSON.stringify(userData));

                showSuccess('Login successful! Redirecting...');

                // Redirect based on role
                setTimeout(() => {
                    if (userData.is_admin) {
                        window.location.href = '/static/admin.html';
                    } else {
                        window.location.href = '/';
                    }
                }, 1000);
            } catch (e) {
                console.error('Failed to get user info:', e);
                const errorMessage = e.message || 'Failed to load user info';
                showError(`Login successful but ${errorMessage}. Please check console for details.`);
            }
        } else {
            showError(data.detail || `Login failed: ${response.status}`);
        }
    } catch (error) {
        showError('Network error. Please check your connection and try again.');
        console.error('Login error:', error);
    }
});

// Register handler
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();

    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        let data;
        try {
            data = await response.json();
        } catch (e) {
            // If response is not JSON, show generic error
            showError(`Registration failed: ${response.status} ${response.statusText}`);
            console.error('Failed to parse response:', e);
            return;
        }

        if (response.ok) {
            showSuccess('Registration successful! Please login.');
            setTimeout(() => {
                switchTab('login');
                document.getElementById('login-email').value = email;
            }, 1500);
        } else {
            showError(data.detail || `Registration failed: ${response.status}`);
        }
    } catch (error) {
        showError('Network error. Please check your connection and try again.');
        console.error('Registration error:', error);
    }
});

// Check if already logged in
if (localStorage.getItem('access_token')) {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.is_admin) {
        window.location.href = '/static/admin.html';
    } else {
        window.location.href = '/';
    }
}
