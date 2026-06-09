from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(instance, source_field, slug_field="slug"):
    base_slug = slugify(getattr(instance, source_field), allow_unicode=True) or "ltn"
    slug = base_slug
    model = instance.__class__
    counter = 2
    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True, allow_unicode=True)
    icon = models.ImageField(upload_to="categories/icons/", blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "name")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:category_products", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=210, unique=True, blank=True, allow_unicode=True)
    sku = models.CharField(max_length=60, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=0)
    sale_price = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "name")
        super().save(*args, **kwargs)

    def get_active_sale(self):
        now = timezone.now()
        targets = SaleTarget.objects.select_related("campaign").filter(
            campaign__is_active=True,
            campaign__start_date__lte=now,
            campaign__end_date__gte=now,
        ).filter(
            models.Q(product=self) |
            models.Q(category=self.category) |
            models.Q(collection__products=self)
        )
        best_campaign = None
        best_price = self.price
        best_priority = 99
        for target in targets:
            priority = target.priority
            sale_price = target.campaign.apply_discount(self.price)
            if priority < best_priority or (priority == best_priority and sale_price < best_price):
                best_campaign = target.campaign
                best_price = sale_price
                best_priority = priority
        if best_campaign:
            best_campaign._ltn_sale_price = best_price
            best_campaign._ltn_target_priority = best_priority
        return best_campaign

    def get_final_price(self):
        campaign = self.get_active_sale()
        if campaign:
            return campaign._ltn_sale_price
        if self.sale_price is not None and self.sale_price < self.price:
            return max(Decimal("0"), self.sale_price)
        return self.price

    def get_discount_percent(self):
        final_price = self.get_final_price()
        if final_price >= self.price or not self.price:
            return 0
        return int(((self.price - final_price) / self.price * Decimal("100")).quantize(Decimal("1")))

    def is_on_sale(self):
        return self.get_final_price() < self.price

    @property
    def final_price(self):
        return self.get_final_price()

    @property
    def has_sale(self):
        return self.is_on_sale()

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        value = self.reviews.filter(is_approved=True).aggregate(avg=Avg("rating"))["avg"] or 0
        return round(float(value), 1)

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.alt_text or f"Ảnh {self.product.name}"


class Collection(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=210, unique=True, blank=True, allow_unicode=True)
    subtitle = models.CharField(max_length=220, blank=True)
    banner_image = models.ImageField(upload_to="collections/", blank=True, null=True)
    description = models.TextField(blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name="collections")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "title")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:collection_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class SaleCampaign(TimeStampedModel):
    DISCOUNT_PERCENT = "percent"
    DISCOUNT_FIXED = "fixed"
    DISCOUNT_CHOICES = [
        (DISCOUNT_PERCENT, "Theo phần trăm"),
        (DISCOUNT_FIXED, "Giảm tiền cố định"),
    ]

    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=210, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_CHOICES, default=DISCOUNT_PERCENT)
    discount_value = models.DecimalField(max_digits=12, decimal_places=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    banner_image = models.ImageField(upload_to="sales/", blank=True, null=True)

    class Meta:
        ordering = ["-start_date", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "name")
        super().save(*args, **kwargs)

    def clean(self):
        if self.discount_type == self.DISCOUNT_PERCENT and not (Decimal("1") <= self.discount_value <= Decimal("90")):
            raise ValidationError({"discount_value": "Phần trăm giảm phải từ 1 đến 90."})
        if self.discount_type == self.DISCOUNT_FIXED and self.discount_value <= 0:
            raise ValidationError({"discount_value": "Giá trị giảm cố định phải lớn hơn 0."})
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "Ngày kết thúc phải lớn hơn ngày bắt đầu."})

    def apply_discount(self, price):
        price = Decimal(price or 0)
        if self.discount_type == self.DISCOUNT_PERCENT:
            value = price * (Decimal("1") - self.discount_value / Decimal("100"))
        else:
            value = price - self.discount_value
        return max(Decimal("0"), value.quantize(Decimal("1")))

    @property
    def status_key(self):
        now = timezone.now()
        if not self.is_active:
            return "disabled"
        if self.start_date > now:
            return "upcoming"
        if self.end_date < now:
            return "ended"
        return "running"

    @property
    def status_label(self):
        return {
            "running": "Đang chạy",
            "upcoming": "Sắp diễn ra",
            "ended": "Đã kết thúc",
            "disabled": "Tạm tắt",
        }[self.status_key]

    @property
    def discount_label(self):
        if self.discount_type == self.DISCOUNT_PERCENT:
            return f"-{int(self.discount_value)}%"
        return f"-{int(self.discount_value):,}".replace(",", ".") + " đ"

    def __str__(self):
        return self.name


