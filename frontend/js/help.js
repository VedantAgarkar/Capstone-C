// Expand/collapse FAQ functionality
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.onclick = function() {
      const card = this.parentElement;
      card.classList.toggle('open');
    }
  });
});
