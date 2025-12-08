# 📌 Django Models cho hệ thống Quản lý Nhà hàng (Cập nhật)

from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.functional import cached_property
# 🔄 Model Category (Loại sản phẩm)
from cloudinary.uploader import upload
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from web_01.utils.model_consts import STATUS_ACTIVE_CHOICES
from datetime import datetime


class BaseModel(models.Model):
    # Trường kiểu DateTimeField, tự động thêm thời gian tạo khi tạo instance mới.
    # Tham số null=True cho phép trường này nhận giá trị NULL trong cơ sở dữ liệu.
    created_at = models.DateTimeField(verbose_name='created_at', null=True, auto_now_add=True, db_column="ngay_tao")

    # Trường kiểu DateTimeField, tự động cập nhật thời gian khi instance được lưu.
    # Tham số null=True cho phép trường này nhận giá trị NULL trong cơ sở dữ liệu.
    updated_at = models.DateTimeField(verbose_name='updated_at', null=True, auto_now=True, db_column="ngay_cap_nhat")

    # Trường kiểu BooleanField để biểu diễn trạng thái xóa (soft delete) của instance.
    # Mặc định không xóa (False).
    is_deleted = models.BooleanField(verbose_name='is_deleted', default=False, db_column="da_xoa")

    class Meta:
        # Khai báo class này là một abstract base class.
        # Các trường của nó sẽ được thêm vào các model kế thừa từ class này,
        # nhưng chính nó sẽ không tạo một bảng riêng trong cơ sở dữ liệu.
        abstract = True

    @cached_property
    def formatted_created_at(self) -> str:
        return self.created_at.strftime('%d/%m/%Y')  # Định dạng ngày/tháng/năm


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_column="ten_loai_san_pham")
    description = models.TextField(null=True, blank=True, db_column="mo_ta")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column="cha_loai_san_pham")
    status = models.CharField(max_length=10, choices=STATUS_ACTIVE_CHOICES, default='active', db_column="trang_thai")

# 🔄 Model Product (Sản phẩm)
    class Meta:
        # Khai báo class này là một abstract base class.
        # Các trường của nó sẽ được thêm vào các model kế thừa từ class này,
        # nhưng chính nó sẽ không tạo một bảng riêng trong cơ sở dữ liệu.
        db_table = 'loai_san_pham'

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kg'),
        ('g', 'Gram'),
        ('ml', 'Milliliter'),
        ('chai', 'Chai'),
        ('gói', 'Gói'),
        ('hộp', 'Hộp'),
        ('lon', 'Lon'),
        ('cai', 'Cái'),
        ('lang', 'Lạng'),
        ('trai', 'Trái'),
        ('hop', 'Hộp'),
        ('o', 'Ổ'),
        ('cu', 'Củ'),
        ('lit', 'Lít'),
        ('ml', 'Ml'),
        ('chai', 'Chai'),
        ('quả', 'Quả'),
    ]

    name = models.CharField(max_length=100, unique=True, db_column="ten_nguyen_lieu")
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, db_column="don_vi_tinh")
    quantity_in_stock = models.IntegerField(default=0, db_column="so_luong_ton")  # 🔄 Số lượng tồn kho

    class Meta:
        db_table = 'nguyenlieu'

    def __str__(self) -> str:
        return f'{self.name}'

    def update_stock(self):
        """Cập nhật số lượng tồn kho từ InventoryLog."""
        total = self.inventorylog_set.aggregate(total=models.Sum('change'))['total']
        self.quantity_in_stock = total if total else 0
        self.save()

# 🔄 Lịch sử nhập xuất kho


