const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://your-render-backend-url.onrender.com';
// Smooth cursor tracking with water-like delay
let mouseX = 50;
let mouseY = 50;
let targetX = 50;
let targetY = 50;

document.addEventListener('mousemove', (e) => {
    targetX = (e.clientX / window.innerWidth) * 100;
    targetY = (e.clientY / window.innerHeight) * 100;
});

// Smooth animation loop for water-like flow
function animateGradient() {
    mouseX += (targetX - mouseX) * 0.08; // Ease factor for smooth delay
    mouseY += (targetY - mouseY) * 0.08;
    
    document.documentElement.style.setProperty('--mouse-x', `${mouseX}%`);
    document.documentElement.style.setProperty('--mouse-y', `${mouseY}%`);
    
    requestAnimationFrame(animateGradient);
}
animateGradient();

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.querySelector('.toggle-password');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.src = 'https://img.icons8.com/?size=100&id=102646&format=png&color=000000';
    } else {
        passwordInput.type = 'password';
        toggleIcon.src = 'https://img.icons8.com/?size=100&id=0ciqibcg6iLl&format=png&color=000000';
    }
}

// Validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate password
function validatePassword(password) {
    return password.length >= 6;
}

// Show error message
function showError(inputId, errorId, message) {
    const errorElement = document.getElementById(errorId);
    const input = document.getElementById(inputId);
    
    errorElement.textContent = message;
    errorElement.classList.add('show');
    input.focus();
    
    // Remove error after 5 seconds
    setTimeout(() => {
        errorElement.classList.remove('show');
    }, 5000);
}

// Handle form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.querySelector('.btn-login');
    
    // Clear previous errors
    document.getElementById('emailError').classList.remove('show');
    document.getElementById('passwordError').classList.remove('show');
    
    let hasError = false;
    
    // Validate email
    if (!email) {
        showError('email', 'emailError', 'Email is required');
        hasError = true;
    } else if (!validateEmail(email)) {
        showError('email', 'emailError', 'Please enter a valid email');
        hasError = true;
    }
    
    // Validate password
    if (!password) {
        showError('password', 'passwordError', 'Password is required');
        hasError = true;
    } else if (!validatePassword(password)) {
        showError('password', 'passwordError', 'Password must be at least 6 characters');
        hasError = true;
    }
    
    if (hasError) return;
    
    // Show loading state
    loginBtn.classList.add('loading');
    
    try {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            }),
        });

        const result = await response.json();

        if (response.ok) {
            // Success - save user data and redirect to dashboard
            localStorage.setItem('user', JSON.stringify(result.user));
            if (result.token) {
                localStorage.setItem('token', result.token);
            }
            hToast('Login successful! Welcome back.');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            // Handle error from backend (e.g., 401 Invalid credentials)
            showError('email', 'emailError', result.detail || 'Login failed. Please try again.');
        }
        
        loginBtn.classList.remove('loading');
    } catch (error) {
        console.error('Login error:', error);
        showError('email', 'emailError', 'Connection error. Is the server running?');
        loginBtn.classList.remove('loading');
    }
});

// Add input focus animations
const inputs = document.querySelectorAll('.form-input');
inputs.forEach(input => {
    input.addEventListener('focus', () => {
        input.parentElement.style.transform = 'scale(1.02)';
    });
    
    input.addEventListener('blur', () => {
        input.parentElement.style.transform = 'scale(1)';
    });
});

// Social login handlers
document.querySelectorAll('.social-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const provider = btn.textContent.trim();
        hToast(`${provider} login coming soon!`);
    });
});

// Add ripple effect to buttons on click
function createRipple(e) {
    const button = e.currentTarget;
    const ripple = document.createElement('span');
    
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Add keyboard navigation
document.getElementById('email').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('password').focus();
    }
});

document.getElementById('password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('loginForm').dispatchEvent(new Event('submit'));
    }
});

// Prevent autofill flickering
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        if (input.value) {
            input.style.color = 'white';
        }
    });
});

// Add smooth page transitions
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
});

// Add accessibility features
document.addEventListener('keydown', (e) => {
    // ESC to blur focused element
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
    
    // TAB navigation
    if (e.key === 'Tab') {
        document.activeElement.style.outline = '2px solid rgba(255, 255, 255, 0.5)';
    }
});
