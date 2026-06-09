function getBasePath() {
  return location.pathname.includes("/pages/") ? "../../" : "";
}

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("currentUser")) || JSON.parse(localStorage.getItem("ltn_current_user"));
  } catch (error) {
    return null;
  }
}

function requireRole(role) {
  var user = getCurrentUser();
  if (!user || user.role !== role) {
    location.href = getBasePath() + "login.html";
  }
}

function requireAnyRole(roles) {
  var user = getCurrentUser();
  if (!user || !roles.includes(user.role)) {
    location.href = getBasePath() + "login.html";
  }
}

function redirectByRole(user) {
  var base = getBasePath();
  if (!user) {
    location.href = base + "login.html";
    return;
  }
  var targets = {
    ADMIN: "pages/admin/dashboard.html",
    EMPLOYEE: "pages/employee/dashboard.html",
    CUSTOMER: "pages/customer/home.html"
  };
  location.href = base + (targets[user.role] || "login.html");
}

function logout() {
  localStorage.removeItem("currentUser");
  localStorage.removeItem("ltn_current_user");
  location.href = getBasePath() + "login.html";
}
