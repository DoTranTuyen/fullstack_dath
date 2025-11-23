
from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.views.decorators.csrf import csrf_exempt
from web_01.models import Table, Order, Product, Invoice, Session, OrderDetail
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField

def service_dashboard(request):
    """Hiển thị dashboard quản lý dịch vụ"""
    # Lấy danh sách bàn
    tables = Table.objects.all().order_by('table_number')

    # Lấy danh sách sản phẩm
    products = Product.objects.filter(is_deleted=False).order_by('category__name', 'name')

    context = {
        'table_list': tables,
        'product_list': products,
    }

    return render(request, '/apps/web_01/service/service_list.html', context)


def process_data_order(request, table_id, is_payment=0):
    # Kiểm tra nếu không có table_id
    if not table_id:
        return JsonResponse({"success": False, "message": "Vui lòng chọn bàn!"}, status=400)

    # Lấy session đang hoạt động của bàn
    session = Session.objects.filter(table_id=table_id, status='active').select_related("customer", 'customer__user').first()

    if not session:
        return JsonResponse({"success": False, "message": "Bàn này chưa có khách hoặc chưa được mở!"}, status=404)

    # Lấy danh sách hóa đơn (Invoices) của bàn này
    invoices = session.invoice_set.prefetch_related("order_set__orderdetail_set__product").all()

    if not invoices.exists():
        return JsonResponse({"success": False, "message": "Bàn này chưa có đơn nào!"}, status=404)

    order_details_list = []
    total_amount = 0
    all_paid = True  # giả định tất cả đã thanh toán
    for invoice in invoices:
        for order in invoice.order_set.all():
            order_data = {
                "order_id": order.id,
                "status": order.status,
                "status_display": order.get_status_display(),
                "order_details": [],
                "order_total": 0
            }
            if order.status != 'completed':
                all_paid = False  # phát hiện 1 đơn chưa thanh toán

            for detail in order.orderdetail_set.all():
                item = {
                    "item_id": detail.id,
                    "product_name": detail.product.name,
                    "product_image_url": detail.product.image.url if detail.product.image else '',
                    "quantity": detail.quantity,
                    "price": detail.price,
                    "total": detail.total,
                    "status": detail.status,
                    "status_display": detail.get_status_display(),
                }
                order_data["order_details"].append(item)
                if detail.status != 'cancelled':
                    order_data["order_total"] += detail.total
                    total_amount += detail.total

            order_details_list.append(order_data)

    # Lấy thông tin khách hàng (nếu có)
    customer_name = f'{session.customer.user.username}({session.customer.user.first_name})' if session.customer else "Khách vãng lai"
    if is_payment:
        html_template = 'apps/web_01/service/modal/content_payment_order.html'
    else:
        html_template = 'apps/web_01/service/order_item.html'
    # Trả về template với danh sách đã gộp
    return render(request, html_template, {
        "order_details": order_details_list,
        "total_amount": total_amount,
        "customer_name": customer_name,
        "session": session,
        "table_id": table_id,
        "all_paid": all_paid
    })


@login_required
def get_order_by_table(request):
    table_id = request.GET.get('table_id')
    is_payment = request.GET.get('is_payment')
    return process_data_order(request, table_id, is_payment)


def get_product_service(request):
    html_template = '/apps/web_01/service/product_item.html'
    product_name = request.GET.get('name', '')
    products = Product.objects.filter(name__icontains=product_name)
    return render(request, html_template, {"product_list": products})


