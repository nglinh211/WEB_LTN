from django import forms

from .models import CartItem, InventoryLog, Order, ProductReview, SaleCampaign


class ProductFilterForm(forms.Form):
    q = forms.CharField(required=False, label="", widget=forms.TextInput(attrs={"placeholder": "Tìm sản phẩm"}))
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("newest", "Mới nhất"),
            ("price_asc", "Giá tăng dần"),
            ("price_desc", "Giá giảm dần"),
        ],
    )


class CartItemUpdateForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ["quantity"]
        widgets = {"quantity": forms.NumberInput(attrs={"min": 1})}

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Số lượng phải lớn hơn 0.")
        if self.instance.product and quantity > self.instance.product.stock:
            raise forms.ValidationError("Số lượng vượt quá tồn kho.")
        return quantity


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "phone", "address", "note", "payment_method"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Họ tên"}),
            "phone": forms.TextInput(attrs={"placeholder": "Số điện thoại"}),
            "address": forms.TextInput(attrs={"placeholder": "Địa chỉ nhận hàng"}),
            "note": forms.Textarea(attrs={"placeholder": "Ghi chú", "rows": 4}),
            "payment_method": forms.Select(),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if len(phone) < 9 or len(phone) > 15:
            raise forms.ValidationError("Số điện thoại không hợp lệ.")
        return phone


class SaleCampaignForm(forms.ModelForm):
    class Meta:
        model = SaleCampaign
        fields = [
            "name",
            "description",
            "discount_type",
            "discount_value",
            "start_date",
            "end_date",
            "is_active",
            "banner_image",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Tên chương trình sale"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Mô tả ngắn"}),
            "discount_type": forms.Select(),
            "discount_value": forms.NumberInput(attrs={"min": 1, "placeholder": "Giá trị giảm"}),
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_date"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        discount_type = cleaned.get("discount_type")
        discount_value = cleaned.get("discount_value")
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")

        if discount_type == SaleCampaign.DISCOUNT_PERCENT and discount_value is not None:
            if discount_value < 1 or discount_value > 90:
                self.add_error("discount_value", "Phần trăm giảm phải từ 1 đến 90.")
        if discount_type == SaleCampaign.DISCOUNT_FIXED and discount_value is not None:
            if discount_value <= 0:
                self.add_error("discount_value", "Giá trị giảm cố định phải lớn hơn 0.")
        if start_date and end_date and end_date <= start_date:
            self.add_error("end_date", "Ngày kết thúc phải lớn hơn ngày bắt đầu.")
        return cleaned


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(5, "5 sao"), (4, "4 sao"), (3, "3 sao"), (2, "2 sao"), (1, "1 sao")]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Chia sẻ cảm nhận của bạn về sản phẩm"}),
        }

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()
        if len(comment) < 5:
            raise forms.ValidationError("Nhận xét cần tối thiểu 5 ký tự.")
        return comment


class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ["new_stock", "note"]
        widgets = {
            "new_stock": forms.NumberInput(attrs={"min": 0, "placeholder": "Số lượng mới"}),
            "note": forms.Textarea(attrs={"rows": 4, "placeholder": "Ghi chú cập nhật tồn kho"}),
        }

    def clean_new_stock(self):
        value = self.cleaned_data["new_stock"]
        if value < 0:
            raise forms.ValidationError("Tồn kho không được nhỏ hơn 0.")
        return value
