from .models import Cart, Wishlist


def dashboard_url_for_user(user):
    if not user.is_authenticated:
        return "/login/"
    role = getattr(getattr(user, "profile", None), "role", "")
    if user.is_superuser or role == "ADMIN":
        return "/dashboard/"
    if role == "STAFF":
        return "/staff/"
    return "/profile/"


def cart_counter(request):
    user_dashboard_url = dashboard_url_for_user(request.user)
    if not request.user.is_authenticated:
        return {"cart_count": 0, "wishlist_count": 0, "user_dashboard_url": user_dashboard_url}
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return {
        "cart_count": sum(item.quantity for item in cart.items.all()),
        "wishlist_count": Wishlist.objects.filter(user=request.user).count(),
        "user_dashboard_url": user_dashboard_url,
    }
