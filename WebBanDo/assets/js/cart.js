function getCart() {
  return JSON.parse(localStorage.getItem("ltn_cart") || "[]");
}

function saveCart(cart) {
  localStorage.setItem("ltn_cart", JSON.stringify(cart));
}

function cartTotal(cart) {
  return cart.reduce(function (sum, item) { return sum + item.price * item.qty; }, 0);
}

function addToCart(id) {
  var product = LTN_PRODUCTS.find(function (item) { return item.id == id; });
  if (!product) return;
  var cart = getCart();
  var line = cart.find(function (item) { return item.id == id; });
  if (line) {
    line.qty += 1;
    line.name = product.name;
    line.price = product.price;
    line.image = product.image;
  } else {
    cart.push({ id: product.id, name: product.name, price: product.price, image: product.image, qty: 1 });
  }
  saveCart(cart);
  showToast("Đã thêm vào giỏ hàng.");
}

function updateCartQty(id, qty) {
  var cart = getCart();
  cart.forEach(function (item) {
    if (item.id == id) item.qty = Math.max(1, Number(qty) || 1);
  });
  saveCart(cart);
  renderCart();
}

function removeFromCart(id) {
  saveCart(getCart().filter(function (item) { return item.id != id; }));
  renderCart();
}
