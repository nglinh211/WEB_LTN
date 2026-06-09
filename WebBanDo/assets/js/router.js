function setActiveLinks() {
  var file = location.pathname.split("/").pop();
  document.querySelectorAll("a[href]").forEach(function (link) {
    if (link.getAttribute("href") === file) link.classList.add("active");
  });
}

function goTo(path) {
  location.href = path;
}