class SaleTarget(models.Model):
    campaign = models.ForeignKey(SaleCampaign, on_delete=models.CASCADE, related_name="targets")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sale_targets", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sale_targets", blank=True, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="sale_targets", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["campaign", "product"], name="uniq_sale_campaign_product"),
            models.UniqueConstraint(fields=["campaign", "category"], name="uniq_sale_campaign_category"),
            models.UniqueConstraint(fields=["campaign", "collection"], name="uniq_sale_campaign_collection"),
        ]

    @property
    def priority(self):
        if self.product_id:
            return 0
        if self.collection_id:
            return 1
        return 2

    @property
    def target_label(self):
        if self.product_id:
            return f"Sản phẩm: {self.product.name}"
        if self.collection_id:
            return f"BST: {self.collection.title}"
        if self.category_id:
            return f"Danh mục: {self.category.name}"
        return "Chưa chọn target"

    def clean(self):
        selected = [bool(self.product_id), bool(self.category_id), bool(self.collection_id)]
        if sum(selected) != 1:
            raise ValidationError("Mỗi target chỉ được chọn một trong: sản phẩm, danh mục hoặc bộ sưu tập.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campaign} - {self.target_label}"


class Banner(models.Model):
    POSITION_HERO = "hero"
    POSITION_GRID = "grid"
    POSITION_FOOTER = "footer"
    POSITION_CHOICES = [
        (POSITION_HERO, "Hero"),
        (POSITION_GRID, "Grid"),
        (POSITION_FOOTER, "Footer"),
    ]

    title = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=220, blank=True)
    image = models.ImageField(upload_to="banners/", blank=True, null=True)
    button_text = models.CharField(max_length=80, blank=True)
    button_url = models.CharField(max_length=220, blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default=POSITION_GRID)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.product}"


class Cart(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")

    def total_amount(self):
        return sum((item.subtotal() for item in self.items.select_related("product")), Decimal("0"))

    def __str__(self):
        return f"Giỏ hàng của {self.user}"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def subtotal(self):
        return self.product.final_price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Order(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_SHIPPING = "shipping"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ xác nhận"),
        (STATUS_CONFIRMED, "Đã xác nhận"),
        (STATUS_SHIPPING, "Đang giao"),
        (STATUS_COMPLETED, "Hoàn thành"),
        (STATUS_CANCELLED, "Đã hủy"),
    ]
    PAYMENT_COD = "cod"
    PAYMENT_BANK = "bank_transfer"
    PAYMENT_CHOICES = [
        (PAYMENT_COD, "Thanh toán khi nhận hàng"),
        (PAYMENT_BANK, "Chuyển khoản"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default=PAYMENT_COD)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Đơn #{self.pk} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class ProductReview(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("product", "user")

    def clean(self):
        if self.comment and len(self.comment.strip()) < 5:
            raise ValidationError({"comment": "Nhận xét cần tối thiểu 5 ký tự."})

    @property
    def stars(self):
        return "★" * self.rating + "☆" * (5 - self.rating)

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating})"


class InventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_logs")
    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_logs")
    old_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name}: {self.old_stock} -> {self.new_stock}"


class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=210, unique=True, blank=True, allow_unicode=True)
    thumbnail = models.ImageField(upload_to="blog/", blank=True, null=True)
    summary = models.TextField()
    content = models.TextField()
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "title")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:blog_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title
