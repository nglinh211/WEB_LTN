function logoPath(prefix) {
  return prefix + "WEBIMG/logoweb.jpg";
}

function showToast(message) {
  var toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(function () { toast.classList.remove("show"); }, 1800);
}

function pubHeader(prefix) {
  var user = getCurrentUser();
  var accountLink = prefix + "login.html";
  var accountLabel = "Đăng nhập";
  var accountAction = '<a class="btn" href="' + accountLink + '">' + accountLabel + '</a>';

  if (user) {
    if (user.role === "ADMIN") accountLink = prefix + "pages/admin/dashboard.html";
    if (user.role === "EMPLOYEE") accountLink = prefix + "pages/employee/dashboard.html";
    if (user.role === "CUSTOMER") accountLink = prefix + "pages/customer/home.html";
    accountLabel = user.role === "CUSTOMER" ? "Tài khoản" : "Bảng điều khiển";
    accountAction = '<a class="btn secondary" href="' + accountLink + '">' + accountLabel + '</a><button class="btn ghost" data-logout>Đăng xuất</button>';
  }

  return '<header class="site-header"><div class="container nav">' +
    '<a class="brand" href="' + prefix + 'index.html"><img src="' + logoPath(prefix) + '" alt="L.T.N Clothing"><span>L.T.N Clothing</span></a>' +
    '<nav class="nav-links"><a href="' + prefix + 'index.html">Trang chủ</a><a href="' + prefix + 'pages/company/about.html">Giới thiệu</a><a href="' + prefix + 'pages/customer/products.html">Sản phẩm</a><a href="' + prefix + 'index.html#news">Tin tức</a><a href="' + prefix + 'pages/company/gallery.html">Liên hệ</a>' + accountAction + '</nav>' +
    '</div></header>';
}

function links(items) {
  return items.map(function (item) { return '<a href="' + item[0] + '">' + item[1] + '</a>'; }).join("");
}

function roleLayout(role, items) {
  var user = getCurrentUser() || {};
  return '<div class="app-shell"><aside class="sidebar">' +
    '<a class="brand sidebar-brand" href="../../index.html"><img src="' + logoPath("../../") + '" alt="L.T.N Clothing"><span>L.T.N Clothing</span></a>' +
    '<nav class="side-nav">' + links(items) + '<button data-logout>Đăng xuất</button></nav></aside>' +
    '<main class="main-area"><div class="page-head"><div><p class="eyebrow">' + role + '</p><h1 data-title></h1><p data-desc></p></div><span class="badge">' + (user.name || "") + '</span></div><div data-content></div></main></div>';
}

function customerLayout() {
  var user = getCurrentUser() || {};
  return pubHeader("../../") + '<main class="container section customer-shell"><aside class="account-menu">' +
    '<strong>' + (user.name || "Khách hàng") + '</strong><a href="home.html">Tổng quan</a><a href="products.html">Sản phẩm</a><a href="cart.html">Giỏ hàng</a><a href="my-orders.html">Đơn hàng</a><a href="feedback.html">Phản hồi</a><a href="profile.html">Hồ sơ</a><button data-logout>Đăng xuất</button>' +
    '</aside><section><div class="page-head"><div><p class="eyebrow">Khách hàng</p><h1 data-title></h1><p data-desc></p></div></div><div data-content></div></section></main>';
}

function metricCards() {
  return '<div class="grid grid-4"><div class="card"><div class="metric">' + LTN_PRODUCTS.length + '</div><p>Sản phẩm</p></div><div class="card"><div class="metric">' + allOrders().length + '</div><p>Đơn hàng</p></div><div class="card"><div class="metric">' + LTN_PRODUCTS.reduce(function (s, p) { return s + p.stock; }, 0) + '</div><p>Tồn kho</p></div><div class="card"><div class="metric">' + allFeedback().length + '</div><p>Phản hồi</p></div></div>';
}

function simpleCards(items) {
  return '<div class="grid grid-3">' + items.map(function (item) {
    return '<div class="card"><h3>' + item[0] + '</h3><p>' + item[1] + '</p><button class="btn secondary" data-save-row>Lưu cập nhật</button></div>';
  }).join("") + '</div>';
}

