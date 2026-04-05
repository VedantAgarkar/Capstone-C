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

// Toggle confirm password visibility
function toggleConfirmPassword() {
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const toggleIcon = document.querySelector('.toggle-confirm-password');
    
    if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        toggleIcon.src = 'https://img.icons8.com/?size=100&id=102646&format=png&color=000000';
    } else {
        confirmPasswordInput.type = 'password';
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
    return password.length >= 8;
}

// Validate full name
function validateFullName(fullname) {
    return fullname.trim().length >= 2;
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
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fullname = document.getElementById('fullname').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const termsCheckbox = document.getElementById('termsCheckbox');
    const signupBtn = document.querySelector('.btn-login');
    
    // Clear previous errors
    document.getElementById('fullnameError').classList.remove('show');
    document.getElementById('emailError').classList.remove('show');
    document.getElementById('passwordError').classList.remove('show');
    document.getElementById('confirmPasswordError').classList.remove('show');
    document.getElementById('termsError').classList.remove('show');
    
    let hasError = false;
    
    // Validate full name
    if (!fullname) {
        showError('fullname', 'fullnameError', 'Full name is required');
        hasError = true;
    } else if (!validateFullName(fullname)) {
        showError('fullname', 'fullnameError', 'Full name must be at least 2 characters');
        hasError = true;
    }
    
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
        showError('password', 'passwordError', 'Password must be at least 8 characters');
        hasError = true;
    }
    
    // Validate confirm password
    if (!confirmPassword) {
        showError('confirmPassword', 'confirmPasswordError', 'Please confirm your password');
        hasError = true;
    } else if (password !== confirmPassword) {
        showError('confirmPassword', 'confirmPasswordError', 'Passwords do not match');
        hasError = true;
    }
    
    // Validate terms
    if (!termsCheckbox.checked) {
        const termsError = document.getElementById('termsError');
        termsError.textContent = 'You must agree to the Terms & Conditions';
        termsError.classList.add('show');
        hasError = true;
        
        setTimeout(() => {
            termsError.classList.remove('show');
        }, 5000);
    }
    
    if (hasError) return;
    
    // Show loading state
    signupBtn.classList.add('loading');
    
    try {
        // Simulate API call (replace with actual backend call)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Success - redirect to login page
        alert('Account created successfully! Please sign in.');
        window.location.href = 'login.html';
        
        signupBtn.classList.remove('loading');
    } catch (error) {
        console.error('Signup error:', error);
        showError('email', 'emailError', 'Signup failed. Please try again.');
        signupBtn.classList.remove('loading');
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

// Social signup handlers
document.querySelectorAll('.social-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const provider = btn.textContent.trim();
        alert(`${provider} signup coming soon!`);
    });
});

// Add keyboard navigation
document.getElementById('fullname').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('email').focus();
    }
});

document.getElementById('email').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('password').focus();
    }
});

document.getElementById('password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('confirmPassword').focus();
    }
});

document.getElementById('confirmPassword').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('signupForm').dispatchEvent(new Event('submit'));
    }
});

// Real-time password match validation
document.getElementById('confirmPassword').addEventListener('input', function() {
    const password = document.getElementById('password').value;
    const confirmPassword = this.value;
    const confirmPasswordError = document.getElementById('confirmPasswordError');
    
    if (confirmPassword && password !== confirmPassword) {
        confirmPasswordError.textContent = 'Passwords do not match';
        confirmPasswordError.classList.add('show');
    } else {
        confirmPasswordError.classList.remove('show');
    }
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
