from datetime import datetime, timedelta
from django.db.models import Sum,Count
from web_01.models import Order,OrderDetail,Invoice
import re
from calendar import monthrange
# Helper function to parse dates

TODAY = 'hôm nay'
YESTERDAY = 'hôm qua'


def parse_date(reference_date):
    if reference_date == YESTERDAY:
        return datetime.now().date() - timedelta(days=1)
    elif reference_date == TODAY:
        return datetime.now().date()
    elif "tháng này" in reference_date:
        return datetime.now().replace(day=1)  # Ngày đầu tháng này
    elif "tháng trước" in reference_date:
        first_day_last_month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
        return first_day_last_month
    return None

# Function to analyze the message


def analyze_message(message):
    message = message.lower()
    response = {
        'intent': None,
        'date': None,
        'product': None,
        'status': None,
    }

    # Xác định ý định và ngày
    if "doanh thu" in message:
        if YESTERDAY in message:
            response['intent'] = "get_revenue"
            response['date'] = YESTERDAY
        elif TODAY in message:
            response['intent'] = "get_revenue"
            response['date'] = TODAY

    if "số đơn" in message:
        if TODAY in message:
            response['intent'] = "count_orders"
            response['date'] = TODAY
        elif YESTERDAY in message:
            response['intent'] = "count_orders"
            response['date'] = YESTERDAY

    # Xử lý trạng thái món ăn
    if "món" in message:
        if "đang làm" in message:
            response['intent'] = "get_product_status"
            response['status'] = "in_progress"
        elif "hoàn thành" in message:
            response['intent'] = "get_product_status"
            response['status'] = "completed"
        elif "hủy" in message:
            response['intent'] = "get_product_status"
            response['status'] = "cancelled"

        # Xử lý yêu cầu sản phẩm bán chạy nhất trong một tháng
    match = re.search(r'sản phẩm bán chạy tháng (\d{1,2})|sản phẩm bán chạy tháng này|sản phẩm bán chạy tháng trước', message)
    if match:
        if match.group(1):
            response['intent'] = "get_top_selling_products"
            response['date'] = int(match.group(1))  # Lấy tháng từ regex
        elif 'tháng này' in message:
            response['intent'] = "get_top_selling_products"
            response['date'] = datetime.now().month  # Tháng hiện tại
        elif 'tháng trước' in message:
            response['intent'] = "get_top_selling_products"
            response['date'] = (datetime.now().month - 1) % 12 or 12  # Tháng trước
        
        
    # Xử lý thông tin sản phẩm
    if "món ăn" in message:
        product_name = message.split("món ăn")[-1].strip()
        response['product'] = product_name

    if not response['intent']:
        return None

    return response

# Function to handle the intent


def handle_intent(intent_data):
    if intent_data["intent"] == "get_revenue":
        target_date = parse_date(intent_data["date"])
        if target_date:
            revenue = Invoice.objects.filter(created_at__date=target_date).aggregate(total=Sum('total_amount'))['total'] or 0
            return f"Doanh thu ngày {target_date.strftime('%d/%m/%Y')} là {revenue:,} VNĐ."

    if intent_data["intent"] == "count_orders":
        target_date = parse_date(intent_data["date"])
        if target_date:
            order_count = Order.objects.filter(created_at__date=target_date).count()
            return f"Số đơn hàng {intent_data['date']} ({target_date.strftime('%d/%m/%Y')}) là {order_count} đơn."

    if intent_data["intent"] == "get_product_status" and intent_data["status"]:
        # Process product status (in_progress, completed, cancelled)
        product_name = intent_data.get("product", "Món ăn không xác định")
        status = intent_data["status"]
        # You could add more business logic to fetch product status from database here.
        return f"Trạng thái món '{product_name}' là: {status.capitalize()}."

    
    if intent_data["intent"] == "get_top_selling_products":
        month = int(intent_data["date"])  # Tháng từ 1-12
        top_products = get_top_selling_products(month)  # Lấy sản phẩm bán chạy theo tháng
        top_product_list = "\n".join([f"Sản phẩm: {product['product']}, Số lượng bán: {product['sales_count']}" for product in top_products])
        return f"Sản phẩm bán chạy nhất trong tháng {month}:\n{top_product_list}"
    
    return "Xin lỗi, tôi chưa hỗ trợ yêu cầu này."

def get_top_selling_products(month):
    # Lấy số ngày trong tháng hiện tại
    year = datetime.now().year
    _, last_day = monthrange(year, month)
    
    # Lấy ra ngày bắt đầu và kết thúc của tháng
    start_date = datetime(year=year, month=month, day=1)
    end_date = datetime(year=year, month=month, day=last_day, hour=23, minute=59, second=59)  # Ngày cuối tháng
    
    # Lấy ra các sản phẩm bán chạy nhất trong tháng
    top_products = OrderDetail.objects.filter(created_at__date__range=[start_date, end_date]) \
                                      .values('product__name') \
                                      .annotate(sales_count=Count('product')) \
                                      .order_by('-sales_count') \
                                      .values('product__name', 'sales_count')[:10]  # Lấy 10 sản phẩm bán chạy nhất
    
    return top_products