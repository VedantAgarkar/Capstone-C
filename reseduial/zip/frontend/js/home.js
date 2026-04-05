/**
 * Home page specific functionality
 * Common functionality is handled in global.js
 */

document.addEventListener('DOMContentLoaded', () => {
  animateHeroSection();
  initializeButtons();
});

function animateHeroSection() {
  const heroSection = document.querySelector('.hero');
  if (heroSection) {
    heroSection.style.opacity = '0';
    heroSection.style.transform = 'translateY(20px)';
    setTimeout(() => {
      heroSection.style.transition = 'all 0.6s ease-in-out';
      heroSection.style.opacity = '1';
      heroSection.style.transform = 'translateY(0)';
    }, 100);
  }
}

function initializeButtons() {
  const ctaButtons = document.querySelectorAll('.cta-btn, .btn');
  ctaButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      this.style.transform = 'scale(0.98)';
      setTimeout(() => {
        this.style.transform = 'scale(1)';
      }, 150);
    });
  });
}