function userTable() {
  return '<div class="table-wrap"><table><thead><tr><th>Tên</th><th>Email</th><th>Vai trò</th><th>Điện thoại</th></tr></thead><tbody>' +
    allUsers().map(function (user) {
      return '<tr><td>' + user.name + '</td><td>' + user.email + '</td><td><span class="badge">' + user.role + '</span></td><td>' + (user.phone || "") + '</td></tr>';
    }).join("") + '</tbody></table></div>';
}

function categoryOptions() {
  return LTN_CATEGORIES.map(function (category) { return '<option>' + category + '</option>'; }).join("");
}

function productOptions() {
  return LTN_PRODUCTS.map(function (product) { return '<option value="' + product.name + '">' + product.name + '</option>'; }).join("");
}

function socialIcon(type) {
  var icons = {
    fb: '<svg viewBox="0 0 24 24"><path d="M14 8h3V4h-3c-3 0-5 2-5 5v3H6v4h3v8h4v-8h3.2l.8-4h-4V9c0-.6.4-1 1-1z"/></svg>',
    ig: '<svg viewBox="0 0 24 24"><path d="M7 2h10c2.8 0 5 2.2 5 5v10c0 2.8-2.2 5-5 5H7c-2.8 0-5-2.2-5-5V7c0-2.8 2.2-5 5-5zm0 2c-1.7 0-3 1.3-3 3v10c0 1.7 1.3 3 3 3h10c1.7 0 3-1.3 3-3V7c0-1.7-1.3-3-3-3H7zm5 4a4 4 0 1 1 0 8 4 4 0 0 1 0-8zm0 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm5.2-3.2a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>',
    yt: '<svg viewBox="0 0 24 24"><path d="M22 8.2c-.2-1.6-1.3-2.8-2.9-3C16.9 5 12 5 12 5s-4.9 0-7.1.3c-1.6.2-2.7 1.4-2.9 3C1.8 9.4 1.8 12 1.8 12s0 2.6.2 3.8c.2 1.6 1.3 2.8 2.9 3C7.1 19 12 19 12 19s4.9 0 7.1-.3c1.6-.2 2.7-1.4 2.9-3 .2-1.2.2-3.8.2-3.8s0-2.6-.2-3.7zM10 15.5v-7l6 3.5-6 3.5z"/></svg>',
    mail: '<svg viewBox="0 0 24 24"><path d="M3 5h18c1.1 0 2 .9 2 2v10c0 1.1-.9 2-2 2H3c-1.1 0-2-.9-2-2V7c0-1.1.9-2 2-2zm9 8 9-6H3l9 6zm0 2.4L3 9.4V17h18V9.4l-9 6z"/></svg>',
    phone: '<svg viewBox="0 0 24 24"><path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.8-.4 1.2-.3 1.3.4 2.6.6 4 .6.7 0 1.2.5 1.2 1.2v3.5c0 .7-.5 1.2-1.2 1.2C10.8 22 2 13.2 2 2.9c0-.7.5-1.2 1.2-1.2h3.5c.7 0 1.2.5 1.2 1.2 0 1.4.2 2.7.6 4 .1.4 0 .9-.3 1.2l-1.6 2.7z"/></svg>'
  };
  return '<span class="social-icon ' + type + '" aria-hidden="true">' + icons[type] + '</span>';
}

function contactCards() {
  return '<div class="card contact-admin-card"><h3>Liên kết với chúng tôi</h3><div class="contact-list">' +
    '<a href="#">' + socialIcon("fb") + 'Facebook: L.T.N Clothing</a>' +
    '<a href="#">' + socialIcon("ig") + 'Instagram: @ltn.clothing</a>' +
    '<a href="#">' + socialIcon("yt") + 'Youtube: L.T.N Fashion</a>' +
    '<a href="mailto:support@ltn.com">' + socialIcon("mail") + 'Email: support@ltn.com</a>' +
    '<a href="tel:0901000001">' + socialIcon("phone") + 'Hotline: 0901 000 001</a>' +
    '</div></div><div class="grid grid-3">' +
    '<div class="card"><h3>Showroom</h3><p>12 Burgundy Avenue, TP.HCM</p></div>' +
    '<div class="card"><h3>Giờ mở cửa</h3><p>09:00 - 21:00 mỗi ngày</p></div>' +
    '<div class="card"><h3>Chăm sóc khách hàng</h3><p>Vận chuyển, đổi size, tư vấn phối đồ.</p></div>' +
    '</div>';
}

