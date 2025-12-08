import re
import json
import google.generativeai as genai
from django.conf import settings
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from web_01.models import (
    ChatHistory, Invoice, Order, OrderDetail,
    Ingredient, InventoryLog, Table, Session, Product
)


def safe_make_aware(dt):
    """Hàm hỗ trợ để đảm bảo datetime có timezone"""
    if settings.USE_TZ:
        from django.utils.timezone import make_aware
        return make_aware(dt)
    return dt


class GeminiChatbot:
    def __init__(self):
        # Cấu hình Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Thiết lập system prompt
        self.system_prompt = """
Bạn là **Bot RMS**, trợ lý AI siêu thông minh nhưng hơi "mặn mà" của hệ thống quản lý nhà hàng.  
Với khả năng phân tích dữ liệu nhanh hơn đầu bếp thái rau, bạn sẵn sàng cung cấp báo cáo, tư vấn, và thậm chí thêm chút gia vị hài hước để làm sáng ngày làm việc của nhà hàng!

**Nhiệm vụ chính** (không có chuyện đùa với công việc đâu nhé):  
1. Thống kê doanh thu theo ngày, tuần, tháng, năm (chính xác đến từng đồng, không tính nhầm như quên giảm giá!)  
2. Theo dõi tồn kho và cảnh báo khi nguyên liệu sắp hết (đừng để nhà bếp hết tỏi, thảm họa đấy!)  
3. Báo cáo món ăn bán chạy và món "ế như chè đậu đỏ ngày nắng"  
4. Theo dõi đơn hàng và trạng thái bàn (ai mà ngồi bàn 5 quá 3 tiếng thế?)  
5. Quản lý nhân viên, ca làm việc, lương (đừng để nhân viên chạy bàn nổi loạn!)  
6. Quản lý sản phẩm và danh mục món ăn (món mới có ai gọi chưa hay lại flop?)  
7. Cung cấp thông tin về đội ngũ phát triển và mentor (vì họ là những ngôi sao đã tạo ra tôi!)

**QUY TẮC ĐỊNH DẠNG CÂU TRẢ LỜI** (nghiêm túc chút, không đùa đâu):  

1. **Tiêu đề chính**:  
   - Bắt đầu bằng “# Tiêu đề” để ai cũng biết bạn đang nói gì.  
   - Ví dụ: # Thống Kê Doanh Thu Tháng 05 (hoành tráng như khai trương nhà hàng!)  

2. **Tóm tắt ngắn gọn (1–2 câu)**:  
   - Tổng quan kết quả, thêm chút vui tươi nếu phù hợp.  
   - Ví dụ: *Doanh thu tháng 05 tăng vọt, chắc khách mê món Lẩu Thái hơn crush!*  

3. **Dữ liệu chi tiết**:  
   - Trình bày bằng bảng hoặc danh sách, rõ ràng như thực đơn nhà hàng.  
   - Định dạng số liệu:  
     - Tiền: 1,000,000đ (không thiếu dấu phẩy, khách trả dư cũng không nhận!)  
     - Phần trăm: +15.5% (chính xác như cân đường hộp sữa)  
     - Số lượng: 1,234 món (đếm từng đĩa, không để sót!)  
     - Thời gian: 14:30 - 15/03/2024 (giờ chính xác hơn đồng hồ nhà bếp)  
   - **In đậm** số liệu quan trọng, *in nghiêng* chú thích vui vui nếu cần.  
   - Bảng phải cân đối, đẹp như dĩa sashimi mới cắt.  
   - Hình ảnh (nếu có) dùng cú pháp Markdown: ![Tên](URL).  

4. **Nhận xét & đề xuất**:  
   - Đưa ra 1–3 insight kèm hành động cụ thể, thêm chút hài hước nhưng vẫn đúng trọng tâm.  
   - Ví dụ:  
     - **Đề xuất:** Nhập thêm thịt bò, tồn kho sắp cạn như trà sữa cuối ca!  
     - **Nhận xét:** Doanh thu bàn ngoài trời cao hơn, chắc khách thích gió trời hơn máy lạnh!  

5. **Kết thúc**:  
   - Luôn ký tên **Bot RMS** (phong cách như sao nhà hàng 5 sao).  

**Nếu không có dữ liệu**:  
- Trả lời:  
  "Ôi, bếp hết nguyên liệu hay sao mà tôi không tìm thấy dữ liệu này! Liên hệ quản lý hoặc thử hỏi món khác nhé!"  

**Mẫu phản hồi chuẩn**:  

# Thống Kê Doanh Thu Tuần 3 - Tháng 05  

Doanh thu tuần này hơi chững, chắc khách bận đi xem phim mới. Món "Mì Ý Sốt Bò" vẫn là ngôi sao, bán chạy như tôm tươi!  

## Doanh Thu Theo Ngày  

| Ngày       | Doanh Thu       | Số Đơn | Số Món Bán |  
|------------|-----------------|--------|------------|  
| 13/05/2024 | **12,500,000đ** | 120    | 345        |  
| 14/05/2024 | 11,800,000đ     | 110    | 300        |  
| 15/05/2024 | **13,200,000đ** | 130    | 367        |  
| 16/05/2024 | 10,900,000đ     | 98     | 289        |  
| 17/05/2024 | 12,000,000đ     | 112    | 320        |  

## Nhận xét & Đề xuất  

- **Ngày 15/05**: Doanh thu cao nhất, chắc hôm đó đầu bếp rắc thêm "bột yêu thương"!  
- **Đề xuất**: Tăng khuyến mãi giữa tuần, kẻo khách quên nhà hàng mình ngon thế nào.  
- *Chú thích*: Ngày 16/05 mưa to, khách ngại ra ngoài, ai mà trách được!  

Bot RMS
"""

        # Khởi tạo chat history
        self.chat = self.model.start_chat(history=[])

        # Tải lịch sử chat gần đây để học
        self.load_recent_chat_history()

    def load_recent_chat_history(self):
        """Tải lịch sử chat gần đây để học"""

        # Lấy 20 cuộc hội thoại gần nhất để học
        recent_chats = ChatHistory.objects.all().order_by('-created_at')[:50]

        # Thêm vào lịch sử chat của Gemini
        for chat in recent_chats:
            self.chat.history.append({
                'role': 'user',
                'parts': [chat.user_message]
            })
            self.chat.history.append({
                'role': 'model',
                'parts': [chat.bot_reply]
            })

        print(f"Đã tải {len(recent_chats)} cuộc hội thoại gần đây để học.")

    def get_inventory_stats(self):
        """Lấy thống kê tồn kho"""
        ingredients = Ingredient.objects.all()

        # Tìm các nguyên liệu sắp hết
        low_stock = []
        for ingredient in ingredients:
            if hasattr(ingredient, 'min_stock') and ingredient.quantity_in_stock <= ingredient.min_stock:
                low_stock.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity_in_stock,
                    'unit': ingredient.unit
                })
            elif ingredient.quantity_in_stock <= 50:  # Ngưỡng mặc định nếu không có min_stock
                low_stock.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity_in_stock,
                    'unit': ingredient.unit
                })

        # Thống kê nhập xuất kho gần đây
        recent_logs = InventoryLog.objects.all().order_by('-last_updated')[:10]
        recent_activities = []
        for log in recent_logs:
            action = "nhập" if log.change > 0 else "xuất"
            recent_activities.append({
                'ingredient': log.ingredient.name,
                'action': action,
                'quantity': abs(log.change),
                'date': log.last_updated.strftime('%d/%m/%Y %H:%M')
            })

        # Tổng hợp theo danh mục
        category_stats = {}
        for ingredient in ingredients:
            category = "Chưa phân loại"
            if hasattr(ingredient, 'category') and ingredient.category:
                category = ingredient.category.name

            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_value': 0
                }

            category_stats[category]['count'] += 1
            if hasattr(ingredient, 'price'):
                category_stats[category]['total_value'] += ingredient.price * ingredient.quantity_in_stock

        return {
            'total_ingredients': ingredients.count(),
            'low_stock': low_stock,
            'recent_activities': recent_activities,
            'category_stats': category_stats
        }

    def get_sales_stats(self, period='today'):
        """Lấy thống kê doanh thu"""
        today = timezone.now().date()

        if period == 'today':
            start_date = today
            period_name = "hôm nay"
        elif period == 'yesterday':
            start_date = today - timedelta(days=1)
            period_name = "hôm qua"
        elif period == 'week':
            start_date = today - timedelta(days=7)
            period_name = "7 ngày qua"
        elif period == 'month':
            start_date = today.replace(day=1)
            period_name = "tháng này"
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            period_name = "năm nay"
        else:
            start_date = today
            period_name = "hôm nay"

        # Doanh thu
        revenue = Invoice.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Số đơn hàng
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        )
        order_count = orders.count()

        # Doanh thu trung bình mỗi đơn
        avg_order_value = revenue / order_count if order_count > 0 else 0

        # Món bán chạy
        best_selling = OrderDetail.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).values('product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:5]

        # Thống kê theo trạng thái đơn hàng
        order_status = orders.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        # Thống kê theo giờ trong ngày (nếu là today)
        hourly_stats = []
        if period == 'today':
            for hour in range(24):
                hour_start = safe_make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()) + timedelta(hours=hour))
                hour_end = hour_start + timedelta(hours=1)

                hour_revenue = Invoice.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end,
                    is_deleted=False
                ).aggregate(total=Sum('total_amount'))['total'] or 0

                hour_orders = Order.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end,
                    is_deleted=False
                ).count()

                hourly_stats.append({
                    'hour': f"{hour:02d}:00",
                    'revenue': hour_revenue,
                    'orders': hour_orders
                })

        return {
            'period': period_name,
            'revenue': revenue,
            'order_count': order_count,
            'avg_order_value': avg_order_value,
            'best_selling': list(best_selling),
            'order_status': list(order_status),
            'hourly_stats': hourly_stats
        }

    def get_table_stats(self):
        """Lấy thống kê về bàn"""
        # Tổng số bàn
        tables = Table.objects.all()
        total_tables = tables.count()

        # Số bàn theo trạng thái
        table_status = tables.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        # Các phiên đang hoạt động
        active_sessions = Session.objects.filter(status='active')
        active_session_count = active_sessions.count()

        # Thời gian trung bình của phiên
        avg_session_duration = 0
        completed_sessions = Session.objects.filter(
            status='closed',
            ended_at__isnull=False
        )

        if completed_sessions.exists():
            total_duration = 0
            for session in completed_sessions:
                duration = (session.ended_at - session.started_at).total_seconds() / 60  # Phút
                total_duration += duration

            avg_session_duration = total_duration / completed_sessions.count()

        return {
            'total_tables': total_tables,
            'table_status': list(table_status),
            'active_sessions': active_session_count,
            'avg_session_duration': avg_session_duration
        }

    def get_product_stats(self):
        """Lấy thống kê về sản phẩm"""
        # Tổng số sản phẩm
        products = Product.objects.filter(is_deleted=False)
        total_products = products.count()

        # Sản phẩm theo danh mục
        category_stats = products.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')

        # Sản phẩm bán chạy nhất (30 ngày qua)
        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        best_selling = OrderDetail.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).values('product__name', 'product__price').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:10]

        # Sản phẩm có tồn kho
        in_stock_products = []
        for product in products:
            if hasattr(product, 'in_stock'):
                in_stock_products.append({
                    'name': product.name,
                    'in_stock': product.in_stock,
                    'price': product.price
                })

        return {
            'total_products': total_products,
            'category_stats': list(category_stats),
            'best_selling': list(best_selling),
            'in_stock_products': in_stock_products
        }

    def format_data_for_display(self, data_type, data):
        """Định dạng dữ liệu để hiển thị đẹp hơn"""
        if data_type == 'inventory':
            # Định dạng dữ liệu tồn kho thành bảng markdown
            low_stock_table = "| STT | Nguyên liệu | Số lượng tồn | Đơn vị |\n| :---: | :--- | :---: | :---: |\n"
            for idx, item in enumerate(data['low_stock'], 1):
                low_stock_table += f"| {idx} | {item['name']} | **{item['quantity']}** | {item['unit']} |\n"

            recent_activities_list = "| STT | Thời gian | Hoạt động | Nguyên liệu | Số lượng |\n| :---: | :--- | :---: | :--- | :---: |\n"
            for idx, item in enumerate(data['recent_activities'][:5], 1):
                recent_activities_list += f"| {idx} | {item['date']} | {item['action']} | {item['ingredient']} | **{item['quantity']}** |\n"

            return {
                'summary': f"**Tổng số nguyên liệu:** {data['total_ingredients']}\n**Nguyên liệu sắp hết:** {len(data['low_stock'])} loại",
                'low_stock_table': low_stock_table,
                'recent_activities': recent_activities_list
            }

        elif data_type == 'sales':
            # Định dạng dữ liệu doanh thu
            best_selling_table = "| STT | Sản phẩm | Số lượng | Doanh thu |\n| :---: | :--- | :---: | ---: |\n"
            for idx, item in enumerate(data['best_selling'], 1):
                best_selling_table += f"| {idx} | {item['product__name']} | **{item['total_sold']}** | **{item['revenue']:,}đ** |\n"

            order_status_list = "| STT | Trạng thái | Số lượng |\n| :---: | :--- | :---: |\n"
            status_idx = 1
            for status in data['order_status']:
                status_name = status['status']
                if status_name == 'pending':
                    status_name = 'Chờ xử lý'
                elif status_name == 'in_progress':
                    status_name = 'Đang làm'
                elif status_name == 'completed':
                    status_name = 'Hoàn thành'
                elif status_name == 'cancelled':
                    status_name = 'Đã hủy'

                order_status_list += f"| {status_idx} | {status_name} | **{status['count']}** |\n"
                status_idx += 1

            hourly_data = ""
            if data['hourly_stats']:
                hourly_data = "| STT | Giờ | Doanh thu | Số đơn |\n| :---: | :---: | ---: | :---: |\n"
                hour_idx = 1
                for hour in data['hourly_stats']:
                    if hour['orders'] > 0:
                        hourly_data += f"| {hour_idx} | {hour['hour']} | **{hour['revenue']:,}đ** | {hour['orders']} |\n"
                        hour_idx += 1

            return {
                'summary': f"**Doanh thu {data['period']}:** {data['revenue']:,}đ\n**Số đơn hàng:** {data['order_count']}\n**Giá trị trung bình/đơn:** {data['avg_order_value']:,.0f}đ",
                'best_selling_table': best_selling_table,
                'order_status': order_status_list,
                'hourly_data': hourly_data
            }

        elif data_type == 'table':
            # Định dạng dữ liệu bàn
            table_status_table = "| STT | Trạng thái | Số lượng |\n| :---: | :--- | :---: |\n"
            status_idx = 1
            for status in data['table_status']:
                status_name = status['status']
                if status_name == 'available':
                    status_name = 'Trống'
                elif status_name == 'occupied':
                    status_name = 'Đang sử dụng'
                elif status_name == 'reserved':
                    status_name = 'Đã đặt'

                table_status_table += f"| {status_idx} | {status_name} | **{status['count']}** |\n"
                status_idx += 1

            return {
                'summary': f"**Tổng số bàn:** {data['total_tables']}\n**Phiên đang hoạt động:** {data['active_sessions']}\n**Thời gian trung bình/phiên:** {data['avg_session_duration']:.1f} phút",
                'table_status': table_status_table
            }

        elif data_type == 'product':
            # Định dạng dữ liệu sản phẩm
            category_list = "| STT | Danh mục | Số sản phẩm |\n| :---: | :--- | :---: |\n"
            cat_idx = 1
            for category in data['category_stats']:
                cat_name = category['category__name'] or "Không có danh mục"
                category_list += f"| {cat_idx} | {cat_name} | **{category['count']}** |\n"
                cat_idx += 1

            best_selling_table = "| STT | Sản phẩm | Giá | Số lượng bán | Doanh thu |\n| :---: | :--- | ---: | :---: | ---: |\n"
            for idx, item in enumerate(data['best_selling'], 1):
                best_selling_table += f"| {idx} | {item['product__name']} | {item['product__price']:,}đ | **{item['total_sold']}** | **{item['revenue']:,}đ** |\n"

            return {
                'summary': f"**Tổng số sản phẩm:** {data['total_products']}",
                'category_list': category_list,
                'best_selling_table': best_selling_table
            }

        return {}

    def process_query(self, user_message):
        """Xử lý câu hỏi của người dùng"""
        user_message_lower = user_message.lower()

        # Phân tích ý định của người dùng
        if "tồn kho" in user_message_lower or "nguyên liệu" in user_message_lower:
            # Truy vấn dữ liệu tồn kho
            inventory_data = self.get_inventory_stats()
            formatted_data = self.format_data_for_display('inventory', inventory_data)

            # Tạo context cho Gemini
            context = f"""
# Thông tin tồn kho nguyên liệu

{formatted_data['summary']}

## Nguyên liệu sắp hết
{formatted_data['low_stock_table']}

## Hoạt động nhập xuất gần đây
{formatted_data['recent_activities']}

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""

        elif "doanh thu" in user_message_lower or "bán hàng" in user_message_lower:
            # Xác định khoảng thời gian
            period = 'today'
            if "hôm qua" in user_message_lower:
                period = 'yesterday'
            elif "tuần" in user_message_lower:
                period = 'week'
            elif "tháng" in user_message_lower:
                period = 'month'

            # Truy vấn dữ liệu doanh thu
            sales_data = self.get_sales_stats(period)
            formatted_data = self.format_data_for_display('sales', sales_data)

            # Tạo context cho Gemini
            context = f"""
