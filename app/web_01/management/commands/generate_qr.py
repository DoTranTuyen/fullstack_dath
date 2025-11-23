from django.core.management.base import BaseCommand
from web_01.models import Table  # 🔄 Đường dẫn đến model Table
from cloudinary.uploader import upload
import qrcode
from io import BytesIO


class Command(BaseCommand):
    help = 'Tạo và upload mã QR cho các bàn'

    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            type=int,
            help='ID của bàn cần tạo mã QR. Nếu không chỉ định sẽ tạo cho tất cả bàn.'
        )

    def handle(self, *args, **options):
        # Tạo các bàn từ 1 -> 20 nếu chưa có
        for i in range(1, 21):
            table, created = Table.objects.get_or_create(
                table_number=i,
                defaults={'status': 'available'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Đã tạo bàn {i}"))
