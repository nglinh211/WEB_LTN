from decimal import Decimal
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import BlogPost, Category, Product


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu cho L.T.N Clothing."

    def handle(self, *args, **options):
        image_map = {
            "cong-so": "công sở.1.jpg",
            "di-choi": "đi chơi.4.jpg",
            "o-nha": "mặc nhà.jpg",
            "phu-kien": "đi chơi.7.jpg",
            "sang-trong-1": "sang trọng.1.png",
            "sang-trong-2": "sang trọng.2.png",
            "tiec-5": "tiệc.5.jpg",
            "hen-ho": "hẹn hò.jpg",
            "the-thao": "thể thao 2.jpg",
            "basic": "đồ baisic.png",
            "di-lam": "đi làm.2.jpg",
            "tiec-9": "tiệc.9.jpg",
            "dam-cong-so": "đồ công sở.4.jpg",
        }
        copied = {}
        for key, filename in image_map.items():
            source = settings.SOURCE_FRONTEND_DIR / "WEBIMG" / filename
            target = settings.MEDIA_ROOT / "seed" / filename
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                copied[key] = f"seed/{filename}"

        categories_data = [
            ("Công sở", "cong-so", "Blazer, sơ mi satin và đầm gọn dáng cho môi trường chuyên nghiệp."),
            ("Đi chơi", "di-choi", "Trang phục trẻ trung, dễ phối cho cà phê, hẹn hò hoặc dạo phố."),
            ("Ở nhà", "o-nha", "Set mặc nhà mềm, thoáng và vẫn gọn đẹp trong đời sống hằng ngày."),
            ("Phụ kiện", "phu-kien", "Túi và điểm nhấn hoàn thiện phong cách burgundy."),
        ]
        categories = {}
        for name, slug, desc in categories_data:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "image": copied.get(slug, ""),
                    "is_active": True,
                },
            )
            categories[slug] = category

        products_data = [
            ("Blazer lụa đỏ đô", "LTN001", "cong-so", 1890000, None, 18, "sang-trong-1", True, "Blazer lụa đỏ đô, hình dáng gọn, hợp công sở và những buổi gặp cần sự chỉn chu."),
            ("Đầm nhung dự tiệc", "LTN002", "di-choi", 2450000, 2190000, 9, "tiec-5", True, "Đầm nhung mềm với đường cắt thanh lịch, tôn dáng mà vẫn dễ di chuyển."),
            ("Sơ mi satin màu kem", "LTN003", "cong-so", 890000, None, 31, "cong-so", True, "Sơ mi satin màu kem, mát nhẹ, dễ phối cùng chân váy hoặc quần âu."),
            ("Quần âu maroon cạp cao", "LTN004", "cong-so", 1190000, None, 15, "di-lam", False, "Quần âu cạp cao màu maroon, đường ly sắc nét cho ngày làm việc năng động."),
            ("Túi da cherry đỏ đô", "LTN005", "phu-kien", 1590000, None, 7, "di-choi", True, "Túi xách cherry đỏ đô với khóa kim loại nhỏ, vừa đủ cho ngày và đêm."),
            ("Áo thun trắng tối giản", "LTN006", "di-choi", 490000, None, 42, "basic", False, "Áo thun cotton trắng đứng form, logo nhỏ, phối nhanh với mọi tủ đồ."),
            ("Đầm midi hẹn hò", "LTN007", "di-choi", 1390000, 1250000, 13, "hen-ho", True, "Đầm midi mềm mại cho buổi hẹn, nhấn eo nhẹ và sắc đỏ rượu vang tinh tế."),
            ("Set mặc nhà mềm mại", "LTN008", "o-nha", 790000, None, 25, "o-nha", True, "Set mặc nhà chất liệu mềm, thoáng, vẫn gọn đẹp khi tiếp khách tại nhà."),
            ("Set thể thao burgundy", "LTN009", "di-choi", 990000, None, 20, "the-thao", False, "Set thể thao co giãn tốt, màu burgundy sang, phù hợp yoga và đi dạo."),
            ("Set basic hiện đại", "LTN010", "di-choi", 1290000, None, 16, "sang-trong-2", False, "Bộ co-ord hiện đại với tỷ lệ gọn, dành cho những ngày cần đẹp nhanh."),
            ("Áo champagne dự tiệc", "LTN011", "di-choi", 950000, None, 12, "tiec-9", False, "Áo đi tiệc màu champagne nhẹ, bắt sáng khuôn mặt và phối đẹp với quần ống suông."),
            ("Đầm công sở thanh lịch", "LTN012", "cong-so", 1690000, 1490000, 11, "dam-cong-so", True, "Đầm công sở gọn dáng, lịch sự, đủ trang trọng cho họp và tiệc nhẹ sau giờ làm."),
        ]
        for name, sku, category_slug, price, sale_price, stock, image_key, featured, desc in products_data:
            Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "category": categories[category_slug],
                    "name": name,
                    "slug": slugify(name),
                    "description": desc,
                    "price": Decimal(price),
                    "sale_price": Decimal(sale_price) if sale_price else None,
                    "stock": stock,
                    "main_image": copied.get(image_key, ""),
                    "is_featured": featured,
                    "is_active": True,
                },
            )

        posts_data = [
            ("Bộ sưu tập Burgundy Muse ra mắt", "Sắc đỏ đô chủ đạo được làm mới bằng lụa, nhung và những đường cắt hiện đại."),
            ("5 cách phối satin trắng cho ngày hè", "Gợi ý phối satin với burgundy, denim sáng màu và phụ kiện ánh vàng nhẹ."),
            ("Dịch vụ tư vấn phong cách cá nhân", "Stylist của L.T.N giúp bạn hoàn thiện tủ đồ theo lịch làm việc và sự kiện."),
        ]
        for title, summary in posts_data:
            BlogPost.objects.update_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "summary": summary,
                    "content": summary + "\n\nNội dung được biên tập cho trải nghiệm mua sắm L.T.N Clothing.",
                    "thumbnail": copied.get("tiec-5", ""),
                    "is_published": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Đã tạo dữ liệu mẫu L.T.N Clothing."))
