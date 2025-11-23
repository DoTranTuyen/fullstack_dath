import os
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from web_01.models import Category


class Command(BaseCommand):
    help = 'Import danh mục sản phẩm từ file Excel'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, "data/categories.xlsx")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ Không tìm thấy file: {file_path}"))
            return

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Lỗi khi đọc file Excel: {e}"))
            return

        for index, row in df.iterrows():
            try:
                category_name = row["name"].strip()
                if category_name:
                    category, created = Category.objects.get_or_create(name=category_name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ Đã thêm danh mục: {category_name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Danh mục '{category_name}' đã tồn tại."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi khi xử lý dòng {index + 1}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Hoàn thành việc import danh mục!"))
