from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q
from web_01.models import Customer


class CustomerManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/customer/customer_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "desc")

            # ✅ Mapping column cho DataTables
            column_mapping = {
                0: "id",
                1: "user__first_name",
                2: "user__username",
                3: "loyalty_points",
                4: "created_at"
            }
            print("column_mapping", column_mapping)

            if order_column_index not in column_mapping:
                order_column_index = 0

            order_column = column_mapping[order_column_index]
            if order_dir == "desc":
                order_column = "-" + order_column

            # ✅ Query Customers
            customer_list = Customer.objects.select_related('user').filter(is_deleted=False)
            print('-----1------', customer_list)
            if search_value:
                customer_list = customer_list.filter(
                    Q(user__username__icontains=search_value) |
                    Q(user__first_name__icontains=search_value) 
                    # Q(user__last_name__icontains=search_value)
                )

            total_count = customer_list.count()
            customer_list = customer_list.order_by("-created_at")[start:start + length]

            # ✅ Chuẩn bị dữ liệu JSON trả về
            customers_data = [
                {
                    "index": index + 1,
                    "id": customer.id,
                    "first_name": customer.user.first_name if customer.user else "N/A",
                    "username": customer.user.username if customer.user else "",
                    "loyalty_points": customer.loyalty_points,
                    "created_at": customer.formatted_created_at,
                }
                for index, customer in enumerate(customer_list, start=start)
            ]
            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": customers_data
            }, safe=False)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@csrf_exempt
def update_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            customer_id = data.get('id')
            loyalty_points = data.get('loyalty_points')
            
            if not customer_id:
                return JsonResponse({"status": "error", "message": "ID khách hàng không hợp lệ"}, status=400)
                
            customer = Customer.objects.get(id=customer_id)
            
            # Cập nhật điểm tích lũy
            if loyalty_points is not None:
                try:
                    customer.loyalty_points = int(loyalty_points)
                except ValueError:
                    return JsonResponse({"status": "error", "message": "Điểm tích lũy phải là số"}, status=400)
            
            customer.save()
            
            return JsonResponse({
                "status": "success", 
                "message": "Cập nhật khách hàng thành công",
                "customer": {
                    "id": customer.id,
                    "first_name": customer.user.first_name if customer.user else "N/A",
                    "loyalty_points": customer.loyalty_points,
                    "created_at": customer.formatted_created_at
                }
            })
            
        except Customer.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Không tìm thấy khách hàng"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Phương thức không được hỗ trợ"}, status=405)


@csrf_exempt
def delete_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            customer_id = data.get('id')
            
            if not customer_id:
                return JsonResponse({"status": "error", "message": "ID khách hàng không hợp lệ"}, status=400)
                
            customer = Customer.objects.get(id=customer_id)
            
            # Soft delete
            customer.is_deleted = True
            customer.save()
            
            return JsonResponse({
                "status": "success", 
                "message": "Xóa khách hàng thành công"
            })
            
        except Customer.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Không tìm thấy khách hàng"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Phương thức không được hỗ trợ"}, status=405)
