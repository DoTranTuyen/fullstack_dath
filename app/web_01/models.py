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
    created_at = models.DateTimeField(verbose_name='created_at', null=True, auto_now_add=True)

    # Trường kiểu DateTimeField, tự động cập nhật thời gian khi instance được lưu.
    # Tham số null=True cho phép trường này nhận giá trị NULL trong cơ sở dữ liệu.
    updated_at = models.DateTimeField(verbose_name='updated_at', null=True, auto_now=True)

    # Trường kiểu BooleanField để biểu diễn trạng thái xóa (soft delete) của instance.
    # Mặc định không xóa (False).
    is_deleted = models.BooleanField(verbose_name='is_deleted', default=False)

    class Meta:
        # Khai báo class này là một abstract base class.
        # Các trường của nó sẽ được thêm vào các model kế thừa từ class này,
        # nhưng chính nó sẽ không tạo một bảng riêng trong cơ sở dữ liệu.
        abstract = True

    @cached_property
    def formatted_created_at(self) -> str:
        return self.created_at.strftime('%d/%m/%Y')  # Định dạng ngày/tháng/năm


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=STATUS_ACTIVE_CHOICES, default='active')

# 🔄 Model Product (Sản phẩm)
    class Meta:
        # Khai báo class này là một abstract base class.
        # Các trường của nó sẽ được thêm vào các model kế thừa từ class này,
        # nhưng chính nó sẽ không tạo một bảng riêng trong cơ sở dữ liệu.
        db_table = 'category'

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

    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES)
    quantity_in_stock = models.IntegerField(default=0)  # 🔄 Số lượng tồn kho

    class Meta:
        db_table = 'ingredient'

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

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    change = models.IntegerField()  # (+ nhập, - xuất)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    note = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    stock_before = models.IntegerField(null=True, blank=True)  # 🆕 thêm
    stock_after = models.IntegerField(null=True, blank=True)   # đã có
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'inventory_log'
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
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientProduct', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_ACTIVE_CHOICES, default='active')

    class Meta:
        db_table = 'product'
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.IntegerField()

    class Meta:
        db_table = 'ingredient_product'


class Customer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    loyalty_points = models.IntegerField()

# 🔄 Model Employee
    class Meta:
        db_table = 'customer'


class Employee(BaseModel):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('chef', 'Chef'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    salary = models.IntegerField()
    avartar_url = CloudinaryField('avartar_url', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')

    class Meta:
        db_table = 'employee'


class WorkShift(BaseModel):
    SHIFT_TYPE_CHOICES = [
        ('morning', 'Sáng'),
        ('afternoon', 'Chiều'),
        ('evening', 'Tối'),
        ('allday', 'Cả Ngày')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="workshifts")
    date = models.DateField()
    shift_type = models.CharField(max_length=10, choices=SHIFT_TYPE_CHOICES)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'work_shift'
        unique_together = ('employee', 'date', 'shift_type')

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.shift_type}"


class ShiftRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="shift_registrations")
    date = models.DateField()
    shift_type = models.CharField(max_length=10, choices=WorkShift.SHIFT_TYPE_CHOICES)
    is_off = models.BooleanField(default=False)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shift_registration'
        unique_together = ('employee', 'date', 'shift_type')

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.shift_type} - {'Nghỉ' if self.is_off else 'Làm việc'}"



# 🔄 Model Table


class Table(models.Model):
    table_number = models.IntegerField(unique=True)
    status = models.CharField(max_length=10, choices=[('available', 'Trống'), ('occupied', 'Sử dụng'), ('reserved', 'Đã đặt')], default='available')
    qr_image = CloudinaryField('image')
    capacity = models.IntegerField(default=4)  # Thêm trường capacity
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'table'
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

        # Lưu lại model bình thường
        super().save(*args, **kwargs)


class Session(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} - {self.customer} - {self.table} ({self.status})"

    class Meta:
        db_table = 'session'

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
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=15, choices=[('cash', 'Tiền mặt'), ('bank_transfer', 'Chuyển khoản'), ('momo', 'Momo')], null=True, blank=True)
    total_amount = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)

    class Meta:
        db_table = 'invoice'
# 🔄 Model Order

    @cached_property
    def formatted_total_amount(self) -> str:
        return f'{self.total_amount:,}đ'.replace(',', '.')


class Order(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Chờ'),
        ('in_progress', 'Đang làm'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy')
    ], default='pending')
    total = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)

    class Meta:
        db_table = 'order'

    @cached_property
    def formatted_price(self) -> str:
        return f'{self.total:,}đ'.replace(',', '.')


class OrderDetail(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()  # Giá của từng sản phẩm
    total = models.IntegerField()  # Tổng tiền của từng dòng sản phẩm (quantity * price)
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Chờ'),
        ('in_progress', 'Đang làm'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy')
    ], default='pending')  # Trạng thái của từng món

    class Meta:
        db_table = 'order_detail'

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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'cart_item'

# 🔄 Model Notification


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(
        max_length=50
    )
    status = models.CharField(
        max_length=10,
        choices=[('read', 'Read'), ('unread', 'Unread')],
        default='unread'
    )
    is_read = models.BooleanField(default=False)
    data = models.JSONField(blank=True, null=True)  # 👈 Thêm JSON field

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} | {self.message[:30]}"

# ✅ Models hoàn tất!


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'comment'


class Rating(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], null=True, blank=True)

    class Meta:
        db_table = 'rating'


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sold_quantity = models.IntegerField()
    report_date = models.DateTimeField()

    class Meta:

        db_table = 'best_selling_product'


class TableReservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Đã hoàn thành'),
    ]

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    many_person = models.IntegerField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True)

    date = models.DateField(null=False)  # Ngày đặt bàn
    hour = models.TimeField(null=False)  # Giờ đặt bàn

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Bàn {self.table.table_number} ({self.date} {self.hour})"

    class Meta:
        db_table = 'table_reservation'


class ChatHistory(models.Model):
    user_message = models.TextField()  # Tin nhắn người dùng
    bot_reply = models.TextField()  # Phản hồi của chatbot
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian gửi tin nhắn

    def __str__(self):
        return f"User: {self.user_message[:20]}... | Bot: {self.bot_reply[:20]}..."

    class Meta:
        db_table = 'chat_history'
