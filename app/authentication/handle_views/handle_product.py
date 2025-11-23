from core.__Include_Library import *
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from authentication.serializers import ProductSerializer
from web_01.models import Product


class ProductPagination(PageNumberPagination):
    page_size = 10  # Số sản phẩm trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 100  # Giới hạn tối đa số sản phẩm trên một trang


class ProductViewSet(ViewSet):
    pagination_class = ProductPagination

    # 🛒 **Lấy danh sách sản phẩm với phân trang**
    @action(detail=False, methods=['get'], url_path='list')
    def list_products(self, request):
        category_id = request.query_params.get('category_id', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        name = request.query_params.get('name', None)

        # 🔄 Lọc sản phẩm theo các điều kiện
        products = Product.objects.filter(category__status='active', status='active')

        if category_id:
            products = products.filter(category_id=category_id)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if name:
            products = products.filter(name__icontains=name)

        # 🏷 **Áp dụng phân trang**
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    # 📌 **Chi tiết sản phẩm**
    @action(detail=True, methods=['get'], url_path='detail')
    def product_detail(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