class InventoryLog(models.Model):
    TYPE_CHOICES = [
        ('import', 'Nhập kho'),
        ('export', 'Xuất kho'),
        ('sell', 'Bán hàng'),
        ('adjustment', 'Điều chỉnh'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ma_nguyen_lieu")
    change = models.IntegerField(db_column="so_luong_thay_doi")  # (+ nhập, - xuất)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, db_column="loai_thay_doi")
    note = models.TextField(null=True, blank=True, db_column="ghi_chu")
    last_updated = models.DateTimeField(auto_now_add=True, db_column="thoi_gian_cap_nhat")
    stock_before = models.IntegerField(null=True, blank=True, db_column="so_luong_truoc")  # 🆕 thêm
    stock_after = models.IntegerField(null=True, blank=True, db_column="so_luong_sau")   # đã có
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column="ma_nguoi_dung")

    class Meta:
        db_table = 'phieunhap_xuat'
        ordering = ['-last_updated']

    def save(self, *args, **kwargs):
        if not self.stock_before:
            self.stock_before = self.ingredient.quantity_in_stock
        super().save(*args, **kwargs)
        self.ingredient.update_stock()
        self.stock_after = self.ingredient.quantity_in_stock
        InventoryLog.objects.filter(pk=self.pk).update(stock_after=self.stock_after)


# 🔄 Sản phẩm


class Product(BaseModel):
    name = models.CharField(max_length=100, db_column="ten_san_pham")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column="ma_loai_san_pham")
    price = models.IntegerField(db_column="gia")
    description = models.TextField(null=True, blank=True, db_column="mo_ta")
    image = CloudinaryField('image', null=True, blank=True, db_column="hinh_anh")
    ingredients = models.ManyToManyField(Ingredient, through='IngredientProduct', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_ACTIVE_CHOICES, default='active', db_column="trang_thai")

    class Meta:
        db_table = 'sanpham'
        ordering = ['-created_at']

    @cached_property
    def in_stock(self):
        """
        Tính số lượng sản phẩm có thể làm được dựa vào nguyên liệu tồn kho.
        Nếu không đủ nguyên liệu để làm ít nhất 1 sản phẩm, trả về 0.
        """
        ingredient_products = self.ingredientproduct_set.all()
        stock_counts = []

        for item in ingredient_products:
            if item.quantity_required == 0:  # Tránh lỗi chia cho 0
                continue

            available_count = item.ingredient.quantity_in_stock // item.quantity_required
            stock_counts.append(available_count)

        return min(stock_counts) if stock_counts else 0  # Trả về số lượng nhỏ nhất có thể làm được


class IngredientProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ma_san_pham")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ma_nguyen_lieu")
    quantity_required = models.IntegerField(db_column="so_luong_can")

    class Meta:
        db_table = 'congthuc_sanpham'


class Customer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, db_column="ma_nguoi_dung")
    loyalty_points = models.IntegerField(db_column="diem_tich_luy")

# 🔄 Model Employee
    class Meta:
        db_table = 'khachhang'


class Employee(BaseModel):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('chef', 'Chef'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column="ma_nguoi_dung")
    salary = models.IntegerField(db_column="luong")
    avartar_url = CloudinaryField('avartar_url', null=True, blank=True, db_column="anh_dai_dien")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff', db_column="vai_tro")

    class Meta:
        db_table = 'nhanvien'


class WorkShift(BaseModel):
    SHIFT_TYPE_CHOICES = [
        ('morning', 'Sáng'),
        ('afternoon', 'Chiều'),
        ('evening', 'Tối'),
        ('allday', 'Cả Ngày')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="workshifts", db_column="ma_nhan_vien")
    date = models.DateField(db_column="ngay")
    shift_type = models.CharField(max_length=10, choices=SHIFT_TYPE_CHOICES, db_column="loai_ca")
    time_start = models.DateTimeField(blank=True, null=True, db_column="thoi_gian_bat_dau")
    time_end = models.DateTimeField(blank=True, null=True, db_column="thoi_gian_ket_thuc")
    notes = models.TextField(blank=True, null=True, db_column="ghi_chu")

    class Meta:
        db_table = 'phancong_ca'
        unique_together = ('employee', 'date', 'shift_type')

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.shift_type}"


class ShiftRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="shift_registrations", db_column="ma_nhan_vien")
    date = models.DateField(db_column="ngay_dang_ky")
    shift_type = models.CharField(max_length=10, choices=WorkShift.SHIFT_TYPE_CHOICES, db_column="loai_ca")
    is_off = models.BooleanField(default=False, db_column="xin_nghi")
    reason = models.TextField(blank=True, null=True, db_column="ly_do")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_column="trang_thai")
    created_at = models.DateTimeField(auto_now_add=True, db_column="ngay_tao")

    class Meta:
        db_table = 'dangky_ca'
        unique_together = ('employee', 'date', 'shift_type')

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.shift_type} - {'Nghỉ' if self.is_off else 'Làm việc'}"


# 🔄 Model Table


