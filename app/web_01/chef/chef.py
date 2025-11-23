from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from web_01.models import Order, OrderDetail, Product, Ingredient
from web_01.chef.decorators import chef_required
import json


@login_required
@chef_required
def chef_dashboard(request):
    """Hiển thị dashboard cho đầu bếp"""
    # Lấy các đơn hàng đang chờ xử lý và đang thực hiện
    
    
    pending_orders = OrderDetail.objects.filter(
        status='pending',
        is_deleted=False
    ).select_related('order', 'product','order__invoice','order__invoice__session','order__invoice__session__table').order_by('created_at')

    in_progress_orders = OrderDetail.objects.filter(
        status='in_progress',
   ).select_related('order', 'product','order__invoice','order__invoice__session','order__invoice__session__table').order_by('created_at')

    completed_orders = OrderDetail.objects.filter(
        status='completed',
        updated_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
   ).select_related('order', 'product','order__invoice','order__invoice__session','order__invoice__session__table').order_by('created_at').order_by('-updated_at')[:10]

    # Lấy danh sách món ăn phổ biến
    popular_dishes = Product.objects.filter(
    )[:10]

    # Kiểm tra nguyên liệu sắp hết
    low_stock_ingredients = Ingredient.objects.filter(
        quantity_in_stock__lte=50,
    ).order_by('quantity_in_stock')

    context = {
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'completed_orders': completed_orders,
        'popular_dishes': popular_dishes,
        'low_stock_ingredients': low_stock_ingredients,
    }

    return render(request, '/apps/web_01/dashboard/chef_dashboard.html', context)

@login_required
@chef_required
def update_order_status(request):
    """Cập nhật trạng thái món ăn"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_detail_id = data.get('order_detail_id')
            new_status = data.get('status')
            
            if not order_detail_id or not new_status:
                return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin cần thiết'})
            
            # Kiểm tra trạng thái hợp lệ
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            if new_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': 'Trạng thái không hợp lệ'})
            
            # Cập nhật trạng thái
            order_detail = get_object_or_404(OrderDetail, id=order_detail_id, is_deleted=False)
            order_detail.status = new_status
            order_detail.updated_at = timezone.now()
            
            order_detail.save()
            
            # Kiểm tra nếu tất cả các món trong đơn hàng đã hoàn thành
            # all_completed = True
            # for detail in OrderDetail.objects.filter(order=order_detail.order, is_deleted=False):
            #     if detail.status != 'completed' and detail.status != 'cancelled':
            #         all_completed = False
            #         break
            
            # Nếu tất cả đã hoàn thành, cập nhật trạng thái đơn hàng
            # if all_completed:
            #     order_detail.order.status = 'completed'
            #     # order_detail.order.completed_at = timezone.now()
            #     order_detail.order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cập nhật trạng thái thành công',
                'order_detail': {
                    'id': order_detail.id,
                    'status': order_detail.status,
                    'updated_at': order_detail.updated_at.strftime('%H:%M:%S')
                }
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không được hỗ trợ'})


