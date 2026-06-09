from decimal import Decimal
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CustomerProfile
from shop.models import Banner, BlogPost, Category, Collection, InventoryLog, Order, OrderItem, Product, ProductReview, SaleCampaign, SaleTarget


def copy_static_asset(self, source_filename, relative_path, copy_to_media=False):
    """
    Copy ảnh từ static/WEBIMG sang static/img hoặc media.
    Không phụ thuộc SOURCE_FRONTEND_DIR nữa.
    """
    source = settings.BASE_DIR / "static" / "WEBIMG" / source_filename
    static_target = settings.BASE_DIR / "static" / relative_path

    if not source.exists():
        self.stdout.write(self.style.WARNING(f"Không tìm thấy ảnh: {source}"))
        return ""

    static_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, static_target)

    if copy_to_media:
        media_target = settings.MEDIA_ROOT / relative_path
        media_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, media_target)
        return relative_path

    return relative_path


def copy_image(self, filename):
    """
    Copy ảnh từ static/WEBIMG sang media/seed.
    """
    source = settings.BASE_DIR / "static" / "WEBIMG" / filename
    target = settings.MEDIA_ROOT / "seed" / filename

    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return f"seed/{filename}"

    self.stdout.write(self.style.WARNING(f"Không tìm thấy ảnh: {source}"))
    return ""

