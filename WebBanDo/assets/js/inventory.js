function inventoryRows() {
  return '<tr><th>Sản phẩm</th><th>Danh mục</th><th>Tồn kho</th><th>Trạng thái</th></tr>' + LTN_PRODUCTS.map(function (product) {
    var status = product.stock < 10 ? "Sắp hết" : "Ổn định";
    return '<tr><td>' + product.name + '</td><td>' + product.category + '</td><td><input class="small-input" type="number" value="' + product.stock + '"></td><td><span class="badge">' + status + '</span></td></tr>';
  }).join("");
}
