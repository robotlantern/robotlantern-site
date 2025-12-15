(() => {
  // Year
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  const intro = document.getElementById("intro");
  const video = document.getElementById("introVideo");

  // If you don't have intro assets, keep intro hidden and do nothing.
  if (!intro || !video) return;

  // Try to load; if it fails, silently fall back to still hero.
  let didStart = false;

  const bail = () => {
    intro.hidden = true;
  };

  const finish = () => {
    // Fade to black briefly, then remove intro layer
    intro.classList.add("intro--fadeout");
    window.setTimeout(() => {
      bail();
    }, 900);
  };

  video.addEventListener("error", bail);
  video.addEventListener("ended", finish);

  // Only show intro if it actually starts playing
  const start = async () => {
    try {
      // Reveal layer
      intro.hidden = false;
      await video.play();
      didStart = true;

      // Safety: in case "ended" doesn't fire reliably on some mobile browsers
      const maxMs = Math.min(Math.max((video.duration || 8) * 1000 + 500, 4500), 12000);
      window.setTimeout(() => { if (didStart) finish(); }, maxMs);
    } catch {
      bail();
    }
  };

  // Respect reduced-motion
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    bail();
    return;
  }

  start();
})();