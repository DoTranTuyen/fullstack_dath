from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Khởi tạo dự án với các dữ liệu mẫu"

    def handle(self, *args, **kwargs):
        setup_commands = ["makemigrations", "migrate"]
        data_commands = ["create_admins", "import_categories", "generate_qr", "import_ingredients", 'import_products']

        # Chạy makemigrations và migrate trước
        for cmd in setup_commands:
            self.stdout.write(self.style.NOTICE(f"🚀 Đang chạy: {cmd}..."))
            try:
                call_command(cmd)
                self.stdout.write(self.style.SUCCESS(f"✅ Hoàn thành: {cmd}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi khi chạy {cmd}: {e}"))

        # Chạy các lệnh khởi tạo dữ liệu
        for cmd in data_commands:
            self.stdout.write(self.style.NOTICE(f"🚀 Đang chạy: {cmd}..."))
            try:
                call_command(cmd)
                self.stdout.write(self.style.SUCCESS(f"✅ Hoàn thành: {cmd}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi khi chạy {cmd}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Dự án đã được khởi tạo thành công!"))
