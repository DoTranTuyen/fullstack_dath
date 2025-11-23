import os
import pandas as pd
import requests
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from web_01.models import Product, Category, Ingredient, IngredientProduct


class Command(BaseCommand):
    help = "Import sản phẩm từ file Excel"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, "data/products.xlsx")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ Không tìm thấy file: {file_path}"))
            return

        try:
            df = pd.read_excel(file_path).fillna("")  # 🔹 Thay NaN bằng chuỗi rỗng
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Lỗi khi đọc file Excel: {e}"))
            return

        for index, row in df.iterrows():
            try:
                # ✅ Đảm bảo các giá trị là chuỗi trước khi gọi .strip()
                product_name = str(row.get("name", "")).strip()
                description = str(row.get("description", "")).strip()
                price = row.get("price", 0)
                image_url = str(row.get("image", "")).strip()
                category_name = str(row.get("category", "")).strip()
                ingredients_data = str(row.get("ingredients", "")).strip()  # Tên nguyên liệu, cách nhau bằng dấu phẩy

                if not product_name:
                    self.stdout.write(self.style.WARNING(f"⚠️ Bỏ qua dòng {index + 1}: Không có tên sản phẩm"))
                    continue

                # ✅ Xử lý danh mục
                category = None
                if category_name:
                    category, _ = Category.objects.get_or_create(name=category_name)

                # ✅ Kiểm tra sản phẩm đã tồn tại chưa
                product, created = Product.objects.get_or_create(
                    name=product_name,
                    defaults={"description": description, "price": price, "category": category},
                )

                # ✅ Cập nhật sản phẩm nếu đã tồn tại
                updated_fields = []
                if not created:
                    if category and product.category != category:
                        product.category = category
                        updated_fields.append("category")

                    if description and product.description != description:
                        product.description = description
                        updated_fields.append("description")

                    if price and product.price != price:
                        product.price = price
                        updated_fields.append("price")

                # ✅ Xử lý ảnh sản phẩm (chỉ tải nếu có URL hợp lệ)
                if image_url.startswith("http"):
                    try:
                        response = requests.get(image_url, timeout=5)
                        if response.status_code == 200:
                            uploaded_image = cloudinary.uploader.upload(ContentFile(response.content))
                            new_image_url = uploaded_image.get("secure_url")

                            if new_image_url and new_image_url != product.image:
                                product.image = new_image_url
                                updated_fields.append("image")
                        else:
                            self.stdout.write(self.style.WARNING(f"⚠️ Không thể tải ảnh từ {image_url}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Lỗi khi tải ảnh: {e}"))

                # ✅ Lưu cập nhật nếu có thay đổi
                if updated_fields:
                    product.save(update_fields=updated_fields)
                    self.stdout.write(self.style.WARNING(f"⚠️ Đã cập nhật sản phẩm '{product_name}' ({', '.join(updated_fields)})"))
                elif created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Đã thêm sản phẩm: {product_name}"))

                # ✅ Xử lý nguyên liệu
                IngredientProduct.objects.filter(product=product).delete()
                if ingredients_data:
                    for ingredient in ingredients_data.split(","):
                        ingredient_name, ingredient_quantity_required = ingredient.strip().split(":")
                        if not ingredient_name or not ingredient_quantity_required:
                            continue
                        try:
                            ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
                            IngredientProduct.objects.create(product=product, ingredient=ingredient, quantity_required=ingredient_quantity_required)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"❌ Lỗi thêm nguyên liệu '{ingredient_name}' cho {product_name}: {e}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi khi xử lý dòng {index + 1}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Hoàn thành việc import sản phẩm!"))