class Command(BaseCommand):
    help = "Seed demo data for L.T.N Clothing."

    def copy_static_asset(self, source_filename, relative_path, copy_to_media=False):
        source = settings.BASE_DIR / "static" / "WEBIMG" / source_filename
        static_target = settings.BASE_DIR / "static" / relative_path
        if not source.exists():
            return ""
        static_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, static_target)
        if copy_to_media:
            media_target = settings.MEDIA_ROOT / relative_path
            media_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, media_target)
            return relative_path
        return relative_path

    def copy_image(self, filename):
        source = settings.BASE_DIR / "static" / "WEBIMG" / filename
        target = settings.MEDIA_ROOT / "seed" / filename
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            return f"seed/{filename}"
        return ""

    def handle(self, *args, **options):
        self.copy_static_asset("tiệc.3.jpg", "img/hero/tiec-3.jpg")

        product_image_map = {
            "dam-tiec-satin-trang.jpg": "tiệc.3.jpg",
            "dam-hong-nu-tinh.jpg": "tiệc.5.jpg",
            "blazer-nu-thanh-lich.jpg": "đồ coogn sở.jpg",
            "tui-da-nu.jpg": "baby.jpg",
            "chan-vay-cong-so.jpg": "đồ công sở.jpg",
            "set-mac-nha-mem-mai.jpg": "mặc nhà.jpg",
            "ao-kieu-nu-thanh-lich.jpg": "sang trọng.3.png",
            "quan-suong-nu-hien-dai.jpg": "đi làm.2.jpg",
            "dam-trang-toi-gian.jpg": "tối giản.1.png",
            "so-mi-satin-mau-kem.jpg": "công sở.1.jpg",
            "chan-vay-midi-satin.jpg": "hẹn hò.2.jpg",
            "set-the-thao-burgundy.jpg": "thể thao 2.jpg",
        }
        product_images = {
            clean_name: self.copy_static_asset(source_name, f"img/products/{clean_name}", copy_to_media=True)
            for clean_name, source_name in product_image_map.items()
        }

        image_names = [
            "tiệc.5.jpg", "sang trọng.1.png", "sang trọng.2.png", "sang trọng.3.png",
            "tối giản.1.png", "tối giản. 2.png", "tối giản .3.png", "công sở.1.jpg",
            "hiện đâị + basic.1.png", "hiện đâị + basic.2.png", "hiện đâị + basic.3.png",
            "đi làm.jpg", "đi làm.2.jpg", "đi làm.3.jpg", "đi làm.4.jpg",
            "đi chơi.jpg", "đi chơi.3.jpg", "đi chơi.4.jpg", "đi chơi.6.jpg", "đi chơi.7.jpg",
            "hẹn hò.jpg", "hẹn hò.2.jpg", "tiệc.6.jpg", "tiệc.7.jpg", "tiệc.9.jpg", "tiệc.10.jpg", "tiệc.11.jpg",
            "mặc nhà.jpg", "nhà.jpg", "nhà.2.jpg", "nhà.3.jpg", "đồ ở nhà.jpg",
            "thể thao1.jpg", "thể thao 2.jpg", "thể thao 3.jpg", "thể thao 4.jpg",
            "đồ đi chơi.jpg", "đồ đi chơi.2.jpg", "đồ công sở.jpg", "đồ công sở.4.jpg",
            "đồ công sở.5.jpg", "đồ coogn sở.jpg", "baby.jpg",
        ]
        copied = {name: self.copy_image(name) for name in image_names}

        category_rows = [
            ("Đi chơi", "di-choi", "Trang phục dạo phố, hẹn hò và cafe cuối tuần."),
            ("Ở nhà", "o-nha", "Set mặc nhà mềm mại, thoải mái và vẫn chỉn chu."),
            ("Đầm", "dam", "Đầm nữ thanh lịch cho công sở, đi chơi và dự tiệc."),
            ("Áo", "ao", "Áo sơ mi, áo thun và áo kiểu nữ dễ phối."),
            ("Quần", "quan", "Quần âu, quần suông và thiết kế cạp cao."),
            ("Chân váy", "chan-vay", "Chân váy nữ tính, hiện đại và dễ ứng dụng."),
            ("Áo khoác", "ao-khoac", "Blazer, áo khoác nhẹ và điểm nhấn layering."),
            ("Sale", "sale", "Sản phẩm ưu đãi theo mùa."),
            ("Phụ kiện", "phu-kien", "Túi, phụ kiện và gam màu cherry hoàn thiện set đồ."),
        ]
        categories = {}
        for index, (name, slug, desc) in enumerate(category_rows, 1):
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "image": copied.get(image_names[index % len(image_names)], ""),
                    "icon": copied.get(image_names[(index + 3) % len(image_names)], ""),
                    "sort_order": index,
                    "is_active": True,
                },
            )
            categories[slug] = category

        products = [
            {
                "sku": "LTN001",
                "name": "Đầm tiệc satin trắng",
                "category": "dam",
                "image": product_images["dam-tiec-satin-trang.jpg"],
                "description": "Thiết kế đầm satin trắng thanh lịch, phù hợp cho tiệc nhẹ và những dịp đặc biệt.",
                "price": Decimal("1250000"),
                "sale_price": Decimal("1090000"),
                "stock": 12,
                "is_featured": True,
                "is_new": True,
                "is_sale": True,
            },
            {
                "sku": "LTN002",
                "name": "Đầm hồng nữ tính",
                "category": "dam",
                "image": product_images["dam-hong-nu-tinh.jpg"],
                "description": "Đầm hồng phom mềm mại, tôn nét nữ tính trong các buổi hẹn và sự kiện ban ngày.",
                "price": Decimal("1180000"),
                "sale_price": None,
                "stock": 15,
                "is_featured": True,
                "is_new": True,
                "is_sale": False,
            },
            {
                "sku": "LTN003",
                "name": "Blazer nữ thanh lịch",
                "category": "ao-khoac",
                "image": product_images["blazer-nu-thanh-lich.jpg"],
                "description": "Blazer nữ gam sáng, đường cắt gọn gàng cho phong cách công sở hiện đại.",
                "price": Decimal("1390000"),
                "sale_price": Decimal("1250000"),
                "stock": 9,
                "is_featured": True,
                "is_new": False,
                "is_sale": True,
            },
            {
                "sku": "LTN004",
                "name": "Túi da nữ",
                "category": "phu-kien",
                "image": product_images["tui-da-nu.jpg"],
                "description": "Túi da nữ nhỏ gọn, dễ phối cùng đầm, blazer và các set dạo phố.",
                "price": Decimal("690000"),
                "sale_price": None,
                "stock": 22,
                "is_featured": True,
                "is_new": False,
                "is_sale": False,
            },
            {
                "sku": "LTN005",
                "name": "Chân váy công sở",
                "category": "chan-vay",
                "image": product_images["chan-vay-cong-so.jpg"],
                "description": "Chân váy công sở dáng gọn, chất liệu đứng phom và dễ phối cùng áo sơ mi.",
                "price": Decimal("760000"),
                "sale_price": Decimal("690000"),
                "stock": 18,
                "is_featured": True,
                "is_new": False,
                "is_sale": True,
            },
            {
                "sku": "LTN006",
                "name": "Set mặc nhà mềm mại",
                "category": "o-nha",
                "image": product_images["set-mac-nha-mem-mai.jpg"],
                "description": "Set mặc nhà mềm mại, thoải mái nhưng vẫn chỉn chu cho những ngày thư giãn.",
                "price": Decimal("620000"),
                "sale_price": None,
                "stock": 20,
                "is_featured": True,
                "is_new": False,
                "is_sale": False,
            },
            {
                "sku": "LTN007",
                "name": "Áo kiểu nữ thanh lịch",
                "category": "ao",
                "image": product_images["ao-kieu-nu-thanh-lich.jpg"],
                "description": "Áo kiểu nữ thanh lịch với chi tiết mềm mại, phù hợp đi làm, đi chơi và gặp gỡ.",
                "price": Decimal("850000"),
                "sale_price": Decimal("790000"),
                "stock": 14,
                "is_featured": True,
                "is_new": True,
                "is_sale": True,
            },
            {
                "sku": "LTN008",
                "name": "Quần suông nữ hiện đại",
                "category": "quan",
                "image": product_images["quan-suong-nu-hien-dai.jpg"],
                "description": "Quần suông nữ hiện đại, cạp cao vừa vặn và dễ kết hợp với áo kiểu hoặc blazer.",
                "price": Decimal("820000"),
                "sale_price": None,
                "stock": 16,
                "is_featured": True,
                "is_new": False,
                "is_sale": False,
            },
            {
                "sku": "LTN009",
                "name": "Đầm trắng tối giản",
                "category": "dam",
                "image": product_images["dam-trang-toi-gian.jpg"],
                "description": "Đầm trắng tối giản, tinh tế cho phong cách nhẹ nhàng và dễ ứng dụng hằng ngày.",
                "price": Decimal("980000"),
                "sale_price": Decimal("890000"),
                "stock": 10,
                "is_featured": False,
                "is_new": True,
                "is_sale": True,
            },
            {
                "sku": "LTN010",
                "name": "Sơ mi satin màu kem",
                "category": "ao",
                "image": product_images["so-mi-satin-mau-kem.jpg"],
                "description": "Sơ mi satin màu kem có bề mặt mềm mượt, hợp với quần suông và chân váy công sở.",
                "price": Decimal("720000"),
                "sale_price": None,
                "stock": 24,
                "is_featured": False,
                "is_new": True,
                "is_sale": False,
            },
            {
                "sku": "LTN011",
                "name": "Chân váy midi satin",
                "category": "chan-vay",
                "image": product_images["chan-vay-midi-satin.jpg"],
                "description": "Chân váy midi satin nữ tính, tạo chuyển động mềm mại trong từng bước đi.",
                "price": Decimal("790000"),
                "sale_price": Decimal("720000"),
                "stock": 11,
                "is_featured": False,
                "is_new": False,
                "is_sale": True,
            },
            {
                "sku": "LTN012",
                "name": "Set thể thao đỏ rượu",
                "category": "sale",
                "image": product_images["set-the-thao-burgundy.jpg"],
                "description": "Set thể thao đỏ rượu năng động, thoải mái cho luyện tập nhẹ và cuối tuần.",
                "price": Decimal("680000"),
                "sale_price": Decimal("590000"),
                "stock": 7,
                "is_featured": False,
                "is_new": False,
                "is_sale": True,
            },
        ]
        active_skus = [item["sku"] for item in products]
        Product.objects.filter(sku__startswith="LTN").exclude(sku__in=active_skus).update(is_active=False)
        product_objects = []
        for index, item in enumerate(products, 1):
            product, _ = Product.objects.update_or_create(
                sku=item["sku"],
                defaults={
                    "category": categories[item["category"]],
                    "name": item["name"],
                    "slug": f"ltn-{index:03d}",
                    "description": item["description"],
                    "price": item["price"],
                    "sale_price": item["sale_price"],
                    "stock": item["stock"],
                    "main_image": item["image"],
                    "is_featured": item["is_featured"],
                    "is_new": item["is_new"],
                    "is_sale": item["is_sale"],
                    "is_active": True,
                },
            )
            product_objects.append(product)

        collection_images = [
            "sang trọng.1.png", "tối giản.1.png", "đi chơi.4.jpg",
            "đi làm.2.jpg", "mặc nhà.jpg", "thể thao 2.jpg",
        ]
        banner_images = [
            "tiệc.5.jpg", "sang trọng.2.png", "tiệc.10.jpg",
            "đi chơi.6.jpg", "nhà.jpg", "đồ công sở.4.jpg",
        ]
        collection_titles = [
            "BST Xuân Hè 2026",
            "BST Công Sở",
            "BST Tiệc Tối",
            "Modern Lady",
            "Elegant Office",
            "Dấu Ấn Phong Cách",
        ]
        collections = []
        for index, image_name in enumerate(collection_images, 1):
            collection, _ = Collection.objects.update_or_create(
                slug=f"bst-ltn-{index}",
                defaults={
                    "title": collection_titles[index - 1],
                    "subtitle": "",
                    "description": "Bộ sưu tập cân bằng giữa nữ tính, chỉn chu và ứng dụng hằng ngày.",
                    "banner_image": copied.get(image_name, ""),
                    "is_active": True,
                },
            )
            collection.products.set(product_objects[(index - 1) * 4:index * 4])
            collections.append(collection)

        for index, image_name in enumerate(banner_images, 1):
            Banner.objects.update_or_create(
                title=f"Banner L.T.N {index}",
                defaults={
                    "subtitle": "Sắc đỏ đô chủ đạo, tinh thần hiện đại",
                    "image": copied.get(image_name, ""),
                    "button_text": "Khám phá",
                    "button_url": "/products/",
                    "position": Banner.POSITION_HERO if index == 1 else Banner.POSITION_GRID,
                    "is_active": True,
                    "sort_order": index,
                },
            )

        now = timezone.now()
        SaleCampaign.objects.filter(slug="burgundy-muse-150k").delete()
        campaign_rows = [
            ("Summer Sale 20%", "summer-sale-20", SaleCampaign.DISCOUNT_PERCENT, Decimal("20"), now - timezone.timedelta(days=2), now + timezone.timedelta(days=20), "Sale mùa hè cho các thiết kế dễ mặc."),
            ("L.T.N Muse giảm 150.000đ", "ltn-muse-150k", SaleCampaign.DISCOUNT_FIXED, Decimal("150000"), now - timezone.timedelta(days=1), now + timezone.timedelta(days=25), "Ưu đãi cố định cho bộ sưu tập sắc đỏ L.T.N."),
            ("Flash Sale 30%", "flash-sale-30", SaleCampaign.DISCOUNT_PERCENT, Decimal("30"), now - timezone.timedelta(hours=2), now + timezone.timedelta(days=3), "Flash sale ngắn hạn cho danh mục sale."),
        ]
        campaigns = {}
        for name, slug, discount_type, discount_value, start_date, end_date, description in campaign_rows:
            campaign, _ = SaleCampaign.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "discount_type": discount_type,
                    "discount_value": discount_value,
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_active": True,
                    "banner_image": copied.get("sang trọng.2.png", ""),
                },
            )
            campaign.targets.all().delete()
            campaigns[slug] = campaign

        for product in product_objects[:4]:
            SaleTarget.objects.get_or_create(campaign=campaigns["summer-sale-20"], product=product)
        SaleTarget.objects.get_or_create(campaign=campaigns["ltn-muse-150k"], category=categories["dam"])
        if collections:
            SaleTarget.objects.get_or_create(campaign=campaigns["flash-sale-30"], collection=collections[0])
        else:
            SaleTarget.objects.get_or_create(campaign=campaigns["flash-sale-30"], category=categories["sale"])

        posts = [
            ("Bộ sưu tập L.T.N Muse ra mắt", "Sắc đỏ đô chủ đạo được làm mới bằng lụa, nhung và đường cắt hiện đại."),
            ("5 cách phối satin trắng cho ngày hè", "Gợi ý phối satin với đỏ rượu, denim sáng màu và phụ kiện ánh vàng nhẹ."),
            ("Dịch vụ tư vấn phong cách cá nhân", "Stylist của L.T.N giúp bạn hoàn thiện tủ đồ theo lịch làm việc và sự kiện."),
            ("Tủ đồ công sở tối giản", "Các thiết kế cơ bản giúp ngày làm việc gọn gàng và tinh tế."),
            ("Chọn phụ kiện cho set đỏ đô", "Túi nhỏ, ánh gold và màu kem tạo điểm cân bằng cho tổng thể."),
        ]
        for index, (title, summary) in enumerate(posts, 1):
            BlogPost.objects.update_or_create(
                slug=f"blog-ltn-{index}",
                defaults={
                    "title": title,
                    "summary": summary,
                    "content": summary + "\n\nNội dung mẫu cho website Django L.T.N Clothing.",
                    "thumbnail": copied.get("tiệc.5.jpg", ""),
                    "is_published": True,
                },
            )

        demo_users = [
            ("admin", "admin@ltn.com", "admin123", "Quản trị L.T.N", "0901000001", "ADMIN", True, True),
            ("staff", "staff@ltn.com", "staff123", "Nhân viên cửa hàng", "0901000002", "STAFF", True, False),
            ("customer", "customer@ltn.com", "customer123", "Khách hàng demo", "0901000003", "CUSTOMER", False, False),
        ]
        for index in range(1, 9):
            demo_users.append((f"customer{index}", f"customer{index}@ltn.com", "customer123", f"Khách hàng {index}", f"09020000{index:02d}", "CUSTOMER", False, False))

        users_by_username = {}
        for username, email, password, full_name, phone, role, is_staff, is_superuser in demo_users:
            user, _ = User.objects.get_or_create(username=username, defaults={"email": email})
            user.email = email
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.first_name = full_name.split(" ")[0]
            user.last_name = " ".join(full_name.split(" ")[1:])
            user.set_password(password)
            user.save()
            CustomerProfile.objects.update_or_create(
                user=user,
                defaults={"full_name": full_name, "phone": phone, "address": "TP.HCM", "role": role},
            )
            users_by_username[username] = user

        Order.objects.filter(note__startswith="DEMO-SEED").delete()
        statuses = [Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_SHIPPING, Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]
        payment_methods = [Order.PAYMENT_COD, Order.PAYMENT_BANK]
        customer_users = [users_by_username[f"customer{index}"] for index in range(1, 9)] + [users_by_username["customer"]]
        for index in range(1, 13):
            user = customer_users[index % len(customer_users)]
            profile = user.profile
            product_a = product_objects[(index * 2) % len(product_objects)]
            product_b = product_objects[(index * 2 + 5) % len(product_objects)]
            qty_a = (index % 3) + 1
            qty_b = 1
            total = product_a.final_price * qty_a + product_b.final_price * qty_b
            order = Order.objects.create(
                user=user,
                full_name=profile.full_name,
                phone=profile.phone or "0900000000",
                address=profile.address or "TP.HCM",
                note=f"DEMO-SEED-{index}",
                total_amount=total,
                status=statuses[index % len(statuses)],
                payment_method=payment_methods[index % len(payment_methods)],
            )
            created_at = timezone.now() - timezone.timedelta(days=12 - index)
            Order.objects.filter(pk=order.pk).update(created_at=created_at, updated_at=created_at)
            for product, qty in [(product_a, qty_a), (product_b, qty_b)]:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.final_price,
                    quantity=qty,
                    subtotal=product.final_price * qty,
                )

        review_comments = [
            "Chất vải mềm, mặc rất thoải mái.",
            "Form dáng đẹp, đúng như hình.",
            "Màu sắc trang nhã, dễ phối đồ.",
            "Giao hàng nhanh, đóng gói cẩn thận.",
            "Sản phẩm phù hợp đi làm và đi chơi.",
            "Đường may chắc chắn, mặc lên rất tôn dáng.",
            "Chất liệu nhẹ và thoáng, mình rất hài lòng.",
            "Thiết kế nữ tính, sắc đỏ rượu rất sang.",
        ]
        customer_users_for_reviews = customer_users + [users_by_username["customer"]]
        ProductReview.objects.filter(comment__in=review_comments).delete()
        for index in range(30):
            product = product_objects[index % len(product_objects)]
            user = customer_users_for_reviews[index % len(customer_users_for_reviews)]
            if ProductReview.objects.filter(product=product, user=user).exists():
                continue
            ProductReview.objects.create(
                product=product,
                user=user,
                rating=5 if index % 5 else 3 if index % 11 == 0 else 4,
                comment=review_comments[index % len(review_comments)],
                is_approved=True,
            )

        InventoryLog.objects.filter(note__startswith="DEMO-SEED").delete()
        staff_user = users_by_username["staff"]
        for index, product in enumerate(product_objects[:8], 1):
            old_stock = product.stock
            new_stock = old_stock + index
            InventoryLog.objects.create(
                product=product,
                staff_user=staff_user,
                old_stock=old_stock,
                new_stock=new_stock,
                note=f"DEMO-SEED cập nhật tồn kho mẫu {index}",
            )

        self.stdout.write(self.style.SUCCESS("Seeded rich dashboard demo data successfully."))
