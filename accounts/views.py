from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import EmailOrUsernameAuthenticationForm, ProfileForm, RegisterForm


class CustomerLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = EmailOrUsernameAuthenticationForm

    def get_success_url(self):
        redirect_to = self.request.POST.get(self.redirect_field_name) or self.request.GET.get(self.redirect_field_name)
        if redirect_to and url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect_to

        profile = getattr(self.request.user, "profile", None)
        role = getattr(profile, "role", "")
        if self.request.user.is_superuser or role == "ADMIN":
            return reverse("shop:dashboard")
        if role == "STAFF":
            return reverse("shop:staff_dashboard")
        return reverse("accounts:profile")


class CustomerLogoutView(LogoutView):
    pass


def register(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Đăng ký thành công.")
        return redirect("shop:home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật hồ sơ.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def orders(request):
    return render(request, "accounts/orders.html", {"orders": request.user.orders.prefetch_related("items")})