function companyAdminPanel() {
  return '<div class="grid grid-3">' +
    '<div class="card"><h3>Nhận diện thương hiệu</h3><p>Tên thương hiệu: L.T.N Clothing</p><p>Màu chủ đạo: burgundy, kem, blush, gold.</p><p>Khách hàng trọng tâm: nữ giới yêu phong cách thanh lịch, hiện đại.</p></div>' +
    '<div class="card"><h3>Tầm nhìn</h3><p>Trở thành thương hiệu thời trang nữ gần gũi, đáng tin cậy và có trải nghiệm mua sắm tinh tế.</p></div>' +
    '<div class="card"><h3>Sứ mệnh</h3><p>Giúp phụ nữ chọn được trang phục vừa đẹp, vừa dễ ứng dụng trong công việc và đời sống.</p></div>' +
    '<div class="card"><h3>Giá trị cốt lõi</h3><p>Nữ tính, chỉn chu, dễ mặc, dịch vụ tận tâm và hình ảnh thương hiệu nhất quán.</p></div>' +
    '<div class="card"><h3>Kênh liên hệ</h3><div class="contact-list"><a href="#">' + socialIcon("fb") + 'Facebook: L.T.N Clothing</a><a href="#">' + socialIcon("ig") + 'Instagram: @ltn.clothing</a><a href="tel:0901000001">' + socialIcon("phone") + 'Hotline: 0901 000 001</a></div></div>' +
    '<div class="card"><h3>Hình ảnh thương hiệu</h3><p>Ưu tiên ảnh sản phẩm sáng, rõ hình dáng, thể hiện sự mềm mại và cao cấp.</p><button class="btn secondary" data-save-row>Lưu nội dung</button></div>' +
    '</div>';
}

function promotionPanel() {
  return '<div class="grid grid-3 promotion-grid">' +
    '<div class="card report-block"><p>Chiến dịch đang chạy</p><div class="metric">3</div><small>Ưu đãi theo mùa và khách hàng thân thiết</small></div>' +
    '<div class="card"><h3>Ưu đãi Burgundy Muse</h3><p>Giảm 15% cho đơn từ 2 sản phẩm công sở và đi tiệc.</p><span class="badge">Đang chạy</span></div>' +
    '<div class="card"><h3>Freeship cuối tuần</h3><p>Miễn phí vận chuyển cho đơn từ 990.000 đ.</p><span class="badge">Thứ 6 - Chủ nhật</span></div>' +
    '<div class="card"><h3>Khách hàng mới</h3><p>Tặng mã LTNNEW giảm 10% cho lần mua đầu tiên.</p><span class="badge">CRM</span></div>' +
    '<form class="card form-grid management-form"><h3>Tạo chương trình</h3><input placeholder="Tên chương trình"><input placeholder="Mã giảm giá"><input type="number" placeholder="% giảm"><textarea placeholder="Điều kiện áp dụng"></textarea><button type="button" data-save-row>Lưu khuyến mãi</button></form>' +
    '<div class="card"><h3>Gợi ý CEO</h3><p>Ưu tiên khuyến mãi theo giá trị đơn hàng để không làm giảm cảm nhận cao cấp của thương hiệu.</p></div>' +
    '</div>';
}

function customerPromotions() {
  return '<div class="grid grid-3">' +
    '<article class="card"><h3>Ưu đãi Burgundy Muse</h3><p>Giảm 15% khi mua từ 2 sản phẩm công sở hoặc đi tiệc.</p><span class="badge">Mã: LTN15</span></article>' +
    '<article class="card"><h3>Freeship cuối tuần</h3><p>Miễn phí vận chuyển cho đơn hàng từ 990.000 đ.</p><span class="badge">Thứ 6 - Chủ nhật</span></article>' +
    '<article class="card"><h3>Khách hàng mới</h3><p>Giảm 10% cho đơn đầu tiên khi tạo tài khoản L.T.N.</p><span class="badge">Mã: LTNNEW</span></article>' +
    '</div>';
}

