/**
 * Global JavaScript utilities for HealthPredict
 * Handles common UI interactions and shared functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize navigation active link highlighting
  initializeNavigation();
  
  // Add smooth scrolling for anchor links
  initializeSmoothScroll();

  // Initialize Language
  initializeLanguage();

  // Check authentication state
  checkAuthState();
});

function checkAuthState() {
    const userJson = localStorage.getItem('user');
    const loginBtn = document.querySelector('.login-btn');
    
    if (userJson && loginBtn) {
        const user = JSON.parse(userJson);
        // Replace "Login" button with User Name and Logout option
        loginBtn.innerHTML = `👤 ${user.fullname}`;
        loginBtn.href = '#';
        loginBtn.classList.add('user-profile-btn');
        
        // Inject Dashboard link if admin
        if (user.is_admin) {
            const navMenu = document.querySelector('.nav-menu');
            if (navMenu && !document.querySelector('.dashboard-nav-link')) {
                const dashboardLi = document.createElement('li');
                dashboardLi.innerHTML = '<a href="dashboard.html" class="nav-link dashboard-nav-link">Dashboard</a>';
                navMenu.appendChild(dashboardLi);
            }
        }
        
        // Add logout on click with confirmation
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            hConfirm('Logout', 'Are you sure you want to log out of your account?', () => {
                localStorage.removeItem('user');
                localStorage.removeItem('token');
                hToast('Logged out successfully');
                setTimeout(() => window.location.reload(), 1200);
            });
        });
    }
}

function initializeLanguage() {
    const langSelect = document.getElementById('lang-select');
    if (!langSelect) return;

    // Check URL param first, then localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');
    const savedLang = localStorage.getItem('healthpredict_lang') || 'en';
    const currentLang = urlLang || savedLang;

    // Set select value
    langSelect.value = currentLang;
    
    // Update local storage if current language is different
    if (currentLang !== savedLang) {
        localStorage.setItem('healthpredict_lang', currentLang);
    }

    // Apply translations
    updateLanguage(currentLang);

    // Handle change with reload
    langSelect.addEventListener('change', (e) => {
        const newLang = e.target.value;
        localStorage.setItem('healthpredict_lang', newLang);
        
        // Force reload with new lang param
        const url = new URL(window.location);
        url.searchParams.set('lang', newLang);
        window.location.href = url.toString();
    });
}

function updateLanguage(lang) {
    if (!window.translations || !window.translations[lang]) return;

    const t = window.translations[lang];

    // 1. Update text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const text = getNestedProperty(t, key);
        if (text) {
            el.textContent = text;
        }
    });

    // 1b. Update placeholders
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        const text = getNestedProperty(t, key);
        if (text) {
            el.placeholder = text;
        }
    });

    // 2. Streamlit link propagation removed for Node.js backend
}

function getNestedProperty(obj, path) {
    return path.split('.').reduce((prev, curr) => {
        return prev ? prev[curr] : null;
    }, obj);
}

/**
 * Highlight the active navigation link based on current page
 */
function initializeNavigation() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

/**
 * Enable smooth scrolling for all anchor links
 */
function initializeSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}


/**
 * CUSTOM NOTIFICATION SYSTEM
 * Replaces browser's default alert(), confirm(), and notifications
 */

/**
 * Shows a custom modal alert
 * @param {string} title 
 * @param {string} message 
 * @param {function} callback 
 */
window.hAlert = function(title, message, callback = null) {
  // Clear any existing modals
  const existing = document.querySelector('.h-modal-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.className = 'h-modal-overlay';
  overlay.innerHTML = `
    <div class="h-modal">
      <div class="h-modal-title">${title}</div>
      <div class="h-modal-text">${message}</div>
      <div class="h-modal-footer">
        <button class="h-modal-btn h-modal-btn-primary">OK</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(overlay);
  
  // Trigger animation
  setTimeout(() => overlay.classList.add('active'), 10);
  
  const btn = overlay.querySelector('.h-modal-btn-primary');
  btn.onclick = () => {
    overlay.classList.remove('active');
    setTimeout(() => {
      overlay.remove();
      if (callback) callback();
    }, 300);
  };
};

/**
 * Shows a custom confirmation modal
 * @param {string} title 
 * @param {string} message 
 * @param {function} onConfirm 
 * @param {function} onCancel 
 */
window.hConfirm = function(title, message, onConfirm, onCancel = null) {
  const existing = document.querySelector('.h-modal-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.className = 'h-modal-overlay';
  overlay.innerHTML = `
    <div class="h-modal">
      <div class="h-modal-title">${title}</div>
      <div class="h-modal-text">${message}</div>
      <div class="h-modal-footer">
        <button class="h-modal-btn h-modal-btn-secondary btn-cancel">Cancel</button>
        <button class="h-modal-btn h-modal-btn-primary btn-confirm">Confirm</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(overlay);
  setTimeout(() => overlay.classList.add('active'), 10);
  
  const confirmBtn = overlay.querySelector('.btn-confirm');
  const cancelBtn = overlay.querySelector('.btn-cancel');
  
  confirmBtn.onclick = () => {
    overlay.classList.remove('active');
    setTimeout(() => {
      overlay.remove();
      if (onConfirm) onConfirm();
    }, 300);
  };
  
  cancelBtn.onclick = () => {
    overlay.classList.remove('active');
    setTimeout(() => {
      overlay.remove();
      if (onCancel) onCancel();
    }, 300);
  };
};

/**
 * Shows a quick toast notification
 * @param {string} message 
 * @param {number} duration 
 */
window.hToast = function(message, duration = 3000) {
  const existing = document.querySelector('.h-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'h-toast';
  toast.innerHTML = `
    <i class="h-toast-icon">✨</i>
    <span class="h-toast-text">${message}</span>
  `;
  
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('active'), 10);
  
    setTimeout(() => {
    toast.classList.remove('active');
    setTimeout(() => toast.remove(), 400);
  }, duration);
};

// Override standard browser methods to ensure consistency
// This catches any missed alert() or confirm() calls
window.alert = function(message) {
  window.hAlert('HealthPredict', message);
};

window.confirm = function(message) {
  // Note: Modern browsers no longer block on custom modals, 
  // so this override might require callback-based logic in the calling code.
  // But for simple "OK/Cancel" style UI consistency, we show the modal.
  console.warn("Standard confirm() called. Use hConfirm() for proper callback handling.");
  window.hAlert('Confirmation Required', message + "\n\n(Please use the application buttons instead of system dialogs)");
  return true; // Simple bypass
};


