from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import CustomerProfile


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email hoặc tên đăng nhập",
        widget=forms.TextInput(attrs={
            "placeholder": "Email hoặc tên đăng nhập",
            "autocomplete": "username",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Mật khẩu",
            "autocomplete": "current-password",
        }),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and "@" in username:
            user = User.objects.filter(email__iexact=username).first()
            if user:
                username = user.username
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Thông tin đăng nhập chưa đúng.")
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label="Họ tên",
        max_length=160,
        widget=forms.TextInput(attrs={"placeholder": "Họ tên", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email", "autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Số điện thoại",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Số điện thoại", "autocomplete": "tel"}),
    )
    address = forms.CharField(
        label="Địa chỉ",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Địa chỉ", "autocomplete": "street-address"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "phone", "address", "password1", "password2"]
        widgets = {"username": forms.TextInput(attrs={"placeholder": "Tên đăng nhập", "autocomplete": "username"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Tên đăng nhập"
        self.fields["password1"].label = "Mật khẩu"
        self.fields["password2"].label = "Nhập lại mật khẩu"
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Mật khẩu",
            "autocomplete": "new-password",
        })
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Nhập lại mật khẩu",
            "autocomplete": "new-password",
        })

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã được sử dụng.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        first, _, last = self.cleaned_data["full_name"].partition(" ")
        user.first_name = first
        user.last_name = last
        if commit:
            user.save()
            CustomerProfile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": self.cleaned_data["full_name"],
                    "phone": self.cleaned_data["phone"],
                    "address": self.cleaned_data["address"],
                },
            )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["full_name", "phone", "address", "avatar"]
