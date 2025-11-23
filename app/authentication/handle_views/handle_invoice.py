from core.__Include_Library import *
from rest_framework.response import Response
from rest_framework import status
from authentication.mixins import AuthenticationPermissionMixin
from authentication.serializers import InvoiceSerializer, InvoiceDetailSerializer
from web_01.models import Invoice, Cart, CartItem, Order, OrderDetail, Notification

from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import hmac
import hashlib
import uuid
import requests
from django.conf import settings


class InvoiceViewSet(AuthenticationPermissionMixin, ViewSet):
    parser_classes = (JSONParser, MultiPartParser)
    # 🔄 Tạo Invoice từ Cart

    def create(self, request):
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({'error': 'Giỏ hàng trống!'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra session active
        active_session = customer.session_set.filter(status='active').first()
        if not active_session:
            return Response({'error': 'Không có session nào đang active!'}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo Invoice
        invoice, _ = Invoice.objects.get_or_create(
            session=active_session
        )

        # Tạo Order
        order = Order.objects.create(invoice=invoice, total=0)  # Cập nhật sau
        total_amount = 0  # Khởi tạo tổng giá trị đơn hàng

        for item in cart_items:
            total_price = item.product.price * item.quantity
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                total=total_price
            )
            total_amount += total_price  # Cộng dồn vào tổng đơn hàng

        # Cập nhật tổng tiền vào Invoice & Order
        invoice.total_amount += total_amount
        order.total = total_amount
        invoice.save()
        order.save()

        # Xóa giỏ hàng
        cart_items.delete()

        # Trả về thông tin Invoice
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        customer = request.user.customer
        active_session = customer.session_set.filter(status='active').first()

        if not active_session:
            return Response({'error': 'Không có session nào đang active!'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.filter(session=active_session).first()
        if not invoice:
            return Response({'error': 'Chưa có hóa đơn nào trong session hiện tại!'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    # 🏦 Action: Tạo thanh toán Momo

    @action(detail=False, methods=['post'], url_path='payment')
    @method_decorator(csrf_exempt)
    def create_payment(self, request):
        customer = request.user.customer
        active_session = customer.session_set.filter(status='active').first()

        if not active_session:
            return Response({'error': 'Không có session nào đang active!'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.filter(session=active_session).first()
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        accessKey = "F8BBA842ECF85"
        secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        orderInfo = "PAY WITH MOMO"
        partnerCode = "MOMO"
        redirectUrl = f"{settings.FRONT_END_URL}/momo/payment/success"
        ipnUrl = f"{settings.CURRENT_URL}/api/invoice/momo-ipn/"
        amount = f"{invoice.total_amount}"
        orderId = f'INVOICE_{str(random.randint(0, 10000))}_00{invoice.id}'
        requestId = str(uuid.uuid4())
        extraData = ""

        rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType=payWithMethod"
        signature = hmac.new(secretKey.encode(), rawSignature.encode(), hashlib.sha256).hexdigest()

        data = {
            'partnerCode': partnerCode,
            'orderId': orderId,
            'partnerName': "MoMo Payment",
            'storeId': "Test Store",
            'ipnUrl': ipnUrl,
            'amount': amount,
            'lang': "vi",
            'requestType': "payWithMethod",
            'redirectUrl': redirectUrl,
            'autoCapture': True,
            'orderInfo': orderInfo,
            'requestId': requestId,
            'extraData': extraData,
            'signature': signature,
            'orderGroupId': ""
        }

        response = requests.post(endpoint, json=data)
        return Response(response.json(), status=response.status_code)

    # 🔄 IPN từ MoMo (disable CSRF)
    @action(detail=False, methods=['post'], url_path='momo-ipn')
    @method_decorator(csrf_exempt)
    def momo_ipn(self, request):
        customer = request.user.customer
        active_session = customer.session_set.filter(status='active').first()

        if not active_session:
            return Response({'error': 'Không có session nào đang active!'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.filter(session=active_session).first()

        # active_session.status = 'closed'
        # active_session.table.status = 'available'
        invoice.payment_method = 'momo'
        # invoice.total_amount = total
        # invoice.discount = discount
        invoice.order_set.all().update(status='completed')
        invoice.save()
        active_session.save()
        active_session.table.save()
        active_session.customer.loyalty_points = math.ceil(invoice.total_amount / 10000) + active_session.customer.loyalty_points
        active_session.customer.save()

        return JsonResponse({'status': 'success', 'session': {
            'session_id': active_session.id,
        }})
