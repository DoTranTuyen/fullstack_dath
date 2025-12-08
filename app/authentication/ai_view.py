import pickle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from rest_framework.permissions import IsAuthenticated

# Import models và serializers từ app 'web_01' của bạn
from web_01.models import Product, OrderDetail, Customer
# Giả sử bạn có serializer cho Product trong web_01, nếu không bạn cần tạo nó.
# from web_01.serializers import ProductSerializer 

# --- Tải mô hình ---
# Tải mô hình một lần khi server khởi động để tối ưu hiệu năng
RECOMMENDATION_MODEL = None
ALL_PRODUCT_IDS = []
try:
    model_path = os.path.join(settings.BASE_DIR, 'recommendations', 'recommendation_model.pkl')
    with open(model_path, 'rb') as f:
        RECOMMENDATION_MODEL = pickle.load(f)

    # Đổi tên file từ all_food_ids.pkl thành all_product_ids.pkl cho nhất quán
    product_ids_path = os.path.join(settings.BASE_DIR, 'recommendations', 'all_product_ids.pkl')
    with open(product_ids_path, 'rb') as f:
        ALL_PRODUCT_IDS = pickle.load(f)
    
    print("INFO: Tải mô hình gợi ý thành công!")
except FileNotFoundError as e:
    print(f"WARNING: Không tìm thấy file mô hình gợi ý: {e}. API gợi ý sẽ không hoạt động.")
except Exception as e:
    print(f"ERROR: Lỗi khi tải mô hình gợi ý: {e}")


class FoodSuggestionView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not RECOMMENDATION_MODEL or not ALL_PRODUCT_IDS:
            return Response(
                {"error": "Hệ thống gợi ý hiện không khả dụng."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        user = request.user
        
        # Lấy danh sách các sản phẩm người dùng đã đặt
        # Dựa trên cấu trúc model: OrderDetail -> Order -> Invoice -> Session -> Customer -> User
        ordered_product_ids = set(
            OrderDetail.objects.filter(order__invoice__session__customer__user=user)
                               .values_list('product_id', flat=True)
        )

        # Dự đoán điểm cho các sản phẩm người dùng chưa từng đặt
        predictions = []
        for product_id in ALL_PRODUCT_IDS:
            if product_id not in ordered_product_ids:
                prediction = RECOMMENDATION_MODEL.predict(uid=user.id, iid=product_id)
                predictions.append((product_id, prediction.est))

        predictions.sort(key=lambda x: x[1], reverse=True)
        top_n_suggestions = predictions[:5]
        suggested_product_ids = [product_id for product_id, rating in top_n_suggestions]
        
        if not suggested_product_ids:
            return Response([], status=status.HTTP_200_OK)

        # Tạm thời trả về JSON thủ công vì chưa có ProductSerializer
        suggested_products = Product.objects.filter(id__in=suggested_product_ids)
        preserved_order = sorted(suggested_products, key=lambda p: suggested_product_ids.index(p.id))
        
        data = [{'id': p.id, 'name': p.name, 'price': p.price, 'image': p.image.url if p.image else None} for p in preserved_order]

        return Response(data, status=status.HTTP_200_OK)