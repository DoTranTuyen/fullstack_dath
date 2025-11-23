from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q
from web_01.models import Order, OrderDetail, Invoice


class OrderManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/order/order_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, **kwargs):
        try:
            # Lấy params từ request
            params = json.loads(request.POST.get('params', '{}'))

            search_value = params.get('search', '').strip()
            start = int(params.get('start', 0))
            length = int(params.get('length', 10))
            order_column_index = int(params.get('order_column', 0))
            order_dir = params.get('order_dir', 'asc')

            # Mapping cột DataTables với DB
            column_mapping = {
                0: "id",
                1: "invoice__session__customer__name",
                2: "invoice__session__table__name",
                3: "total",
                4: "created_at"
            }
            order_column = column_mapping.get(order_column_index, "id")
            if order_dir == "desc":
                order_column = "-" + order_column

                # Lấy tất cả các invoice và các order liên quan
            invoice_list = Invoice.objects.filter(session__status='closed').select_related(
                'session__customer',
                'session__table'
            )

            # Đảm bảo rằng bạn lấy các order liên quan đến invoice
            order_list = Order.objects.select_related(
                'invoice',
                'invoice__session__customer',
                'invoice__session__table'
            )

            # Dữ liệu trả về cho UI
            invoices_data = []
            for index, invoice in enumerate(invoice_list):
                related_orders = order_list.filter(invoice=invoice)

                # # Lấy thông tin các đơn hàng liên quan
                # orders_data = [
                #     {
                #         "order_id": order.id,
                #         "username": order.invoice.session.customer.user.username,
                #         "first_name": order.invoice.session.customer.user.first_name,
                #         "table": f"Bàn {order.invoice.session.table.table_number}" if order.invoice.session.table else "Không có bàn",
                #         "total": order.formatted_price,
                #         "status": order.status,
                #         "status_display": order.get_status_display(),
                #         "formatted_created_at": order.formatted_created_at,
                #     }
                #     for order in related_orders
                # ]

                # Thêm vào dữ liệu của invoice
                invoices_data.append({
                    "index": index + 1,
                    "id": invoice.id,
                    "customer_name": f'{invoice.session.customer.user.username}({invoice.session.customer.user.first_name})',
                    "payment_method": invoice.payment_method,
                    "payment_method_display": invoice.get_payment_method_display(),
                    "total_amount": invoice.formatted_total_amount,
                    "created_at": invoice.created_at.strftime('%d/%m/%Y'),
                    # "total_orders": len(orders_data),
                    # "orders": orders_data  # Đưa thông tin các order vào đây
                })

            # Trả về JSON cho DataTables
            return JsonResponse({
                "draw": params.get('draw', 1),
                "recordsTotal": invoice_list.count(),
                "recordsFiltered": invoice_list.count(),  # Tính filtered count nếu có
                "data": invoices_data
            })

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            return JsonResponse({"error": str(e)}, status=400)


@login_required
def detail_order(request, id):
    order = get_object_or_404(
        Order.objects.select_related(
            "invoice", "invoice__session", "invoice__session__customer"
        ),
        id=id
    )

    # Lấy danh sách món ăn trong đơn, tối ưu bằng prefetch_related
    order_details = OrderDetail.objects.filter(order=order).exclude(status='cancelled').select_related("product")

    context = {
        "order": order,
        "order_details": order_details
    }
    return render(request, "apps/web_01/modal/content/content_detail_order.html", context)


@login_required
def detail_invoice(request, id):
    # Lấy hóa đơn từ database, nếu không tìm thấy thì trả về lỗi 404
    invoice = get_object_or_404(Invoice, id=id)

    order_details_list = []
    for order in invoice.order_set.all():
        order_data = {
            "order_id": order.id,
            "status": order.status,
            "status_display": order.get_status_display(),
            "order_details": [],
            "order_total": order.total,
            "order_discount": order.discount,
        }

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
            # if detail.status != 'cancelled':
            #     order_data["order_total"] += detail.total
                # total_amount += detail.total

        order_details_list.append(order_data)

    # Tạo context cho template
    context = {
        'invoice': invoice,
        'order_details': order_details_list
    }

    # Render template modal với dữ liệu từ context
    return render(request, "/apps/web_01/modal/content/content_detail_order.html", context)
