function allOrders() {
  return (window.LTN_ORDERS || []).concat(JSON.parse(localStorage.getItem("ltnOrders") || "[]"));
}

function createOrder(form) {
  var cart = getCart();
  if (!cart.length) {
    showToast("Giỏ hàng đang trống.");
    return;
  }
  var current = getCurrentUser() || {};
  var orders = JSON.parse(localStorage.getItem("ltnOrders") || "[]");
  orders.push({
    id: "LTN" + Date.now().toString().slice(-6),
    customer: form.name.value.trim(),
    email: current.email || "",
    phone: form.phone.value.trim(),
    address: form.address.value.trim(),
    note: form.note.value.trim(),
    total: cartTotal(cart),
    status: "Chờ xác nhận",
    date: new Date().toISOString().slice(0, 10),
    items: cart
  });
  localStorage.setItem("ltnOrders", JSON.stringify(orders));
  saveCart([]);
  showToast("Đặt hàng thành công.");
  setTimeout(function () { location.href = "my-orders.html"; }, 500);
}

function orderTable(orders) {
  return '<div class="table-wrap"><table><thead><tr><th>Mã</th><th>Khách hàng</th><th>Ngày</th><th>Tổng</th><th>Trạng thái</th></tr></thead><tbody>' +
    orders.map(function (order) {
      return '<tr><td>' + order.id + '</td><td>' + order.customer + '</td><td>' + order.date + '</td><td>' + money(order.total) + '</td><td><span class="badge status-' + order.status.toLowerCase().replaceAll(" ", "-") + '">' + order.status + '</span></td></tr>';
    }).join("") + '</tbody></table></div>';
}
