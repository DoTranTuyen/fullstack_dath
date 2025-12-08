import re
import json
import google.generativeai as genai
from django.conf import settings
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta, datetime

from web_01.models import (
    ChatHistory, Invoice, Order, OrderDetail,
    Ingredient, InventoryLog, Table, Session, Product
)
import re


def remove_emoji(text):
    emoji_pattern = re.compile(
        "["u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U0001F300-\U0001F5FF"     # Symbols & pictographs
        u"\U0001F680-\U0001F6FF"     # Transport & map symbols
        u"\U0001F1E0-\U0001F1FF"     # Flags (iOS)
        u"\U00002700-\U000027BF"     # Dingbats
        u"\U0001F900-\U0001F9FF"     # Supplemental Symbols and Pictographs
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


class CustomerChatbot:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.system_prompt = """
Bạn là **FoodieBot**, trợ lý AI siêu dễ thương và nhiệt tình của khách hàng nhà hàng.

 **Nhiệm vụ chính của bạn**:
- Gợi ý món ăn & đồ uống theo sở thích khách hàng  
- Gợi ý món bán chạy  
- Gợi ý món theo thời tiết (nóng, lạnh, mưa, nắng)  
- Gợi ý món theo thời gian trong ngày  
- Gợi ý món theo tâm trạng khách  
- Gợi ý combo thông minh  
- Hỗ trợ thông tin món ăn (giá, mô tả, nguyên liệu)  

 **Phong cách trả lời**:
- Dễ thương, vui vẻ, tích cực, thân thiện  
- Trả lời ngắn gọn – không quá dài  
- Thỉnh thoảng thêm emoji  
- Luôn ưu tiên gợi ý món trong thực đơn thật của nhà hàng (từ DB)  
- Luôn xưng “mình” hoặc “mình là FoodieBot”

**Quy tắc quan trọng**:
- Nếu khách hỏi món không có trong hệ thống → đề xuất món tương tự  
- Không bao giờ bịa ra giá  
- Khi trả lời luôn ưu tiên dữ liệu thật từ database  
"""

        self.chat = self.model.start_chat(history=[])

        # Tải lịch sử chat không cần quá nhiều
        self.load_recent_chat()

    def load_recent_chat(self):
        """Load history nhẹ để bot tự nhiên hơn"""
        recent_chats = ChatHistory.objects.all().order_by('-created_at')[:50]

        for msg in recent_chats:
            self.chat.history.append({'role': 'user', 'parts': [msg.user_message]})
            self.chat.history.append({'role': 'model', 'parts': [msg.bot_reply]})

    # ---------------------------------------------------------
    #  ✨  MODULE 1 — GỢI Ý MÓN BÁN CHẠY
    # ---------------------------------------------------------
    def get_best_selling(self):
        best = (
            OrderDetail.objects
            .values("product__name", "product__price")
            .annotate(total=Sum("quantity"))
            .order_by("-total")[:5]
        )

        formatted = [
            f"{item['product__name']} – bán {item['total']} phần – giá {item['product__price']}đ"
            for item in best
        ]

        return formatted

    # ---------------------------------------------------------
    #  ✨ MODULE 2 — GỢI Ý THEO THỜI TIẾT
    # ---------------------------------------------------------
    def suggest_by_weather(self, weather=None):
        """
        weather = hot | cold | rainy | sunny
        Nếu không truyền → tự detect thời tiết ngoài trời
        """

        if weather == "hot":
            return ["Trà chanh lạnh", "Nước ép cam", "Salad trái cây", "Trà đào cam sả"]
        if weather == "cold":
            return ["Lẩu Thái", "Phở bò", "Mì cay", "Cacao nóng"]
        if weather == "rainy":
            return ["Mì cay", "Lẩu kim chi", "Khoai chiên nóng", "Trà gừng mật ong"]
        return ["Phở gà", "Cơm tấm", "Nước mía", "Trà sữa truyền thống"]

    # ---------------------------------------------------------
    #  ✨ MODULE 3 — GỢI Ý THEO THỜI GIAN TRONG NGÀY
    # ---------------------------------------------------------
    def suggest_by_time(self):
        now = datetime.now().hour
        if now < 11:
            return ["Bánh mì trứng", "Bún bò", "Cafe sữa đá"]
        elif 11 <= now < 17:
            return ["Cơm gà", "Bún chả", "Trà tắc", "Bún thịt nướng"]
        return ["Lẩu Thái", "Pizza", "Mì Ý", "Trà đào cam sả"]

    # ---------------------------------------------------------
    #  ✨ MODULE 4 — GỢI Ý TỪ DATABASE
    # ---------------------------------------------------------
    def get_menu_items(self):
        products = Product.objects.filter(is_deleted=False)
        return [p.name for p in products]

    # ---------------------------------------------------------
    #  ✨ MODULE 5 — XỬ LÝ TIN NHẮN
    # ---------------------------------------------------------
    def ask(self, message):
        best_selling = self.get_best_selling()
        menu_items = self.get_menu_items()
        today_suggest = self.suggest_by_time()

        context = f"""
    Dữ liệu thật từ database:

    ### Món bán chạy:
    {best_selling}

    ### Toàn bộ món trong menu:
    {menu_items}

    ### Gợi ý theo thời gian trong ngày:
    {today_suggest}
    """

        final_prompt = self.system_prompt + "\n\n" + context + "\n\nNgười dùng hỏi: " + message

        response = self.chat.send_message(final_prompt)
        reply = response.text

        # ❗ LỌC BỎ EMOJI TRƯỚC KHI LƯU
        clean_user_msg = remove_emoji(message)
        clean_bot_msg = remove_emoji(reply)

        ChatHistory.objects.create(
            user_message=clean_user_msg,
            bot_reply=clean_bot_msg
        )

        return reply
