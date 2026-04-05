/**
 * Home page specific functionality
 * Common functionality is handled in global.js
 */

document.addEventListener('DOMContentLoaded', () => {
  animateHeroSection();
  initializeButtons();
  init3DTilt();
  initScrollReveal();
  initPreloader();
  initNavbarEffect();
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

/**
 * Preloader Logic
 */
function initPreloader() {
  const preloader = document.getElementById('preloader');
  if (preloader) {
    // Wait for window load or fallback to timeout
    const hidePreloader = () => {
      preloader.classList.add('preloader-hidden');
      setTimeout(() => {
        preloader.style.display = 'none';
      }, 500);
    };

    if (document.readyState === 'complete') {
      setTimeout(hidePreloader, 500);
    } else {
      window.addEventListener('load', () => { 
        setTimeout(hidePreloader, 500); 
      });
      // Safety fallback
      setTimeout(hidePreloader, 3000);
    }
  }
}

/**
 * Glassmorphism Navbar Effect
 */
function initNavbarEffect() {
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

/**
 * 3D Tilt Effect for Solution Cards
 */
function init3DTilt() {
  const cards = document.querySelectorAll('.solution-btn');
  
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // Calculate rotation based on cursor position
      // Center is (0.5, 0.5)
      // Range: -10deg to 10deg
      const multiplier = 20;
      const xPct = (x / rect.width) - 0.5;
      const yPct = (y / rect.height) - 0.5;
      
      const rotateY = xPct * multiplier; 
      const rotateX = yPct * -multiplier; // Invert X axis for natural tilt

      card.style.setProperty('--rotateX', `${rotateX}deg`);
      card.style.setProperty('--rotateY', `${rotateY}deg`);
      
      // Update spotlight effect position
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });

    card.addEventListener('mouseleave', () => {
      // Reset position smoothly
      card.style.setProperty('--rotateX', '0deg');
      card.style.setProperty('--rotateY', '0deg');
    });
  });
}

/**
 * Scroll Reveal Animation
 */
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('scroll-visible');
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  });

  // Target elements to animate
  const targets = document.querySelectorAll('.metrics-block, .legal-solutions h2, .solution-btn');
  targets.forEach((el, index) => {
    el.classList.add('scroll-hidden');
    // Stagger animations slightly
    el.style.transitionDelay = `${index * 0.1}s`;
    observer.observe(el);
  });
}
