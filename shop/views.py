from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CartItemUpdateForm, CheckoutForm, InventoryUpdateForm, ProductFilterForm, ProductReviewForm, SaleCampaignForm
from .models import Banner, BlogPost, Cart, CartItem, Category, Collection, InventoryLog, Order, OrderItem, Product, ProductReview, SaleCampaign, SaleTarget, Wishlist


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def home(request):
    categories = Category.objects.filter(is_active=True)[:10]
    hero_banner = Banner.objects.filter(is_active=True, position=Banner.POSITION_HERO).first()
    grid_banners = Banner.objects.filter(is_active=True, position=Banner.POSITION_GRID)[:6]
    collections = Collection.objects.filter(is_active=True)[:6]
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:8]
    latest_products = Product.objects.filter(is_active=True, is_new=True).select_related("category")[:8]
    sale_products = [product for product in Product.objects.filter(is_active=True).select_related("category") if product.has_sale][:8]
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    return render(request, "shop/home.html", {
        "categories": categories,
        "hero_banner": hero_banner,
        "grid_banners": grid_banners,
        "collections": collections,
        "featured_products": featured_products,
        "latest_products": latest_products,
        "sale_products": sale_products,
        "latest_posts": latest_posts,
    })


def about(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:8]
    gallery_images = list(Banner.objects.filter(is_active=True).exclude(image="")[:6])
    return render(request, "shop/about.html", {
        "featured_products": featured_products,
        "gallery_images": gallery_images,
    })


def product_list(request, slug=None):
    category = None
    products = Product.objects.filter(is_active=True).select_related("category")
    if slug:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products = products.filter(category=category)

    form = ProductFilterForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get("q")
        sort = form.cleaned_data.get("sort")
        if query:
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if sort == "price_asc":
            products = products.order_by("sale_price", "price")
        elif sort == "price_desc":
            products = products.order_by("-sale_price", "-price")
        else:
            products = products.order_by("-created_at")

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "shop/product_list.html", {
        "category": category,
        "categories": Category.objects.filter(is_active=True),
        "form": form,
        "page_obj": page_obj,
    })


def collection_list(request):
    collections = Collection.objects.filter(is_active=True)
    return render(request, "shop/collection_list.html", {"collections": collections})


def collection_detail(request, slug):
    collection = get_object_or_404(Collection, slug=slug, is_active=True)
    products = Product.objects.filter(is_active=True).select_related("category")[:12]
    return render(request, "shop/collection_detail.html", {"collection": collection, "products": products})


def lookbook(request):
    banners = Banner.objects.filter(is_active=True)
    collections = Collection.objects.filter(is_active=True)
    return render(request, "shop/lookbook.html", {"banners": banners, "collections": collections})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category").prefetch_related("images"), slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:3]
    reviews = product.reviews.filter(is_approved=True).select_related("user", "user__profile")
    user_review = None
    if request.user.is_authenticated:
        user_review = ProductReview.objects.filter(product=product, user=request.user).first()
    review_form = ProductReviewForm()
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        if user_review:
            messages.warning(request, "Bạn đã đánh giá sản phẩm này rồi.")
            return redirect(product.get_absolute_url())
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Cảm ơn bạn đã gửi đánh giá.")
            return redirect(product.get_absolute_url())
    return render(request, "shop/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "review_form": review_form,
        "user_review": user_review,
    })


