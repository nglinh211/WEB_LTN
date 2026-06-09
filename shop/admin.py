from django.contrib import admin, messages

from .models import Banner, BlogPost, Cart, CartItem, Category, Collection, InventoryLog, Order, OrderItem, Product, ProductImage, ProductReview, SaleCampaign, SaleTarget, Wishlist

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    def delete_model(self, request, obj):
        """
        Xử lý khi xóa một danh mục.
        """

        if obj.products.exists():
            messages.error(
                request,
                "Không thể xóa danh mục vì vẫn còn sản phẩm thuộc danh mục này."
            )
            return

        super().delete_model(request, obj)

        messages.success(
            request,
            "Xóa danh mục thành công."
        )

   
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sku", "price", "sale_price", "stock", "is_featured", "is_new", "is_sale", "is_active")
    list_filter = ("category", "is_featured", "is_new", "is_sale", "is_active")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    def has_add_permission(self, request):
        """
        Chỉ Admin mới được thêm sản phẩm.
        """
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        """
        Xử lý khi thêm hoặc cập nhật sản phẩm.
        """

        # Kiểm tra dữ liệu
        if obj.price <= 0:
            messages.error(
                request,
                "Giá sản phẩm phải lớn hơn 0."
            )
            return

        if obj.stock < 0:
            messages.error(
                request,
                "Tồn kho không được nhỏ hơn 0."
            )
            return

        # Lưu dữ liệu
        super().save_model(
            request,
            obj,
            form,
            change
        )

        # Thông báo
        if change:
            messages.success(
                request,
                "Cập nhật sản phẩm thành công."
            )
        else:
            messages.success(
                request,
                "Thêm sản phẩm thành công."
            )



class SaleTargetInline(admin.TabularInline):
    model = SaleTarget
    extra = 1


@admin.register(SaleCampaign)
class SaleCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "discount_type", "discount_value", "start_date", "end_date", "is_active", "status_label")
    list_filter = ("discount_type", "is_active", "start_date", "end_date")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SaleTargetInline]


@admin.register(SaleTarget)
class SaleTargetAdmin(admin.ModelAdmin):
    list_display = ("campaign", "product", "category", "collection", "created_at")
    list_filter = ("campaign", "category", "collection")
    search_fields = ("campaign__name", "product__name", "category__name", "collection__title")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity", "subtotal")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "total_amount", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("full_name", "phone", "address")
    inlines = [OrderItemInline]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}

    def has_add_permission(self, request):
        """
        Chỉ Admin mới được thêm bài viết.
        """
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        """
        Xử lý khi thêm hoặc cập nhật bài viết.
        """

        # Kiểm tra dữ liệu
        if not obj.title.strip():
            messages.error(
                request,
                "Tiêu đề bài viết không được để trống."
            )
            return

        if not obj.content.strip():
            messages.error(
                request,
                "Nội dung bài viết không được để trống."
            )
            return

        # Lưu dữ liệu
        super().save_model(
            request,
            obj,
            form,
            change
        )

        # Thông báo
        if change:
            messages.success(
                request,
                "Cập nhật bài viết thành công."
            )
        else:
            messages.success(
                request,
                "Thêm bài viết thành công."
            )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "position", "sort_order", "is_active")
    list_filter = ("position", "is_active")
    search_fields = ("title", "subtitle")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = ("product__name", "user__username", "comment")


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ("product", "staff_user", "old_stock", "new_stock", "created_at")
    list_filter = ("created_at",)
    search_fields = ("product__name", "product__sku", "staff_user__username", "note")