@csrf_exempt
def complete_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table_id = data.get("table_id")
            total = data.get("total")
            discount = data.get("discount_percent")
            payment_method = data.get("payment_method", "cash")  # Mặc định là tiền mặt

            # 🔹 Tìm session của bàn (giả sử có model Session liên kết)
            session = Session.objects.filter(table_id=table_id, status='active').first()

            if not session:
                return JsonResponse({"message": "Không tìm thấy session cho bàn này!", "status": "error"}, status=400)

            invoice = Invoice.objects.get(session=session)

            session.status = 'closed'
            session.table.status = 'available'
            invoice.payment_method = payment_method
            invoice.total_amount = total
            invoice.discount = discount
            invoice.order_set.all().update(status='completed', discount=discount)
            invoice.save()
            session.save()
            session.table.save()
            session.customer.loyalty_points = math.ceil(total / 10000) + session.customer.loyalty_points
            session.customer.save()

            return JsonResponse({
                "message": "Thanh toán thành công!",
                "invoice_id": invoice.id,
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({"message": str(e), "status": "error"}, status=400)

    return JsonResponse({"message": "Phương thức không hợp lệ!"}, status=405)


def complete_payment_multi_order(request):
    try:
        data = json.loads(request.body)

        order_ids = data.get('order_ids', [])
        table_id = data.get('table_id')
        discount_percent = data.get('discount_percent', 0)
        payment_method = data.get('payment_method', 'cash')
        total_amount = data.get('total', 0)

        if not order_ids:
            return JsonResponse({'success': False, 'message': 'Không có đơn hàng nào được chọn.'}, status=400)

        # Lấy danh sách các order
        orders = Order.objects.filter(id__in=order_ids).select_related('invoice')
        if not orders.exists():
            return JsonResponse({'success': False, 'message': 'Không tìm thấy đơn hàng.'}, status=404)
        orders.update(
            discount=discount_percent
        )

        with transaction.atomic():
            # Duyệt qua các đơn và cập nhật trạng thái đã thanh toán
            for order in orders:
                order.status = 'completed'
                order.save()

                # Cập nhật trạng thái hóa đơn nếu tất cả đơn trong hóa đơn đã thanh toán
                invoice = order.invoice
                related_orders = invoice.order_set.all()
                if all(o.status == 'completed' for o in related_orders):
                    invoice.payment_method = payment_method
                    invoice.total_amount = sum(order.total - order.total * order.discount/100 for order in related_orders)
                    invoice.save()

            # TODO: Ghi lại lịch sử thanh toán nếu muốn
            # PaymentHistory.objects.create(...)

        return process_data_order(request, table_id)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Đã xảy ra lỗi: {str(e)}'}, status=500)


def update_item_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_id = data.get('table_id')
        order_id = data.get('order_id')
        item_id = data.get('item_id')
        new_status = data.get('status')

        try:
            item = OrderDetail.objects.get(id=item_id, order_id=order_id)
            old_status = item.status  # Trạng thái cũ trước khi cập nhật
            item.status = new_status
            item.updated_by = request.user
            item.save()

            # Nếu chuyển từ trạng thái khác sang 'cancelled' => cập nhật tổng tiền
            if new_status == 'cancelled':
                order = item.order
                invoice = order.invoice  # Quan hệ FK đến Order
                order.total -= item.price * item.quantity  # hoặc item.total_price nếu có
                order.save()
                invoice.total_amount -= order.total
                invoice.save()

            return process_data_order(request, table_id)
        except OrderDetail.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def end_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        print('data', data)
        session_id = data.get('session_id')

        try:
            session = Session.objects.get(id=session_id)
            invoice = Invoice.objects.get(session=session)
            session.table.status = 'available'
            # session.ended_at = timezone.now()

            # session.status = 'closed'
            invoice.order_set.all().update(status='completed')
            session.save()
            session.table.save()
            return JsonResponse({'success': True})
        except Session.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def add_product_to_order(request):
    data = json.loads(request.body)
    order_id = data.get("order_id")
    table_id = data.get("table_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    try:
        order = Order.objects.get(id=order_id)
        product = Product.objects.get(id=product_id)

        # Kiểm tra sản phẩm đã có trong đơn chưa
        item, created = OrderDetail.objects.get_or_create(
            order=order,
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.price,
                'total': product.price * quantity,
                'status': 'pending'
            }
        )

        if not created:
            # Nếu đã tồn tại -> cập nhật quantity và total
            item.quantity += quantity
            item.total = item.price * item.quantity
            item.save()

        return process_data_order(request, table_id)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
