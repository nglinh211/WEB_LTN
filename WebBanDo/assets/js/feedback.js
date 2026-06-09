function allFeedback() {
  return (window.LTN_FEEDBACK || []).concat(JSON.parse(localStorage.getItem("ltnFeedback") || "[]"));
}

function ratingStars(rating) {
  var value = Math.max(0, Math.min(5, Number(rating) || 0));
  return "★★★★★".slice(0, value) + "☆☆☆☆☆".slice(0, 5 - value);
}

function feedbackRows() {
  var rows = allFeedback();
  if (!rows.length) return '<tr><td class="empty">Chưa có phản hồi.</td></tr>';
  return '<tr><th>Khách hàng</th><th>Sản phẩm</th><th>Đánh giá</th><th>Nội dung</th><th>Trạng thái</th></tr>' + rows.map(function (item) {
    return '<tr><td>' + item.customer + '</td><td>' + (item.product || "Tổng quan dịch vụ") + '</td><td><span class="rating-stars">' + ratingStars(item.rating) + '</span></td><td>' + item.message + '</td><td><span class="badge">' + item.status + '</span></td></tr>';
  }).join("");
}

function saveFeedback(form) {
  var user = getCurrentUser() || {};
  var rows = JSON.parse(localStorage.getItem("ltnFeedback") || "[]");
  rows.push({ customer: user.name || "Khách hàng", product: form.product.value, rating: Number(form.rating.value), message: form.message.value.trim(), status: "Mới" });
  localStorage.setItem("ltnFeedback", JSON.stringify(rows));
  showToast("Đã gửi phản hồi.");
  form.reset();
}
