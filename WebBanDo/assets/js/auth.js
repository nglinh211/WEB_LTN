function allUsers() {
  return (window.LTN_USERS || []).concat(JSON.parse(localStorage.getItem("ltnUsers") || "[]"));
}

function setAuthMessage(text) {
  var node = document.querySelector("[data-auth-message]");
  if (node) {
    node.textContent = text;
    node.hidden = !text;
  }
}

document.addEventListener("DOMContentLoaded", function () {
  var loginForm = document.querySelector("[data-login-form]");
  var registerForm = document.querySelector("[data-register-form]");

  document.querySelectorAll("[data-demo-login]").forEach(function (button) {
    button.addEventListener("click", function () {
      loginForm.email.value = button.dataset.email;
      loginForm.password.value = "123456";
    });
  });

  if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var email = loginForm.email.value.trim().toLowerCase();
      var user = allUsers().find(function (item) {
        return item.email.toLowerCase() === email && item.password === loginForm.password.value;
      });
      if (!user) {
        setAuthMessage("Email hoặc mật khẩu không đúng.");
        return;
      }
      localStorage.setItem("currentUser", JSON.stringify(user));
      setAuthMessage("Đăng nhập thành công. Đang điều hướng...");
      redirectByRole(user);
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var users = JSON.parse(localStorage.getItem("ltnUsers") || "[]");
      var email = registerForm.email.value.trim().toLowerCase();
      if (allUsers().some(function (user) { return user.email.toLowerCase() === email; })) {
        setAuthMessage("Email đã tồn tại.");
        return;
      }
      users.push({
        id: Date.now(),
        name: registerForm.name.value.trim(),
        email: email,
        password: registerForm.password.value,
        phone: registerForm.phone.value.trim(),
        address: registerForm.address ? registerForm.address.value.trim() : "",
        role: "CUSTOMER"
      });
      localStorage.setItem("ltnUsers", JSON.stringify(users));
      setAuthMessage("Đăng ký thành công. Chuyển về trang đăng nhập...");
      setTimeout(function () { location.href = "login.html"; }, 700);
    });
  }
});
