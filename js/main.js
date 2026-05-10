(function () {
  'use strict';

  document.querySelectorAll('.site-nav a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      var targetId = link.getAttribute('href').slice(1);
      var target = document.getElementById(targetId);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  });

  var header = document.querySelector('.site-header');
  if (header) {
    var lastY = 0;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      header.style.boxShadow = y > 4
        ? '0 4px 12px rgba(45, 30, 15, 0.15)'
        : '0 2px 6px rgba(45, 30, 15, 0.08)';
      lastY = y;
    }, { passive: true });
  }
})();
