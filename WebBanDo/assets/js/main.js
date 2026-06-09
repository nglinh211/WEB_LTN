// Home scene animation: reveal sections as the visitor scrolls.
document.addEventListener("DOMContentLoaded", function () {
  var scenes = Array.prototype.slice.call(document.querySelectorAll(".reveal-section"));
  if (!scenes.length) return;

  var activateScene = function (scene) {
    if (scene.classList.contains("is-visible")) return;
    scene.classList.add("is-visible");
    scene.classList.add("is-active");
  };

  if (!("IntersectionObserver" in window)) {
    scenes.forEach(activateScene);
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) activateScene(entry.target);
    });
  }, {
    threshold: 0.28,
    rootMargin: "0px 0px -10% 0px"
  });

  scenes.forEach(function (scene, index) {
    observer.observe(scene);
    if (index === 0) {
      requestAnimationFrame(function () {
        setTimeout(function () { activateScene(scene); }, 80);
      });
    }
  });
});