class Table(models.Model):
    table_number = models.IntegerField(unique=True, db_column="so_ban", null=True)
    status = models.CharField(max_length=10, choices=[('available', 'Trống'), ('occupied', 'Sử dụng'), ('reserved', 'Đã đặt')], default='available', db_column="trang_thai")
    qr_image = CloudinaryField('image', db_column="anh_qr")
    capacity = models.IntegerField(default=4, db_column="suc_chua")  # Thêm trường capacity
    is_deleted = models.BooleanField(default=False, db_column="da_xoa")

    class Meta:
        db_table = 'ban_an'
    # 🔄 Model Ingredient
    # 🔄 Override phương thức save()

    def __str__(self):
        return f"Bàn {self.table_number}"

    def save(self, *args, **kwargs):
        force_update_qr = kwargs.pop('force_update_qr', False)

        # Tạo URL dựa trên table_number
        url = f"{settings.FRONT_END_URL}/login-menu/?table_number={self.table_number}"

        # Tạo mã QR
        qr = qrcode.make(url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)

        # Upload ảnh QR nếu chưa có hoặc được yêu cầu cập nhật
        if not self.qr_image or force_update_qr:
            result = upload(qr_bytes, public_id=f"table_{self.table_number}_qr", overwrite=True)
            self.qr_image = result['url']

        if not self.table_number:
            last = Table.objects.order_by('-table_number').first()
            self.table_number = 1 if not last else last.table_number + 1
        # Lưu lại model bình thường
        super().save(*args, **kwargs)


class Session(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column="ma_khach_hang")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, db_column="ma_ban")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', db_column="trang_thai")
    started_at = models.DateTimeField(auto_now_add=True, db_column="thoi_gian_bat_dau")
    ended_at = models.DateTimeField(null=True, blank=True, db_column="thoi_gian_ket_thuc")

    def __str__(self):
        return f"Session {self.id} - {self.customer} - {self.table} ({self.status})"

    class Meta:
        db_table = 'phienphucvu'

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Session.objects.get(pk=self.pk).status
            if old_status == 'active' and self.status == 'closed':
                # Lấy tất cả các hóa đơn thuộc session
                invoices = Invoice.objects.filter(session=self)
                for invoice in invoices:
                    orders = invoice.order_set.exclude(status='cancelled')
                    # Cập nhật status Order
                    orders.update(status='completed')

                    # Cập nhật status OrderDetail tương ứng
                    for order in orders:
                        order.orderdetail_set.exclude(status='cancelled').update(status='completed')

        if self.status == 'closed' and not self.ended_at:
            self.ended_at = datetime.now()

        super().save(*args, **kwargs)


class Invoice(BaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, db_column="ma_phien_phuc_vu")
    payment_method = models.CharField(max_length=15, choices=[('cash', 'Tiền mặt'), ('bank_transfer', 'Chuyển khoản'),
                                      ('momo', 'Momo')], null=True, blank=True, db_column="phuong_thuc_thanh_toan")
    total_amount = models.IntegerField(default=0, db_column="tong_tien")
    discount = models.IntegerField(default=0, db_column="giam_gia")

    class Meta:
        db_table = 'hoadon'
# 🔄 Model Order

    @cached_property
    def formatted_total_amount(self) -> str:
        return f'{self.total_amount:,}đ'.replace(',', '.')


class Order(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, db_column="ma_hoa_don")
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Chờ'),
        ('in_progress', 'Đang làm'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy')
    ], default='pending', db_column="trang_thai")
    total = models.IntegerField(default=0, db_column="tong_tien")
    discount = models.IntegerField(default=0, db_column="giam_gia")

    class Meta:
        db_table = 'donhang'

    @cached_property
    def formatted_price(self) -> str:
        return f'{self.total:,}đ'.replace(',', '.')