function renderCart() {
  var target = document.querySelector("[data-cart]");
  if (!target) return;
  var cart = getCart().map(function (item) {
    var product = LTN_PRODUCTS.find(function (productItem) { return productItem.id == item.id; });
    return Object.assign({}, item, {
      name: product ? product.name : item.name,
      price: product ? product.price : item.price,
      image: product ? product.image : item.image,
      category: product ? product.category : "",
      stock: product ? product.stock : ""
    });
  });
  if (!cart.length) {
    target.innerHTML = '<div class="empty">Giỏ hàng đang trống. <a class="text-link" href="products.html">Tiếp tục mua sắm</a>.</div>';
    return;
  }
  target.innerHTML = cart.map(function (item) {
    return '<div class="cart-row"><img class="cart-thumb" src="' + assetPath(item.image || "") + '" alt="' + item.name + '"><div><strong>' + item.name + '</strong><p>' + (item.category || "Sản phẩm") + (item.stock !== "" ? " | Tồn kho: " + item.stock : "") + '</p></div><span>' + money(item.price) + '</span><input type="number" min="1" value="' + item.qty + '" data-cart-qty="' + item.id + '"><button class="btn ghost" data-remove-cart="' + item.id + '">Xóa</button></div>';
  }).join("") + '<div class="cart-total"><h2>Tổng: ' + money(cartTotal(cart)) + '</h2><a class="btn" href="checkout.html">Thanh toán</a></div>';
}