@login_required
def cart_detail(request):
    cart = get_cart(request.user)
    return render(request, "shop/cart.html", {"cart": cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if not product.is_in_stock:
        messages.error(request, "Sản phẩm hiện đã hết hàng.")
        return redirect(product.get_absolute_url())
    cart = get_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": 1})
    if not created:
        if item.quantity >= product.stock:
            messages.warning(request, "Số lượng trong giỏ đã bằng tồn kho hiện có.")
        else:
            item.quantity += 1
            item.save()
            messages.success(request, "Đã cập nhật giỏ hàng.")
    else:
        messages.success(request, "Đã thêm sản phẩm vào giỏ hàng.")
    return redirect("shop:cart")


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, "Đã thêm vào yêu thích.")
    else:
        item.delete()
        messages.success(request, "Đã xóa khỏi yêu thích.")
    return redirect(request.META.get("HTTP_REFERER") or product.get_absolute_url())


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related("product", "product__category")
    return render(request, "shop/wishlist.html", {"items": items})


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    form = CartItemUpdateForm(request.POST, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật số lượng.")
    else:
        messages.error(request, form.errors.get("quantity", ["Không thể cập nhật số lượng."])[0])
    return redirect("shop:cart")


@login_required
def remove_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("shop:cart")


@login_required
def checkout(request):
    cart = get_cart(request.user)
    items = list(cart.items.select_related("product"))
    if not items:
        messages.error(request, "Giỏ hàng đang trống.")
        return redirect("shop:cart")

    profile = getattr(request.user, "profile", None)
    initial = {}
    if profile:
        initial = {"full_name": profile.full_name, "phone": profile.phone, "address": profile.address}

    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked_items = list(CartItem.objects.select_related("product").select_for_update().filter(cart=cart))
            if not locked_items:
                messages.error(request, "Giỏ hàng đang trống.")
                return redirect("shop:cart")
            for item in locked_items:
                if item.quantity > item.product.stock:
                    messages.error(request, f"{item.product.name} không đủ tồn kho.")
                    return redirect("shop:cart")
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = sum(item.subtotal() for item in locked_items)
            order.save()
            for item in locked_items:
                product = item.product
                subtotal = item.subtotal()
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.final_price,
                    quantity=item.quantity,
                    subtotal=subtotal,
                )
                product.stock -= item.quantity
                product.save(update_fields=["stock", "updated_at"])
            cart.items.all().delete()
        return redirect("shop:order_success", order_id=order.id)
    return render(request, "shop/checkout.html", {"cart": cart, "form": form})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, "shop/blog_list.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "shop/blog_detail.html", {"post": post})


def dashboard_allowed(user, staff_ok=True):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(getattr(user, "profile", None), "role", "")
    return role == "ADMIN" or (staff_ok and role == "STAFF")


def dashboard_denied(request):
    role = getattr(getattr(request.user, "profile", None), "role", "")
    if role == "STAFF":
        return redirect("shop:staff_dashboard")
    if role == "CUSTOMER":
        return redirect("accounts:profile")
    return HttpResponseForbidden("Bạn không có quyền truy cập tổng quan quản trị.")


def is_admin_user(user):
    return user.is_superuser or getattr(getattr(user, "profile", None), "role", "") == "ADMIN"


def is_staff_user(user):
    role = getattr(getattr(user, "profile", None), "role", "")
    return role == "STAFF"


def staff_allowed(user):
    return user.is_authenticated and (is_staff_user(user) or is_admin_user(user))


def staff_denied(request):
    role = getattr(getattr(request.user, "profile", None), "role", "")
    if role == "CUSTOMER":
        return redirect("accounts:profile")
    return HttpResponseForbidden("Bạn không có quyền truy cập khu vực nhân viên.")


def money_value(value):
    return int(value or 0)


def format_vnd(value):
    return f"{money_value(value):,}".replace(",", ".") + " đ"


@login_required
def dashboard(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)

    today = timezone.localdate()
    start_month = today.replace(day=1)
    start_7_days = today - timedelta(days=6)
    completed_orders = Order.objects.filter(status=Order.STATUS_COMPLETED)
    total_orders = Order.objects.count()
    completed_count = completed_orders.count()
    completion_rate = round((completed_count / total_orders) * 100, 1) if total_orders else 0

    status_rows = Order.objects.values("status").annotate(total=Count("id")).order_by("status")
    status_labels = [dict(Order.STATUS_CHOICES).get(row["status"], row["status"]) for row in status_rows]
    status_values = [row["total"] for row in status_rows]

    revenue_rows = completed_orders.filter(created_at__date__gte=start_7_days).annotate(day=TruncDate("created_at")).values("day").annotate(total=Sum("total_amount")).order_by("day")
    revenue_map = {row["day"]: money_value(row["total"]) for row in revenue_rows}
    revenue_labels = [(start_7_days + timedelta(days=i)).strftime("%d/%m") for i in range(7)]
    revenue_values = [revenue_map.get(start_7_days + timedelta(days=i), 0) for i in range(7)]

    category_rows = Category.objects.annotate(total=Count("products")).order_by("-total")[:5]
    top_product_rows = OrderItem.objects.values("product_name").annotate(total=Sum("quantity")).order_by("-total")[:5]

    stats = {
        "total_revenue": completed_orders.aggregate(total=Sum("total_amount"))["total"] or 0,
        "monthly_revenue": completed_orders.filter(created_at__date__gte=start_month).aggregate(total=Sum("total_amount"))["total"] or 0,
        "total_orders": total_orders,
        "pending_orders": Order.objects.filter(status=Order.STATUS_PENDING).count(),
        "completed_orders": completed_count,
        "completion_rate": completion_rate,
        "total_products": Product.objects.filter(is_active=True).count(),
        "low_stock_products": Product.objects.filter(stock__lte=10, is_active=True).count(),
        "total_customers": User.objects.filter(profile__role="CUSTOMER").count(),
    }
    stats_display = {
        "total_revenue": format_vnd(stats["total_revenue"]),
        "monthly_revenue": format_vnd(stats["monthly_revenue"]),
    }
    recent_orders = list(Order.objects.select_related("user").order_by("-created_at")[:8])
    for order in recent_orders:
        order.total_amount_display = format_vnd(order.total_amount)
    return render(request, "dashboard/index.html", {
        "page_title": "Tổng quan vận hành",
        "stats": stats,
        "stats_display": stats_display,
        "recent_orders": recent_orders,
        "low_stock_list": Product.objects.select_related("category").filter(stock__lte=10, is_active=True).order_by("stock")[:8],
        "new_customers": User.objects.select_related("profile").order_by("-date_joined")[:8],
        "revenue_chart": {"labels": revenue_labels, "values": revenue_values},
        "order_status_chart": {"labels": status_labels, "values": status_values},
        "category_chart": {"labels": [row.name for row in category_rows], "values": [row.total for row in category_rows]},
        "top_product_chart": {"labels": [row["product_name"] for row in top_product_rows], "values": [row["total"] or 0 for row in top_product_rows]},
    })


@login_required
def dashboard_products(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    products = Product.objects.select_related("category").order_by("-created_at")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    flag = request.GET.get("flag", "")
    status = request.GET.get("status", "")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category:
        products = products.filter(category_id=category)
    if flag == "new":
        products = products.filter(is_new=True)
    if status == "inactive":
        products = products.filter(is_active=False)
    else:
        products = products.filter(is_active=True)
    products = list(products)
    if flag == "sale":
        products = [product for product in products if product.has_sale]
    for product in products:
        product.price_display = format_vnd(product.price)
        product.sale_price_display = format_vnd(product.final_price) if product.has_sale else "-"
    return render(request, "dashboard/products.html", {
        "page_title": "Quản lý sản phẩm",
        "products": products,
        "categories": Category.objects.filter(is_active=True),
        "can_delete": is_admin_user(request.user),
    })


@login_required
def dashboard_categories(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    categories = Category.objects.annotate(product_count=Count("products")).order_by("sort_order", "name")
    return render(request, "dashboard/categories.html", {
        "page_title": "Quản lý danh mục",
        "categories": categories,
        "can_delete": is_admin_user(request.user),
    })


@login_required
def dashboard_orders(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    if request.method == "POST":
        order = get_object_or_404(Order, pk=request.POST.get("order_id"))
        status = request.POST.get("status")
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save(update_fields=["status", "updated_at"])
            messages.success(request, "Đã cập nhật trạng thái đơn hàng.")
        return redirect("shop:dashboard_orders")
    status_counts = {key: Order.objects.filter(status=key).count() for key, _ in Order.STATUS_CHOICES}
    status_cards = [{"key": key, "label": label, "count": status_counts.get(key, 0)} for key, label in Order.STATUS_CHOICES]
    orders = list(Order.objects.select_related("user").order_by("-created_at"))
    for order in orders:
        order.total_amount_display = format_vnd(order.total_amount)
    return render(request, "dashboard/orders.html", {
        "page_title": "Quản lý đơn hàng",
        "orders": orders,
        "status_cards": status_cards,
        "status_choices": Order.STATUS_CHOICES,
    })


@login_required
def dashboard_customers(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    today = timezone.localdate()
    start_month = today.replace(day=1)
    query = request.GET.get("q", "").strip()
    segment = request.GET.get("segment", "").strip()
    customers = User.objects.select_related("profile").annotate(
        order_count=Count("orders"),
        total_spent=Sum("orders__total_amount", filter=Q(orders__status=Order.STATUS_COMPLETED)),
    ).order_by("-date_joined")
    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__full_name__icontains=query) |
            Q(profile__phone__icontains=query)
        )
    if segment == "new":
        customers = customers.filter(date_joined__date__gte=start_month)
    elif segment == "vip":
        customers = customers.filter(total_spent__gte=5000000)
    elif segment == "frequent":
        customers = customers.filter(order_count__gte=3)
    elif segment == "no_order":
        customers = customers.filter(order_count=0)
    total_customers = customers.count()
    new_this_month = customers.filter(date_joined__date__gte=start_month).count()
    buyers = customers.filter(order_count__gt=0).count()
    customers = list(customers)
    for customer in customers:
        customer.total_spent_display = format_vnd(customer.total_spent)
        customer.customer_status = "Khách VIP" if money_value(customer.total_spent) >= 5000000 else ("Đã mua hàng" if customer.order_count else "Chưa mua")
    return render(request, "dashboard/customers.html", {
        "page_title": "Quản lý khách hàng",
        "customers": customers,
        "total_customers": total_customers,
        "new_this_month": new_this_month,
        "buyers": buyers,
        "segment": segment,
        "query": query,
    })


@login_required
def dashboard_banners(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    return render(request, "dashboard/banners.html", {
        "page_title": "Quản lý banner",
        "banners": Banner.objects.order_by("sort_order", "id"),
    })


@login_required
def dashboard_blogs(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    return render(request, "dashboard/blogs.html", {
        "page_title": "Quản lý bài viết",
        "posts": BlogPost.objects.order_by("-created_at"),
    })


@login_required
def dashboard_sales(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    now = timezone.now()
    sales = SaleCampaign.objects.prefetch_related("targets").order_by("-start_date")
    status = request.GET.get("status", "")
    if status == "running":
        sales = sales.filter(is_active=True, start_date__lte=now, end_date__gte=now)
    elif status == "upcoming":
        sales = sales.filter(is_active=True, start_date__gt=now)
    elif status == "ended":
        sales = sales.filter(end_date__lt=now)
    elif status == "disabled":
        sales = sales.filter(is_active=False)
    stats = {
        "total": SaleCampaign.objects.count(),
        "running": SaleCampaign.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now).count(),
        "upcoming": SaleCampaign.objects.filter(is_active=True, start_date__gt=now).count(),
        "ended": SaleCampaign.objects.filter(end_date__lt=now).count(),
    }
    return render(request, "dashboard/sales.html", {
        "page_title": "Quản lý khuyến mãi",
        "sales": sales,
        "stats": stats,
        "current_status": status,
    })


@login_required
def dashboard_sale_create(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    form = SaleCampaignForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        sale = form.save()
        messages.success(request, "Đã tạo chương trình sale.")
        return redirect("shop:dashboard_sale_targets", id=sale.id)
    return render(request, "dashboard/sale_form.html", {
        "page_title": "Tạo khuyến mãi",
        "form": form,
        "sale": None,
    })


@login_required
def dashboard_sale_edit(request, id):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    sale = get_object_or_404(SaleCampaign, pk=id)
    form = SaleCampaignForm(request.POST or None, request.FILES or None, instance=sale)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật chương trình sale.")
        return redirect("shop:dashboard_sales")
    return render(request, "dashboard/sale_form.html", {
        "page_title": "Sửa khuyến mãi",
        "form": form,
        "sale": sale,
    })


@login_required
def dashboard_sale_targets(request, id):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    sale = get_object_or_404(SaleCampaign.objects.prefetch_related("targets"), pk=id)
    query = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True).select_related("category").order_by("name")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_target":
            target = get_object_or_404(SaleTarget, pk=request.POST.get("target_id"), campaign=sale)
            target.delete()
            messages.success(request, "Đã xóa mục áp dụng.")
            return redirect("shop:dashboard_sale_targets", id=sale.id)

        added = 0
        product_ids = request.POST.getlist("products")
        for product_id in product_ids:
            product = get_object_or_404(Product, pk=product_id)
            _, created = SaleTarget.objects.get_or_create(campaign=sale, product=product)
            added += int(created)

        category_id = request.POST.get("category")
        if category_id:
            category = get_object_or_404(Category, pk=category_id)
            _, created = SaleTarget.objects.get_or_create(campaign=sale, category=category)
            added += int(created)

        collection_id = request.POST.get("collection")
        if collection_id:
            collection = get_object_or_404(Collection, pk=collection_id)
            _, created = SaleTarget.objects.get_or_create(campaign=sale, collection=collection)
            added += int(created)

        if added:
            messages.success(request, f"Đã gán {added} mục áp dụng cho chương trình sale.")
        else:
            messages.info(request, "Không có mục áp dụng mới hoặc mục này đã tồn tại.")
        return redirect("shop:dashboard_sale_targets", id=sale.id)

    return render(request, "dashboard/sale_targets.html", {
        "page_title": "Gán sản phẩm sale",
        "sale": sale,
        "products": products[:80],
        "categories": Category.objects.filter(is_active=True),
        "collections": Collection.objects.filter(is_active=True),
        "targets": SaleTarget.objects.select_related("product", "category", "collection").filter(campaign=sale),
        "query": query,
    })


@login_required
def dashboard_sale_delete(request, id):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    sale = get_object_or_404(SaleCampaign, pk=id)
    if request.method == "POST":
        sale.delete()
        messages.success(request, "Đã xóa chương trình sale.")
        return redirect("shop:dashboard_sales")
    return render(request, "dashboard/sale_confirm_delete.html", {
        "page_title": "Xóa khuyến mãi",
        "sale": sale,
    })


@login_required
def dashboard_reviews(request):
    if not dashboard_allowed(request.user, staff_ok=False):
        return dashboard_denied(request)
    if request.method == "POST":
        review = get_object_or_404(ProductReview, pk=request.POST.get("review_id"))
        action = request.POST.get("action")
        if action == "approve":
            review.is_approved = True
            review.save(update_fields=["is_approved", "updated_at"])
            messages.success(request, "Đã duyệt đánh giá.")
        elif action == "hide":
            review.is_approved = False
            review.save(update_fields=["is_approved", "updated_at"])
            messages.success(request, "Đã ẩn đánh giá.")
        elif action == "delete":
            review.delete()
            messages.success(request, "Đã xóa đánh giá.")
        return redirect("shop:dashboard_reviews")
    reviews = ProductReview.objects.select_related("product", "user").order_by("-created_at")
    return render(request, "dashboard/reviews.html", {
        "page_title": "Quản lý đánh giá",
        "reviews": reviews,
        "total_reviews": reviews.count(),
        "approved_reviews": reviews.filter(is_approved=True).count(),
        "hidden_reviews": reviews.filter(is_approved=False).count(),
    })


def staff_orders_queryset():
    return Order.objects.select_related("user").filter(
        status__in=[Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_SHIPPING]
    ).order_by("-created_at")


def decorate_orders(orders):
    orders = list(orders)
    for order in orders:
        order.total_amount_display = format_vnd(order.total_amount)
    return orders


@login_required
def staff_dashboard(request):
    if not staff_allowed(request.user):
        return staff_denied(request)

    today = timezone.localdate()
    start_7_days = today - timedelta(days=6)
    today_orders = Order.objects.filter(created_at__date=today)
    pending_today = Order.objects.filter(status=Order.STATUS_PENDING, created_at__date=today).count()
    shipping_orders = Order.objects.filter(status=Order.STATUS_SHIPPING).count()
    low_stock_products = Product.objects.select_related("category").filter(is_active=True, stock__lte=10).order_by("stock")
    new_customers_qs = User.objects.select_related("profile").filter(profile__role="CUSTOMER").order_by("-date_joined")
    new_customers = new_customers_qs[:6]
    attention_orders = decorate_orders(staff_orders_queryset()[:8])
    care_customers = User.objects.filter(profile__role="CUSTOMER", date_joined__date__gte=today - timedelta(days=7)).count()
    today_revenue = today_orders.exclude(status=Order.STATUS_CANCELLED).aggregate(total=Sum("total_amount"))["total"] or 0
    new_orders_today = today_orders.count()
    top_staff_products = []
    top_product_rows = OrderItem.objects.exclude(order__status=Order.STATUS_CANCELLED).values("product_name").annotate(
        sold_quantity=Sum("quantity"),
        revenue=Sum("subtotal"),
    ).order_by("-sold_quantity")[:5]
    for rank, row in enumerate(top_product_rows, 1):
        top_staff_products.append({
            "rank": rank,
            "name": row["product_name"],
            "sold_quantity": row["sold_quantity"] or 0,
            "revenue_display": format_vnd(row["revenue"] or 0),
        })

    order_rows = Order.objects.filter(created_at__date__gte=start_7_days).annotate(day=TruncDate("created_at")).values("day").annotate(total=Count("id")).order_by("day")
    revenue_rows = Order.objects.filter(created_at__date__gte=start_7_days).exclude(status=Order.STATUS_CANCELLED).annotate(day=TruncDate("created_at")).values("day").annotate(total=Sum("total_amount")).order_by("day")
    customer_rows = User.objects.filter(profile__role="CUSTOMER", date_joined__date__gte=start_7_days).annotate(day=TruncDate("date_joined")).values("day").annotate(total=Count("id")).order_by("day")
    order_map = {row["day"]: row["total"] for row in order_rows}
    revenue_map = {row["day"]: money_value(row["total"]) for row in revenue_rows}
    customer_map = {row["day"]: row["total"] for row in customer_rows}
    chart_labels = [(start_7_days + timedelta(days=i)).strftime("%d/%m") for i in range(7)]
    chart_days = [start_7_days + timedelta(days=i) for i in range(7)]

    progress_checks = [
        pending_today == 0,
        shipping_orders == 0,
        low_stock_products.count() == 0,
        care_customers == 0,
    ]
    progress_percent = round((sum(1 for item in progress_checks if item) / len(progress_checks)) * 100)

    todos = [
        {"label": "Xác nhận đơn mới", "count": Order.objects.filter(status=Order.STATUS_PENDING).count()},
        {"label": "Cập nhật đơn đang giao", "count": shipping_orders},
        {"label": "Kiểm tra sản phẩm sắp hết", "count": low_stock_products.count()},
        {"label": "Chăm sóc khách hàng mới", "count": care_customers},
    ]

    order_values = [order_map.get(day, 0) for day in chart_days]
    revenue_values = [revenue_map.get(day, 0) for day in chart_days]
    customer_values = [customer_map.get(day, 0) for day in chart_days]
    max_order_value = max(order_values) if order_values else 0
    max_revenue_value = max(revenue_values) if revenue_values else 0
    max_customer_value = max(customer_values) if customer_values else 0
    staff_order_points = [
        {"label": label, "value": value, "percent": round((value / max_order_value) * 100) if max_order_value else 0}
        for label, value in zip(chart_labels, order_values)
    ]
    staff_revenue_points = [
        {"label": label, "value": format_vnd(value), "raw": value, "percent": round((value / max_revenue_value) * 100) if max_revenue_value else 0}
        for label, value in zip(chart_labels, revenue_values)
    ]
    staff_customer_points = [
        {"label": label, "value": value, "percent": round((value / max_customer_value) * 100) if max_customer_value else 0}
        for label, value in zip(chart_labels, customer_values)
    ]

    return render(request, "staff/index.html", {
        "page_title": "Tổng quan nhân viên",
        "pending_today": pending_today,
        "shipping_orders": shipping_orders,
        "low_stock_count": low_stock_products.count(),
        "new_customer_count": new_customers_qs.count(),
        "today_revenue_display": format_vnd(today_revenue),
        "new_orders_today": new_orders_today,
        "care_customers": care_customers,
        "progress_percent": progress_percent,
        "todos": todos,
        "attention_orders": attention_orders,
        "attention_products": low_stock_products[:8],
        "new_customers": new_customers,
        "top_staff_products": top_staff_products,
        "staff_order_chart": {"labels": chart_labels, "values": order_values},
        "staff_revenue_chart": {"labels": chart_labels, "values": revenue_values},
        "staff_customer_chart": {"labels": chart_labels, "values": customer_values},
        "staff_order_points": staff_order_points,
        "staff_revenue_points": staff_revenue_points,
        "staff_customer_points": staff_customer_points,
        "staff_order_total": sum(order_values),
        "staff_revenue_total": format_vnd(sum(revenue_values)),
        "staff_customer_total": sum(customer_values),
    })


@login_required
def staff_orders(request):
    if not staff_allowed(request.user):
        return staff_denied(request)
    if request.method == "POST":
        order = get_object_or_404(Order, pk=request.POST.get("order_id"))
        status = request.POST.get("status")
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save(update_fields=["status", "updated_at"])
            messages.success(request, "Đã cập nhật trạng thái đơn hàng.")
        return redirect("shop:staff_orders")
    return render(request, "staff/orders.html", {
        "page_title": "Đơn hàng cần xử lý",
        "orders": decorate_orders(staff_orders_queryset()),
        "status_choices": Order.STATUS_CHOICES,
    })


@login_required
def staff_products(request):
    if not staff_allowed(request.user):
        return staff_denied(request)
    products = Product.objects.select_related("category").filter(is_active=True).order_by("stock", "name")
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    products = list(products)
    for product in products:
        product.price_display = format_vnd(product.price)
    return render(request, "staff/products.html", {
        "page_title": "Sản phẩm và tồn kho",
        "products": products,
        "inventory_only": False,
    })


@login_required
def staff_inventory(request):
    if not staff_allowed(request.user):
        return staff_denied(request)
    products_qs = Product.objects.select_related("category").filter(is_active=True)
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    stock_status = request.GET.get("stock_status", "")
    sort = request.GET.get("sort", "stock_asc")
    if query:
        products_qs = products_qs.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category_id:
        products_qs = products_qs.filter(category_id=category_id)
    if stock_status == "in_stock":
        products_qs = products_qs.filter(stock__gt=10)
    elif stock_status == "low_stock":
        products_qs = products_qs.filter(stock__gt=0, stock__lte=10)
    elif stock_status == "out_stock":
        products_qs = products_qs.filter(stock=0)
    products_qs = products_qs.order_by("-stock" if sort == "stock_desc" else "stock", "name")
    all_products = Product.objects.filter(is_active=True)
    stats = {
        "total": all_products.count(),
        "in_stock": all_products.filter(stock__gt=10).count(),
        "low_stock": all_products.filter(stock__gt=0, stock__lte=10).count(),
        "out_stock": all_products.filter(stock=0).count(),
        "stock_total": all_products.aggregate(total=Sum("stock"))["total"] or 0,
    }
    products = list(products_qs)
    for product in products:
        product.price_display = format_vnd(product.price)
        product.latest_inventory_log = product.inventory_logs.first()
    return render(request, "staff/products.html", {
        "page_title": "Quản lý tồn kho",
        "products": products,
        "inventory_only": True,
        "categories": Category.objects.filter(is_active=True),
        "stats": stats,
    })


@login_required
def staff_inventory_update(request, product_id):
    if not staff_allowed(request.user):
        return staff_denied(request)
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    old_stock = product.stock
    form = InventoryUpdateForm(request.POST or None, initial={"new_stock": product.stock})
    if request.method == "POST" and form.is_valid():
        log = form.save(commit=False)
        log.product = product
        log.staff_user = request.user
        log.old_stock = old_stock
        log.save()
        product.stock = log.new_stock
        product.save(update_fields=["stock", "updated_at"])
        messages.success(request, "Cập nhật tồn kho thành công.")
        return redirect("shop:staff_inventory")
    return render(request, "staff/inventory_update.html", {
        "page_title": "Cập nhật tồn kho",
        "product": product,
        "form": form,
        "old_stock": old_stock,
        "latest_log": product.inventory_logs.first(),
    })


@login_required
def staff_inventory_report(request):
    if not staff_allowed(request.user):
        return staff_denied(request)
    all_products = Product.objects.filter(is_active=True)
    category_rows = Category.objects.annotate(total_stock=Sum("products__stock")).order_by("name")
    top_products = Product.objects.filter(is_active=True).order_by("-stock")[:10]
    low_products = Product.objects.filter(is_active=True, stock__gt=0, stock__lte=10).order_by("stock")[:10]
    low_stock_count = all_products.filter(stock__gt=0, stock__lte=10).count()
    top_category = category_rows.order_by("-total_stock").first()
    stats = {
        "total_products": all_products.count(),
        "stock_total": all_products.aggregate(total=Sum("stock"))["total"] or 0,
        "low_stock": low_stock_count,
        "out_stock": all_products.filter(stock=0).count(),
        "top_category": top_category.name if top_category and top_category.total_stock else "-",
    }
    return render(request, "staff/inventory_report.html", {
        "page_title": "Báo cáo tồn kho",
        "stats": stats,
        "category_chart": {"labels": [row.name for row in category_rows], "values": [row.total_stock or 0 for row in category_rows]},
        "low_stock_chart": {"labels": [p.name for p in low_products], "values": [p.stock for p in low_products]},
        "top_stock_chart": {"labels": [p.name for p in top_products], "values": [p.stock for p in top_products]},
    })


@login_required
def staff_customers(request):
    if not staff_allowed(request.user):
        return staff_denied(request)
    customers = User.objects.select_related("profile").filter(profile__role="CUSTOMER").annotate(
        order_count=Count("orders"),
        total_spent=Sum("orders__total_amount", filter=Q(orders__status=Order.STATUS_COMPLETED)),
    ).order_by("-date_joined")
    customers = list(customers)
    for customer in customers:
        customer.total_spent_display = format_vnd(customer.total_spent)
    return render(request, "staff/customers.html", {
        "page_title": "Khách hàng",
        "customers": customers,
    })
