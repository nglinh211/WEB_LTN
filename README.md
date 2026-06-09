# L.T.N Clothing Django Backend

## Cấu trúc

```text
ltn_clothing/
  manage.py
  requirements.txt
  config/
  shop/
  accounts/
  templates/
  static/
  media/
```

## Chạy local

```powershell
cd C:\Coder\ltn_clothing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

Mở trang chủ tại `http://127.0.0.1:8000/`.

## Route chính

- `/`
- `/products/`
- `/products/<slug:slug>/`
- `/category/<slug:slug>/`
- `/cart/`
- `/cart/add/<int:product_id>/`
- `/cart/update/<int:item_id>/`
- `/cart/remove/<int:item_id>/`
- `/checkout/`
- `/order-success/<int:order_id>/`
- `/login/`
- `/register/`
- `/logout/`
- `/profile/`
- `/orders/`
- `/blog/`
- `/blog/<slug:slug>/`
- `/collections/`
- `/collections/<slug:slug>/`
- `/lookbook/`
- `/wishlist/`
- `/dashboard/`
- `/dashboard/products/`
- `/dashboard/categories/`
- `/dashboard/orders/`
- `/dashboard/customers/`
- `/dashboard/banners/`
- `/dashboard/blogs/`

## Tài khoản demo

Seed data tạo lại đúng tài khoản demo từ source HTML/JS cũ:

- `admin` hoặc `admin@ltn.com` / `123456` / `ADMIN`
- `employee` hoặc `employee@ltn.com` / `123456` / `STAFF`
- `customer` hoặc `customer@ltn.com` / `123456` / `CUSTOMER`

## HTML đã chuyển sang template

- `index.html` -> `templates/shop/home.html`
- `login.html` -> `templates/accounts/login.html`
- `register.html` -> `templates/accounts/register.html`
- Trang sản phẩm/giỏ hàng/checkout/blog/profile/order được dựng mới bằng Django template.

Static đang đọc lại từ frontend cũ qua `STATICFILES_DIRS`:

- `WebBanDo/assets`
- `WebBanDo/WEBIMG`

Ảnh upload từ admin dùng `media/`.
