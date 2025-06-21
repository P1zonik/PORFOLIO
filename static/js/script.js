
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting)
        entry.target.classList.add('visible');
    });
  });
  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
});
function toggleTheme() {
  document.body.classList.toggle('dark-mode');
}
function toggleTheme() {
  document.body.classList.toggle('dark-theme');
  localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

document.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-theme');
  }
});
