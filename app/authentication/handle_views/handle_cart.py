from core.__Include_Library import *
from rest_framework.response import Response
from authentication.mixins import AuthenticationPermissionMixin
from authentication.serializers import CartSerializer, CartItemSerializer
from web_01.models import Product, Cart, CartItem
from rest_framework import status


class CartViewSet(AuthenticationPermissionMixin, ViewSet):
    parser_classes = (JSONParser, MultiPartParser)
    # 🔄 Lấy giỏ hàng của customer

    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        customer = request.user.customer  # Giả sử user đã đăng nhập
        cart, created = Cart.objects.get_or_create(customer=customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # 🔄 Thêm sản phẩm vào giỏ hàng
    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        customer = request.user.customer
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id or not quantity:
            return Response({'error': 'product_id and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(customer=customer)

        # Kiểm tra sản phẩm đã có trong giỏ hàng chưa
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        cart_item.save()
        return Response({'message': 'Đã thêm vào giỏ hàng!'}, status=status.HTTP_201_CREATED)

    # 🔄 Xóa sản phẩm khỏi giỏ hàng
    @action(detail=False, methods=['delete'], url_path='remove-item')
    def remove_item(self, request):
        customer = request.user.customer
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({'error': 'Thiếu product_id!'}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, customer=customer)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        return Response({'message': 'Đã xóa khỏi giỏ hàng!'}, status=status.HTTP_200_OK)

    # 🔄 Cập nhật số lượng sản phẩm trong giỏ hàng
    @action(detail=False, methods=['put'], url_path='update-item')
    def update_item(self, request):
        customer = request.user.customer
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', None)

        if not product_id or quantity is None:
            return Response({'error': 'Thiếu product_id hoặc quantity!'}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, customer=customer)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        if int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
            return Response({'message': 'Đã cập nhật giỏ hàng!'}, status=status.HTTP_200_OK)
        else:
            cart_item.delete()
            return Response({'message': 'Đã xóa sản phẩm khỏi giỏ hàng!'}, status=status.HTTP_200_OK)