class OrderDetail(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column="ma_don_hang")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ma_san_pham")
    quantity = models.IntegerField(db_column="so_luong")
    price = models.IntegerField(db_column="gia")  # Giá của từng sản phẩm
    total = models.IntegerField(db_column="thanh_tien")  # Tổng tiền của từng dòng sản phẩm (quantity * price)
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Chờ'),
        ('in_progress', 'Đang làm'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy')
    ], default='pending', db_column="trang_thai")  # Trạng thái của từng món

    class Meta:
        db_table = 'donhang_chitiet'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        prev_status = None
        if not is_new:
            prev = OrderDetail.objects.get(pk=self.pk)
            prev_status = prev.status

        super().save(*args, **kwargs)

        # Nếu chuyển sang "completed" mà trước đó không phải completed
        if self.status == 'completed' and prev_status != 'completed':
            self.export_ingredients()

    def export_ingredients(self):
        product_ingredient = IngredientProduct.objects.filter(product=self.product).first()
        total_quantity_used = product_ingredient.quantity_required * self.quantity
        ingredient = product_ingredient.ingredient
        old_stock = ingredient.quantity_in_stock
        ingredient.quantity_in_stock -= total_quantity_used
        ingredient.save()
        # Tạo log
        InventoryLog.objects.create(
            ingredient=ingredient,
            change=-total_quantity_used,
            type='export',
            note=f"Đơn hàng (#00{self.order.id}) - ({self.product.name} x {total_quantity_used})",
            stock_before=old_stock,
            stock_after=ingredient.quantity_in_stock,
            user=self.updated_by if hasattr(self, 'updated_by') else None
        )


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column="ma_khach_hang")

    class Meta:
        db_table = 'giohang'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, db_column="ma_gio_hang")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ma_san_pham")
    quantity = models.IntegerField(default=1, db_column="so_luong")

    class Meta:
        db_table = 'giohang_chitiet'

# 🔄 Model Notification


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="ma_nguoi_dung")
    message = models.TextField(db_column="noi_dung")
    type = models.CharField(
        max_length=50,
        db_column="loai_thong_bao"
    )
    status = models.CharField(
        max_length=10,
        choices=[('read', 'Read'), ('unread', 'Unread')],
        default='unread',
        db_column="trang_thai"
    )
    is_read = models.BooleanField(default=False,
                                  db_column="da_doc")
    data = models.JSONField(blank=True, null=True, db_column="du_lieu_json")  # 👈 Thêm JSON field

    class Meta:
        db_table = 'thong_bao'  # Đổi tên bảng
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} | {self.message[:30]}"

# ✅ Models hoàn tất!


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="ma_nguoi_dung")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ma_san_pham")
    content = models.TextField(null=True, blank=True, db_column="noi_dung")

    class Meta:
        db_table = 'binhluan'


class Rating(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="ma_nguoi_dung")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ma_san_pham")
    score = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], null=True, blank=True, db_column="diem_so")

    class Meta:
        db_table = 'danhgia'


class BestSellingProduct(models.Model):
    """
    🔍 Các trường:
        product (ForeignKey):
            Liên kết đến bảng Product.
            Xác định sản phẩm cụ thể.
        sold_quantity (IntegerField):

        Số lượng sản phẩm đã bán.
            report_date (DateField):

        Ngày tạo báo cáo (có thể là ngày, tuần, tháng hoặc năm).

    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ma_san_pham")
    sold_quantity = models.IntegerField(db_column="so_luong_da_ban")
    report_date = models.DateTimeField(db_column="ngay_bao_cao")

    class Meta:

        db_table = 'sanpham_banchay'


class TableReservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Đã hoàn thành'),
    ]

    name = models.CharField(max_length=100, db_column="ten_khach_hang")
    phone_number = models.CharField(max_length=15, db_column="so_dien_thoai")
    many_person = models.IntegerField(db_column="so_nguoi")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True, db_column="ma_ban")

    date = models.DateField(null=False, db_column="ngay_dat")  # Ngày đặt bàn
    hour = models.TimeField(null=False, db_column="gio_dat")  # Giờ đặt bàn

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_column="trang_thai")
    created_at = models.DateTimeField(auto_now_add=True, db_column="ngay_tao")

    def __str__(self):
        return f"{self.name} - Bàn {self.table.table_number} ({self.date} {self.hour})"

    class Meta:
        db_table = 'datban'


class ChatHistory(models.Model):
    user_message = models.TextField(db_column="tin_nhan_nguoi_dung")  # Tin nhắn người dùng
    bot_reply = models.TextField(db_column="tin_nhan_bot")  # Phản hồi của chatbot
    created_at = models.DateTimeField(auto_now_add=True, db_column="thoi_gian_tao")  # Thời gian gửi tin nhắn

    def __str__(self):
        return f"User: {self.user_message[:20]}... | Bot: {self.bot_reply[:20]}..."

    class Meta:
        db_table = 'lichsu_tinnhan'
