
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.product-card');
  
  // Create an intersection observer to trigger animation when cards come into view
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // Add the visible class to the container or trigger stagger on children
        triggerStaggerAnimation(cards);
        observer.disconnect(); // Only animate once
      }
    });
  }, { threshold: 0.1 });

  if (cards.length > 0) {
    observer.observe(cards[0].parentElement); // Observe the row container
  }
  
  initParticleNetwork();
  initSpotlightEffect();
  initTypewriterEffect();
});

function triggerStaggerAnimation(cards) {
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add('visible');
    }, index * 200); // 200ms delay between each card
  });
}

/**
 * 1. Neural Network Particle Background
 */
function initParticleNetwork() {
  const canvas = document.createElement('canvas');
  canvas.id = 'particle-canvas';
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.zIndex = '-1';
  canvas.style.pointerEvents = 'none';
  document.body.prepend(canvas);

  const ctx = canvas.getContext('2d');
  let particles = [];
  
  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.vx = (Math.random() - 0.5) * 0.5;
      this.vy = (Math.random() - 0.5) * 0.5;
      this.size = Math.random() * 2 + 1;
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
      if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }
    draw() {
      ctx.fillStyle = 'rgba(183, 147, 71, 0.3)'; // Gold color
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  for (let i = 0; i < 50; i++) particles.push(new Particle());

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.update();
      p.draw();
      particles.forEach(p2 => {
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 150) {
          ctx.strokeStyle = `rgba(183, 147, 71, ${0.1 - dist/1500})`;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      });
    });
    requestAnimationFrame(animate);
  }
  animate();
}

/**
 * 2. Spotlight Border Effect
 */
function initSpotlightEffect() {
  const cards = document.querySelectorAll('.product-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
}

/**
 * 3. Typewriter Text Animation
 * Delay start until i18n has resolved the final heading text.
 */
function initTypewriterEffect() {
  const heading = document.querySelector('.product-heading');
  if (!heading) return;

  // Wait for i18n to update the text content, then start typewriter
  setTimeout(() => {
    // Use textContent (not innerText) to preserve spaces between words
    const text = heading.textContent.trim();
    heading.textContent = '';
    heading.style.borderRight = '3px solid #B79347'; // cursor
    heading.style.width = 'fit-content';
    heading.style.margin = '46px auto 35px auto';
    heading.style.whiteSpace = 'nowrap';
    heading.style.overflow = 'hidden';
    heading.style.wordSpacing = 'normal';

    let i = 0;
    const type = () => {
      if (i < text.length) {
        heading.textContent += text[i]; // index notation preserves spaces
        i++;
        setTimeout(type, 50);
      } else {
        heading.style.borderRight = 'none'; // remove cursor when done
      }
    };
    type();
  }, 600); // 600ms gives i18n time to run first
}