function pageData(page) {
  var orders = allOrders();
  var current = getCurrentUser() || {};
  var myOrders = orders.filter(function (order) { return !current.email || order.email === current.email || order.customer === current.name; });
  var data = {
    "customer-home": ["Không gian mua sắm riêng của bạn", "Gợi ý sản phẩm mới, ưu đãi đang chạy và đơn hàng gần đây.", '<section><h2>Ưu đãi dành cho bạn</h2>' + customerPromotions() + '</section><section class="section"><h2>Gợi ý hôm nay</h2><div class="grid grid-3">' + LTN_PRODUCTS.slice(0, 3).map(productCard).join("") + '</div></section>' + orderTable(myOrders.slice(0, 3))],
    "customer-products": ["Bộ sưu tập L.T.N", "Tìm kiếm, lọc danh mục và thêm sản phẩm vào giỏ hàng.", '<div class="filters"><input data-search placeholder="Tìm sản phẩm"><select data-category><option value="">Tất cả danh mục</option>' + categoryOptions() + '</select></div><div class="grid grid-3" data-products></div>'],
    "customer-product-detail": ["Chi tiết sản phẩm", "Xem thông tin, giá và tồn kho trước khi thêm vào giỏ.", '<div data-product-detail></div>'],
    "customer-cart": ["Giỏ hàng", "Cập nhật số lượng, xóa sản phẩm và chuyển sang thanh toán.", '<div data-cart></div>'],
    "customer-checkout": ["Thanh toán", "Nhập thông tin nhận hàng để hoàn tất đơn.", '<form class="card form-grid" data-checkout><input name="name" required placeholder="Họ tên" value="' + (current.name || "") + '"><input name="phone" required placeholder="Số điện thoại" value="' + (current.phone || "") + '"><input name="address" required placeholder="Địa chỉ" value="' + (current.address || "") + '"><textarea name="note" placeholder="Ghi chú"></textarea><button>Đặt hàng</button></form>'],
    "customer-orders": ["Lịch sử đơn hàng", "Theo dõi các đơn hàng của tài khoản hiện tại.", myOrders.length ? orderTable(myOrders) : '<div class="empty">Chưa có đơn hàng nào.</div>'],
    "customer-feedback": ["Phản hồi", "Gửi đánh giá theo sản phẩm để L.T.N cải thiện chất lượng và dịch vụ.", '<form class="card form-grid" data-feedback-form><select name="product"><option value="Tổng quan dịch vụ">Tổng quan dịch vụ</option>' + productOptions() + '</select><select name="rating"><option value="5">5 sao</option><option value="4">4 sao</option><option value="3">3 sao</option></select><textarea name="message" required placeholder="Nội dung phản hồi"></textarea><button>Gửi phản hồi</button></form><section class="section"><table>' + feedbackRows() + '</table></section>'],
    "customer-profile": ["Hồ sơ tài khoản", "Thông tin đăng nhập và liên hệ của bạn.", '<form class="card form-grid"><input value="' + (current.name || "") + '"><input value="' + (current.email || "") + '"><input value="' + (current.phone || "") + '"><button data-save-row>Lưu thông tin</button></form>'],
    "employee-dashboard": ["Tổng quan vận hành", "Theo dõi sản phẩm, đơn hàng, tồn kho và phản hồi.", metricCards()],
    "employee-products": ["Sản phẩm", "Thêm, chỉnh sửa, xóa và cập nhật nhanh danh sách sản phẩm.", productManagementPanel()],
    "employee-categories": ["Danh mục", "Quản lý nhóm sản phẩm đang bán.", simpleCards(LTN_CATEGORIES.map(function (c) { return [c, "Danh mục đang hiển thị trên bộ lọc sản phẩm."]; }))],
    "employee-inventory": ["Tồn kho", "Theo dõi số lượng và trạng thái nhập hàng.", '<div class="table-wrap"><table>' + inventoryRows() + '</table></div>'],
    "employee-orders": ["Đơn hàng", "Cập nhật trạng thái xử lý đơn hàng.", orderTable(orders)],
    "employee-feedback": ["Phản hồi", "Xem đánh giá và yêu cầu từ khách hàng.", '<div class="table-wrap"><table>' + feedbackRows() + '</table></div>'],
    "employee-news": ["Tin tức", "Đăng, chỉnh sửa, xóa bài viết và quản lý nội dung từng bài.", newsManagementPanel()],
    "employee-promotions": ["Khuyến mãi", "Quản lý chương trình giảm giá, mã ưu đãi và chiến dịch bán hàng.", promotionPanel()],
    "employee-contacts": ["Liên hệ", "Thông tin showroom và các kênh chăm sóc khách hàng.", contactCards()],
    "admin-dashboard": ["Bảng điều khiển CEO", "Tổng quan điều hành dành cho chủ doanh nghiệp: doanh thu, đơn hàng, khách hàng, tồn kho và các cảnh báo cần xử lý.", ceoDashboard()],
    "admin-users": ["Tài khoản", "Quản lý tài khoản theo vai trò.", userTable()],
    "admin-roles": ["Vai trò", "Phân quyền giả lập cho ADMIN, EMPLOYEE, CUSTOMER.", simpleCards([["ADMIN", "Toàn quyền quản trị hệ thống."], ["EMPLOYEE", "Vận hành sản phẩm, kho, đơn hàng."], ["CUSTOMER", "Mua hàng và quản lý tài khoản cá nhân."]])],
    "admin-company": ["Công ty", "Quản trị nhận diện thương hiệu, thông tin doanh nghiệp, tầm nhìn, sứ mệnh và kênh liên hệ.", companyAdminPanel()],
    "admin-products": ["Sản phẩm", "Thêm, chỉnh sửa, xóa sản phẩm; quản lý giá, hình ảnh và tồn kho.", productManagementPanel()],
    "admin-categories": ["Danh mục", "Quản lý danh mục sản phẩm.", simpleCards(LTN_CATEGORIES.map(function (c) { return [c, "Nhóm sản phẩm đang kinh doanh."]; }))],
    "admin-services": ["Dịch vụ", "Quản lý dịch vụ thời trang.", simpleCards([["Tư vấn phong cách", "Gợi ý phối đồ theo sự kiện."], ["Gói quà", "Đóng gói cao cấp với điểm nhấn gold."], ["Đổi size", "Hỗ trợ đổi size linh hoạt."]])],
    "admin-inventory": ["Kho hàng", "Quản lý tồn kho toàn hệ thống.", '<div class="table-wrap"><table>' + inventoryRows() + '</table></div>'],
    "admin-orders": ["Đơn hàng", "Quản lý trạng thái đơn hàng.", orderTable(orders)],
    "admin-order-items": ["Chi tiết đơn hàng", "Chi tiết các sản phẩm trong đơn.", '<div class="table-wrap"><table><tr><th>Đơn</th><th>Sản phẩm</th><th>SL</th><th>Tổng</th></tr>' + orders.flatMap(function (order) { return (order.items || []).map(function (item) { return '<tr><td>' + order.id + '</td><td>' + item.name + '</td><td>' + item.qty + '</td><td>' + money(item.price * item.qty) + '</td></tr>'; }); }).join("") + '</table></div>'],
    "admin-news": ["Tin tức", "Đăng, chỉnh sửa, xóa bài viết và kiểm soát nội dung truyền thông.", newsManagementPanel()],
    "admin-promotions": ["Khuyến mãi", "Quản lý chương trình khuyến mãi, giảm giá và mã ưu đãi.", promotionPanel()],
    "admin-contacts": ["Liên hệ", "Quản lý thông tin liên hệ.", contactCards()],
    "admin-feedback": ["Phản hồi theo sản phẩm", "Xem đánh giá khách hàng gắn với từng sản phẩm để ưu tiên cải thiện chất lượng.", '<div class="table-wrap"><table>' + feedbackRows() + '</table></div>'],
    "admin-reports": ["Báo cáo", "Báo cáo doanh thu, kho, đơn hàng và khách hàng.", ceoDashboard() + '<div class="card"><h3>Nhận định điều hành</h3><p>Doanh thu hiện tại tập trung vào nhóm công sở và đi tiệc. CEO nên ưu tiên kiểm soát tồn kho thấp, theo dõi phản hồi mới và đẩy mạnh các sản phẩm có biên doanh thu cao.</p></div>'],
    "admin-settings": ["Cấu hình", "Cấu hình website và thông tin hiển thị.", '<form class="card form-grid"><input value="L.T.N Clothing"><input value="support@ltn.com"><select><option>Giao diện Burgundy Luxury</option></select><button data-save-row>Lưu cấu hình</button></form>']
  };
  return data[page] || ["L.T.N Clothing", "Nội dung đang cập nhật.", '<div class="card">Trang đang cập nhật nội dung.</div>'];
}

