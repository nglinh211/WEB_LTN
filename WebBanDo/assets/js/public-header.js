function initPublicHeader(prefix) {
  var user = getCurrentUser();
  var loginLink = document.querySelector('.nav-links a[href$="login.html"]');
  if (!user || !loginLink) return;

  var accountHref = prefix + "login.html";
  var accountLabel = "Tài khoản";
  if (user.role === "ADMIN") {
    accountHref = prefix + "pages/admin/dashboard.html";
    accountLabel = "Bảng điều khiển";
  }
  if (user.role === "EMPLOYEE") {
    accountHref = prefix + "pages/employee/dashboard.html";
    accountLabel = "Bảng điều khiển";
  }
  if (user.role === "CUSTOMER") {
    accountHref = prefix + "pages/customer/home.html";
  }

  loginLink.outerHTML = '<a class="btn secondary" href="' + accountHref + '">' + accountLabel + '</a><button class="btn ghost" data-logout>Đăng xuất</button>';
  document.addEventListener("click", function (event) {
    if (event.target.closest("[data-logout]")) logout();
  });
}
