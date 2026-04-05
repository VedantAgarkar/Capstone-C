/**
 * Global JavaScript utilities for HealthPredict
 * Handles common UI interactions and shared functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize navigation active link highlighting
  initializeNavigation();
  
  // Add smooth scrolling for anchor links
  initializeSmoothScroll();
});

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
 * Utility function for toggling element visibility
 */
function toggleElement(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.style.display = element.style.display === 'none' ? 'block' : 'none';
  }
}

/**
 * Utility function for adding CSS classes
 */
function addClass(elementId, className) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.add(className);
  }
}

/**
 * Utility function for removing CSS classes
 */
function removeClass(elementId, className) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.remove(className);
  }
}
