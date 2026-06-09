from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.product_list, name="category_products"),
    path("collections/", views.collection_list, name="collection_list"),
    path("collections/<slug:slug>/", views.collection_detail, name="collection_detail"),
    path("lookbook/", views.lookbook, name="lookbook"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_cart, name="remove_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/products/", views.dashboard_products, name="dashboard_products"),
    path("dashboard/categories/", views.dashboard_categories, name="dashboard_categories"),
    path("dashboard/orders/", views.dashboard_orders, name="dashboard_orders"),
    path("dashboard/customers/", views.dashboard_customers, name="dashboard_customers"),
    path("dashboard/banners/", views.dashboard_banners, name="dashboard_banners"),
    path("dashboard/blogs/", views.dashboard_blogs, name="dashboard_blogs"),
    path("dashboard/reviews/", views.dashboard_reviews, name="dashboard_reviews"),
    path("dashboard/sales/", views.dashboard_sales, name="dashboard_sales"),
    path("dashboard/sales/create/", views.dashboard_sale_create, name="dashboard_sale_create"),
    path("dashboard/sales/<int:id>/edit/", views.dashboard_sale_edit, name="dashboard_sale_edit"),
    path("dashboard/sales/<int:id>/targets/", views.dashboard_sale_targets, name="dashboard_sale_targets"),
    path("dashboard/sales/<int:id>/delete/", views.dashboard_sale_delete, name="dashboard_sale_delete"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/orders/", views.staff_orders, name="staff_orders"),
    path("staff/products/", views.staff_products, name="staff_products"),
    path("staff/inventory/", views.staff_inventory, name="staff_inventory"),
    path("staff/inventory/update/<int:product_id>/", views.staff_inventory_update, name="staff_inventory_update"),
    path("staff/inventory/report/", views.staff_inventory_report, name="staff_inventory_report"),
    path("staff/customers/", views.staff_customers, name="staff_customers"),
]
