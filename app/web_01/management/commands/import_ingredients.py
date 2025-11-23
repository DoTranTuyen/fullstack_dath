import os
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from web_01.models import Ingredient, InventoryLog


class Command(BaseCommand):
    help = 'Import nguyên liệu từ file Excel'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, "data/ingredients.xlsx")

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
                ingredient_id = int(row["id"])
                ingredient_name = row["name"].strip()
                unit = row["unit"].strip()

                if ingredient_name and unit:
                    ingredient, created = Ingredient.objects.get_or_create(
                        id=ingredient_id,
                        defaults={'name': ingredient_name, 'unit': unit}
                    )
                    # ingredient.quantity_in_stock = 100
                    # ingredient.save()

                    log = InventoryLog(
                        ingredient=ingredient,
                        change=100,
                        type='import',
                        note='',
                        user_id=1  # thêm dòng này
                    )
                    log.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ Đã thêm nguyên liệu: {ingredient_name} ({unit})"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Nguyên liệu '{ingredient_name}' đã tồn tại."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi khi xử lý dòng {index + 1}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Hoàn thành việc import nguyên liệu!"))
