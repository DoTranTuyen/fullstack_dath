from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from web_01.models import Employee
import requests
from cloudinary.uploader import upload

TAI_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

AN_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

HOANG_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

PHU_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

ANH_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

ADMIN_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

def upload_avatar_and_update_employee(user, avatar_url):
    # Bước 1: Download ảnh từ avatar_url cũ
    response = requests.get(ADMIN_AVATAR_URL)
    if response.status_code == 200:
        image_bytes = response.content
        
        # Bước 2: Upload lên Cloudinary
        result = upload(image_bytes, public_id=f"user_avatar_{user.username}")
        cloudinary_url = result['url']
        
        defaults = defaults={
                'salary': 10000000,
                'avartar_url': cloudinary_url,
            }
        if user.username == 'chef':
            defaults['role'] = 'chef'
            
        if user.username == 'manager':
            defaults['role'] = 'manager'
        # Bước 3: Tạo hoặc update Employee
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults=defaults
        )
        
        if not created:
            employee.avartar_url = cloudinary_url
            employee.save()
        
        print(f"✅ Avatar uploaded and updated for {user.username}")
    else:
        print(f"❌ Failed to download avatar from {avatar_url}")

class Command(BaseCommand):
    help = "Tạo tài khoản admin và member mặc định + thêm Employee"

    ADMIN_ACCOUNTS = [
        ("viettai", "123456", 'Viết', 'Tài', TAI_AVATAR_URL),
        ("an", "123456", 'Trường', 'Ân', AN_AVATAR_URL),
        ("hoang", "123456", 'Quốc', 'Hoàng', HOANG_AVATAR_URL),
        ("phu", "123456", 'Châu', 'Phú', PHU_AVATAR_URL),
        ("anh", "123456", 'Công', 'Anh', ANH_AVATAR_URL),
        ("admin", "123456", '', 'Admin', ADMIN_AVATAR_URL),
        ("manager", "123456", 'manager', 'Manager', ADMIN_AVATAR_URL),
        ("chef", "123456", 'Chef', 'Chef', ADMIN_AVATAR_URL),
    ]

    def handle(self, *args, **kwargs):
        created_count = 0

        # Đảm bảo Group 'Member' tồn tại
        member_group, _ = Group.objects.get_or_create(name="Member")

        for username, password, last_name, first_name, avatar_url in self.ADMIN_ACCOUNTS:
            user = User.objects.filter(username=username).first()
            if not user:
                if username == "admin":
                    # Tạo superuser
                    user = User.objects.create_superuser(
                        username=username,
                        last_name=last_name,
                        first_name=first_name,
                        password=password,
                        email=f"{username}@rms.com"
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo superuser: {username}"))
                else:
                    # Tạo member
                    user = User.objects.create_user(
                        username=username,
                        last_name=last_name,
                        first_name=first_name,
                        password=password,
                        email=f"{username}@rms.com"
                    )
                    user.is_staff = True
                    user.save()
                    user.groups.add(member_group)

                    upload_avatar_and_update_employee(user, avatar_url)
                    
                    self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo member: {username}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Tài khoản '{username}' đã tồn tại."))

            

        self.stdout.write(self.style.SUCCESS(f"🎉 Đã xử lý xong {len(self.ADMIN_ACCOUNTS)} tài khoản!"))
