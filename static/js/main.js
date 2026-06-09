document.addEventListener("DOMContentLoaded", function () {
  var menuToggle = document.querySelector(".mobile-menu-toggle");
  var primaryNav = document.getElementById("primary-navigation");

  if (menuToggle && primaryNav && !menuToggle.dataset.bound) {
    menuToggle.dataset.bound = "true";

    menuToggle.addEventListener("click", function () {
      var isOpen = primaryNav.classList.toggle("is-open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    });

    document.addEventListener("click", function (event) {
      if (!primaryNav.classList.contains("is-open")) return;
      if (primaryNav.contains(event.target) || menuToggle.contains(event.target)) return;

      primaryNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;

      primaryNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  }

  var elements = Array.prototype.slice.call(document.querySelectorAll(".jm-section, .product-card, .jm-banner, .collection-card, .lookbook-card, .about-hero, .about-section, .about-card, .about-slogan, .about-final-cta"));
  elements = elements.filter(function (element) {
    if (element.dataset.revealBound) return false;
    element.dataset.revealBound = "true";
    return true;
  });

  if (!elements.length) return;

  elements.forEach(function (element) {
    element.classList.add("reveal-soft");
  });

  if (!("IntersectionObserver" in window)) {
    elements.forEach(function (element) {
      element.classList.add("is-visible");
    });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: "0px 0px -8% 0px"
  });

  elements.forEach(function (element) {
    observer.observe(element);
  });
});
