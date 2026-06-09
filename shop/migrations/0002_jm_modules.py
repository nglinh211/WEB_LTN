from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="icon",
            field=models.ImageField(blank=True, null=True, upload_to="categories/icons/"),
        ),
        migrations.AddField(
            model_name="category",
            name="sort_order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["sort_order", "name"], "verbose_name_plural": "Categories"},
        ),
        migrations.AddField(
            model_name="product",
            name="is_new",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="is_sale",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="Banner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("subtitle", models.CharField(blank=True, max_length=220)),
                ("image", models.ImageField(blank=True, null=True, upload_to="banners/")),
                ("button_text", models.CharField(blank=True, max_length=80)),
                ("button_url", models.CharField(blank=True, max_length=220)),
                ("position", models.CharField(choices=[("hero", "Hero"), ("grid", "Grid"), ("footer", "Footer")], default="grid", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order", "id"]},
        ),
        migrations.CreateModel(
            name="Collection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(allow_unicode=True, blank=True, max_length=210, unique=True)),
                ("subtitle", models.CharField(blank=True, max_length=220)),
                ("banner_image", models.ImageField(blank=True, null=True, upload_to="collections/")),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Wishlist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wishlisted_by", to="shop.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wishlist_items", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user", "product")}},
        ),
    ]
