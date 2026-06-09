function reportCards() {
  var orders = allOrders();
  var revenue = orders.reduce(function (sum, order) { return sum + Number(order.total || 0); }, 0);
  var customers = new Set(orders.map(function (order) { return order.email || order.customer; })).size + JSON.parse(localStorage.getItem("ltnUsers") || "[]").length;
  var stock = LTN_PRODUCTS.reduce(function (sum, product) { return sum + product.stock; }, 0);
  return '<div class="grid grid-4 report-grid"><div class="card report-block"><p>Doanh thu</p><div class="metric">' + money(revenue) + '</div></div><div class="card"><p>Đơn hàng</p><div class="metric">' + orders.length + '</div></div><div class="card"><p>Tồn kho</p><div class="metric">' + stock + '</div></div><div class="card"><p>Khách hàng</p><div class="metric">' + customers + '</div></div></div>';
}

function statusCount(orders, keyword) {
  return orders.filter(function (order) { return order.status.toLowerCase().includes(keyword.toLowerCase()); }).length;
}

function categoryRevenueRows(orders) {
  var revenueByCategory = {};
  orders.forEach(function (order) {
    (order.items || []).forEach(function (item) {
      var product = LTN_PRODUCTS.find(function (productItem) { return productItem.id == item.productId || productItem.name === item.name; });
      var category = product ? product.category : "Khác";
      revenueByCategory[category] = (revenueByCategory[category] || 0) + item.price * item.qty;
    });
  });
  return Object.keys(revenueByCategory).sort(function (a, b) { return revenueByCategory[b] - revenueByCategory[a]; }).map(function (category) {
    return '<tr><td>' + category + '</td><td>' + money(revenueByCategory[category]) + '</td></tr>';
  }).join("");
}

function lowStockRows() {
  return LTN_PRODUCTS.filter(function (product) { return product.stock <= 12; }).map(function (product) {
    return '<tr><td>' + product.name + '</td><td>' + product.category + '</td><td><span class="badge">' + product.stock + '</span></td></tr>';
  }).join("") || '<tr><td colspan="3">Không có sản phẩm tồn kho thấp.</td></tr>';
}

function ceoDashboard() {
  var orders = allOrders();
  var feedback = allFeedback();
  var revenue = orders.reduce(function (sum, order) { return sum + Number(order.total || 0); }, 0);
  var customers = new Set(orders.map(function (order) { return order.email || order.customer; })).size + JSON.parse(localStorage.getItem("ltnUsers") || "[]").length;
  var stock = LTN_PRODUCTS.reduce(function (sum, product) { return sum + product.stock; }, 0);
  var averageOrder = orders.length ? revenue / orders.length : 0;
  var pendingOrders = statusCount(orders, "chờ") + statusCount(orders, "đang");
  var newFeedback = feedback.filter(function (item) { return item.status === "Mới"; }).length;

  return '<section class="ceo-dashboard">' +
    '<div class="grid grid-4 report-grid">' +
    '<div class="card report-block"><p>Doanh thu lũy kế</p><div class="metric">' + money(revenue) + '</div><small>Tổng doanh thu từ đơn hàng hiện có</small></div>' +
    '<div class="card"><p>Giá trị đơn trung bình</p><div class="metric">' + money(averageOrder) + '</div><small>Theo dõi sức mua của khách hàng</small></div>' +
    '<div class="card"><p>Đơn cần xử lý</p><div class="metric">' + pendingOrders + '</div><small>Đơn chờ hoặc đang vận hành</small></div>' +
    '<div class="card"><p>Khách hàng</p><div class="metric">' + customers + '</div><small>Tài khoản và khách đã phát sinh đơn</small></div>' +
    '</div>' +
    '<div class="grid ceo-grid">' +
    '<div class="card"><h3>Doanh thu theo danh mục</h3><div class="table-wrap compact-table"><table><tr><th>Danh mục</th><th>Doanh thu</th></tr>' + categoryRevenueRows(orders) + '</table></div></div>' +
    '<div class="card"><h3>Cảnh báo tồn kho</h3><p>Tổng tồn kho hiện tại: <strong>' + stock + '</strong> sản phẩm.</p><div class="table-wrap compact-table"><table><tr><th>Sản phẩm</th><th>Danh mục</th><th>Tồn</th></tr>' + lowStockRows() + '</table></div></div>' +
    '<div class="card"><h3>Visual bán hàng</h3><div class="visual-bars"><span>Công sở<i style="width:86%"></i></span><span>Đi tiệc<i style="width:72%"></i></span><span>Đi chơi<i style="width:58%"></i></span><span>Phụ kiện<i style="width:42%"></i></span></div></div>' +
    '<div class="card"><h3>Ưu tiên hôm nay</h3><div class="action-list"><span>Kiểm tra ' + pendingOrders + ' đơn cần xử lý</span><span>Phản hồi ' + newFeedback + ' đánh giá mới</span><span>Theo dõi sản phẩm tồn kho thấp trước chiến dịch bán hàng</span></div></div>' +
    '<div class="card"><h3>Góc nhìn CEO</h3><p>Dashboard này tập trung vào quyết định: doanh thu, sức mua, tồn kho rủi ro, phản hồi khách hàng và trạng thái vận hành.</p></div>' +
    '</div></section>';
}