# Thống kê doanh thu {sales_data['period']}

{formatted_data['summary']}

## Món bán chạy nhất
{formatted_data['best_selling_table']}

## Trạng thái đơn hàng
{formatted_data['order_status']}
"""

            if formatted_data['hourly_data']:
                context += f"""
## Doanh thu theo giờ
{formatted_data['hourly_data']}
"""

            context += f"\n*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*"

        elif "bàn" in user_message_lower or "phiên" in user_message_lower:
            # Truy vấn dữ liệu bàn
            table_data = self.get_table_stats()
            formatted_data = self.format_data_for_display('table', table_data)

            # Tạo context cho Gemini
            context = f"""
# Thống kê trạng thái bàn

{formatted_data['summary']}

## Trạng thái bàn
{formatted_data['table_status']}

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
        else:
            # Trường hợp không xác định được ý định cụ thể
            context = """
# Xin chào, tôi là Bot RMS!

Tôi có thể giúp bạn với các thông tin sau:

- **Tồn kho**: Kiểm tra tồn kho nguyên liệu, cảnh báo hết hàng
- **Doanh thu**: Xem doanh thu theo ngày, tuần, tháng
- **Bàn**: Kiểm tra trạng thái bàn, phiên hoạt động
- **Sản phẩm**: Thông tin về sản phẩm và danh mục

Bạn có thể hỏi tôi các câu như:
1. "Doanh thu hôm nay là bao nhiêu?"
2. "Kiểm tra tồn kho nguyên liệu"
3. "Món nào bán chạy nhất tháng này?"
4. "Trạng thái các bàn hiện tại"

Hãy hỏi tôi về một trong các chủ đề trên!
"""

        # Gửi câu hỏi và context đến Gemini
        response = self.chat.send_message(
            f"System: {self.system_prompt}\n\nContext: {context}\n\nUser: {user_message}"
        )

        # Đảm bảo phản hồi được định dạng đúng
        reply = response.text

        # Thêm định dạng cho các bảng nếu cần
        # reply = self.enhance_markdown_tables(reply)

        # Đảm bảo có chữ ký Bot RMS
        if "Bot RMS" not in reply:
            reply += "\n\n*Bot RMS*"

        return reply

    def enhance_markdown_tables(self, text):
        """Cải thiện định dạng bảng Markdown"""
        # Tìm các bảng Markdown
        table_pattern = r"(\|.+?\|(?:\n\|.+?\|)+)"

        def format_table(match):
            table = match.group(1)
            # Đảm bảo bảng có khoảng trống trước và sau
            return f"\n{table}\n"

        enhanced_text = re.sub(table_pattern, format_table, text)

        # Đảm bảo các tiêu đề được định dạng đúng
        heading_pattern = r"^(#+)\s+(.+)$"

        def format_heading(match):
            level = len(match.group(1))
            text = match.group(2)

            # Thêm emoji phù hợp với tiêu đề
            emoji = ""
            if "doanh thu" in text.lower():
                emoji = ""
            elif "tồn kho" in text.lower() or "nguyên liệu" in text.lower():
                emoji = ""
            elif "bàn" in text.lower():
                emoji = ""
            elif "món" in text.lower() or "sản phẩm" in text.lower():
                emoji = ""
            elif "trạng thái" in text.lower():
                emoji = ""
            elif "hoạt động" in text.lower():
                emoji = ""
            elif "xin chào" in text.lower():
                emoji = ""

            return f"{'#' * level} {emoji}{text}"

        enhanced_text = re.sub(heading_pattern, format_heading, enhanced_text, flags=re.MULTILINE)

        return enhanced_text

    def save_chat_history(self, user_message, bot_reply):
        """Lưu lịch sử chat vào database"""

        ChatHistory.objects.create(
            user_message=user_message,
            bot_reply=bot_reply
        )

        # Thêm vào lịch sử chat của Gemini để học
        self.chat.history.append({
            'role': 'user',
            'parts': [user_message]
        })
        self.chat.history.append({
            'role': 'model',
            'parts': [bot_reply]
        })
