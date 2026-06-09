function money(value) {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(value);
}

function assetPath(path) {
  return getBasePath() + path;
}

function productImage(product) {
  if (!product.image) return "";
  return '<img src="' + assetPath(product.image) + '" alt="' + product.name + '" loading="lazy">';
}

function productCard(product) {
  return '<article class="card product-card">' +
    '<a class="product-art" href="product-detail.html?id=' + product.id + '">' + productImage(product) + '<span class="badge">' + product.category + '</span></a>' +
    '<div class="content"><h3>' + product.name + '</h3><p>' + product.desc + '</p>' +
    '<p class="price">' + money(product.price) + '</p><p>Tồn kho: ' + product.stock + ' | Size: ' + product.size + '</p><p><span class="rating-stars">★★★★★</span> <small>Đánh giá tốt</small></p>' +
    '<div class="hero-actions"><a class="btn secondary" href="product-detail.html?id=' + product.id + '">Chi tiết</a><button data-add-cart="' + product.id + '">Thêm vào giỏ</button></div></div></article>';
}

function productTable() {
  return '<div class="table-wrap"><table><thead><tr><th>Sản phẩm</th><th>Danh mục</th><th>Giá</th><th>Tồn</th><th>Thao tác</th></tr></thead><tbody>' +
    LTN_PRODUCTS.map(function (product) {
      return '<tr><td><strong>' + product.name + '</strong><br><small>' + product.desc + '</small></td><td>' + product.category + '</td><td>' + money(product.price) + '</td><td><input class="small-input" type="number" value="' + product.stock + '" data-stock-input="' + product.id + '"></td><td><div class="row-actions"><button class="btn secondary" data-save-row>Sửa</button><button class="btn secondary" data-save-row>Lưu</button><button class="btn ghost" data-delete-row>Xóa</button></div></td></tr>';
    }).join("") + '</tbody></table></div>';
}

function productManagementPanel() {
  return '<form class="card form-grid management-form"><h3>Thêm sản phẩm</h3><div class="form-grid cols-4"><input placeholder="Tên sản phẩm"><select>' + categoryOptions() + '</select><input type="number" placeholder="Giá"><input type="number" placeholder="Tồn kho"></div><textarea placeholder="Mô tả sản phẩm"></textarea><button type="button" data-save-row>Thêm sản phẩm</button></form>' + productTable();
}

function productReviewBlock(product) {
  var rows = allFeedback().filter(function (item) { return item.product === product.name; });
  if (!rows.length) {
    rows = [{ customer: "Khách hàng L.T.N", rating: 5, message: "Sản phẩm đẹp, hình ảnh rõ và chất liệu dễ mặc.", product: product.name }];
  }
  return '<section class="section product-reviews"><h2>Đánh giá sản phẩm</h2><div class="grid grid-3">' + rows.map(function (item) {
    return '<article class="card review-card"><img src="' + assetPath(product.image) + '" alt="' + product.name + '"><div><strong>' + item.customer + '</strong><p><span class="rating-stars">' + ratingStars(item.rating) + '</span></p><p>' + item.message + '</p></div></article>';
  }).join("") + '</div></section>';
}

function renderProducts() {
  var target = document.querySelector("[data-products]");
  if (!target) return;
  var categorySelect = document.querySelector("[data-category]");
  if (categorySelect && !categorySelect.dataset.ready) {
    var selectedCategory = new URLSearchParams(location.search).get("category");
    if (selectedCategory) categorySelect.value = selectedCategory;
    categorySelect.dataset.ready = "true";
  }
  var query = (document.querySelector("[data-search]")?.value || "").toLowerCase();
  var category = categorySelect?.value || "";
  var products = LTN_PRODUCTS.filter(function (product) {
    return product.name.toLowerCase().includes(query) && (!category || product.category === category);
  });
  target.innerHTML = products.map(productCard).join("") || '<div class="empty">Không tìm thấy sản phẩm phù hợp.</div>';
}

function renderProductDetail() {
  var target = document.querySelector("[data-product-detail]");
  if (!target) return;
  var product = LTN_PRODUCTS.find(function (item) { return item.id == new URLSearchParams(location.search).get("id"); }) || LTN_PRODUCTS[0];
  target.innerHTML = '<div class="detail-grid"><div class="product-art detail-art">' + productImage(product) + '</div>' +
    '<div class="card detail-copy"><p class="eyebrow">' + product.category + '</p><h1>' + product.name + '</h1><p>' + product.desc + '</p>' +
    '<p class="price">' + money(product.price) + '</p><p>Tồn kho: ' + product.stock + '</p><p>Size: ' + product.size + '</p>' +
    '<button data-add-cart="' + product.id + '">Thêm vào giỏ hàng</button><a class="btn secondary" href="products.html">Quay lại sản phẩm</a></div></div>' + productReviewBlock(product);
}