function initPage() {
  var page = document.body.dataset.page;
  var role = document.body.dataset.role;
  if (role === "ADMIN") {
    document.body.innerHTML = roleLayout("Quản trị", [["dashboard.html", "Bảng điều khiển"], ["users.html", "Tài khoản"], ["roles.html", "Vai trò"], ["company.html", "Công ty"], ["products.html", "Sản phẩm"], ["categories.html", "Danh mục"], ["promotions.html", "Khuyến mãi"], ["services.html", "Dịch vụ"], ["inventory.html", "Kho hàng"], ["orders.html", "Đơn hàng"], ["order-items.html", "Chi tiết đơn"], ["news.html", "Tin tức"], ["contacts.html", "Liên hệ"], ["feedback.html", "Phản hồi"], ["reports.html", "Báo cáo"], ["settings.html", "Cấu hình"]]);
  }
  if (role === "EMPLOYEE") {
    document.body.innerHTML = roleLayout("Nhân viên", [["dashboard.html", "Bảng điều khiển"], ["products.html", "Sản phẩm"], ["categories.html", "Danh mục"], ["promotions.html", "Khuyến mãi"], ["inventory.html", "Kho hàng"], ["orders.html", "Đơn hàng"], ["feedback.html", "Phản hồi"], ["news.html", "Tin tức"], ["contacts.html", "Liên hệ"]]);
  }
  if (role === "CUSTOMER") {
    document.body.innerHTML = customerLayout();
  }
  if (page) {
    var data = pageData(page);
    document.querySelector("[data-title]").textContent = data[0];
    document.querySelector("[data-desc]").textContent = data[1];
    document.querySelector("[data-content]").innerHTML = data[2];
  }
  renderProducts();
  renderProductDetail();
  renderCart();
  setActiveLinks();
}

document.addEventListener("DOMContentLoaded", function () {
  initPage();
  document.addEventListener("click", function (event) {
    var add = event.target.closest("[data-add-cart]");
    var remove = event.target.closest("[data-remove-cart]");
    if (add) addToCart(add.dataset.addCart);
    if (remove) removeFromCart(remove.dataset.removeCart);
    if (event.target.closest("[data-logout]")) logout();
    if (event.target.closest("[data-save-row]")) showToast("Đã lưu thay đổi giả lập.");
    if (event.target.closest("[data-delete-row]")) showToast("Đã xóa dữ liệu giả lập.");
  });
  document.addEventListener("input", function (event) {
    if (event.target.matches("[data-search],[data-category]")) renderProducts();
    if (event.target.matches("[data-cart-qty]")) updateCartQty(event.target.dataset.cartQty, event.target.value);
  });
  document.addEventListener("submit", function (event) {
    if (event.target.matches("[data-checkout]")) {
      event.preventDefault();
      createOrder(event.target);
    }
    if (event.target.matches("[data-feedback-form]")) {
      event.preventDefault();
      saveFeedback(event.target);
    }
  });
});
