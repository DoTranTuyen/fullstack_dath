from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField, Case, When, Value, CharField, Count
from web_01.models import Ingredient, InventoryLog, Category
from web_01.utils.utils import get_username
from django import forms
from django.utils import timezone
from datetime import timedelta
import json
from web_01.models import Notification


class InventoryManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/web_01/inventory/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Thêm các danh mục nguyên liệu nếu cần
        context['ingredients'] = Ingredient.objects.filter()
        return context

    def post(self, request, *args, **kwargs):

        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()

            # Lọc theo danh mục nếu có
            category = request.POST.get("category", "[]")  # Nếu không có, mặc định là []
            price = request.POST.get("price", "-1")
            category_ids = json.loads(category)  # Chuyển từ JSON thành danh sách Python
            stock_status = request.POST.get("stock_status", '')

            # Queryset chính
            qs = Ingredient.objects.all()

            # Lọc theo danh mục
            if category_ids:
                qs = qs.filter(id__in=category_ids)

            # Tìm kiếm (nếu có)
            if search_value:
                qs = qs.filter(
                    Q(name__icontains=search_value) |
                    Q(unit__icontains=search_value)
                )

            # Thêm trường tính toán cho trạng thái tồn kho

            if stock_status == 'low':
                qs = qs.filter(quantity_in_stock__lte=10)
            elif stock_status == 'medium':
                qs = qs.filter(quantity_in_stock__lte=30)
            elif stock_status == 'good':
                qs = qs.filter(quantity_in_stock__gt=30)

            # Sắp xếp
            order_column = request.POST.get('order[0][column]', '0')
            order_dir = request.POST.get('order[0][dir]', 'asc')

            # Xác định cột để sắp xếp
            order_columns = ['id', 'name', 'quantity_in_stock', 'unit']
            if order_column and int(order_column) < len(order_columns):
                column_name = order_columns[int(order_column)]
                if order_dir == 'desc':
                    qs = qs.order_by(F'-{column_name}')
                else:
                    qs = qs.order_by(F(column_name))
            else:
                # Mặc định sắp xếp theo tên
                qs = qs.order_by('name')

            total_count = qs.count()
            qs = qs[start:start+length]

            data = []
            for index, ing in enumerate(qs):
                # Lấy log gần nhất
                latest_log = ing.inventorylog_set.order_by('-last_updated').first()

                data.append({
                    'index': start + index + 1,
                    'id': ing.id,
                    'name': ing.name,
                    'unit': ing.get_unit_display(),
                    'quantity': ing.quantity_in_stock,
                    'latest_update': latest_log.last_updated.strftime('%d/%m/%Y %H:%M') if latest_log else '-',
                    'latest_user': get_username(latest_log.user) if latest_log and latest_log.user else '-',
                })

            return JsonResponse({
                "draw": draw,
                "recordsTotal": Ingredient.objects.count(),
                "recordsFiltered": total_count,
                "data": data
            }, safe=False)

        except Exception as e:
            print('erro', str(e))
            return JsonResponse({"error": str(e)}, status=400)


def inventory_log_list(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    logs = ingredient.inventorylog_set.all().select_related('user').order_by('-last_updated')
    current_stock = ingredient.quantity_in_stock
    latest_log = logs.first()  # Log gần nhất

    # Thêm thông tin về người dùng gần nhất
    latest_user = get_username(latest_log.user) if latest_log and latest_log.user else '-'

    # Thêm thông tin về danh mục
    category_name = ingredient.category.name if hasattr(ingredient, 'category') and ingredient.category else 'Không có danh mục'

    return render(request, '/apps/web_01/modal/content/content_detail_inventory_log.html', {
        'ingredient': ingredient,
        'logs': logs,
        'current_stock': current_stock,
        'latest_user': latest_user,
        'category_name': category_name
    })


class IngredientImportForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ['ingredient', 'change', 'note']
        labels = {
            'ingredient': 'Nguyên liệu',
            'change': 'Số lượng nhập',
            'note': 'Ghi chú',
        }
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control form-control-sm select2'}),
            'change': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
            'note': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.all().order_by('name')
        self.fields['change'].initial = 1


def import_ingredient(request):
    if request.method == 'POST':
        try:
            data = request.POST

            if isinstance(data, dict) and 'items' in data:
                items = data['items']

                # Kiểm tra trùng nguyên liệu
                ingredient_ids = [item['ingredient_id'] for item in items]
                if len(ingredient_ids) != len(set(ingredient_ids)):
                    return JsonResponse({'error': 'Không được nhập trùng nguyên liệu!'}, status=400)

                # Xử lý từng mục nhập kho
                print('items', items)
                for item in items:
                    ing_id = int(item['ingredient_id'])
                    change = int(item['quantity'])
                    note = item.get('note', '').strip()

                    # Lấy thông tin nguyên liệu
                    ingredient = Ingredient.objects.get(id=ing_id)

                    # Tạo log nhập kho
                    log = InventoryLog(
                        ingredient_id=ing_id,
                        change=change,
                        type='import',
                        note=note or f"Nhập kho ngày {timezone.now().strftime('%d/%m/%Y')}",
                        user=request.user,
                        stock_before=ingredient.quantity_in_stock
                    )
                    log.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Nhập kho thành công!'
                })
            else:
                # Xử lý form thông thường
                ingredient_ids = request.POST.getlist('ingredient[]')
                changes = request.POST.getlist('change[]')
                notes = request.POST.getlist('note[]')

                print('ingredient_ids', ingredient_ids)
                # Kiểm tra trùng nguyên liệu
                if len(ingredient_ids) != len(set(ingredient_ids)):
                    return JsonResponse({'error': 'Không được nhập trùng nguyên liệu!'}, status=400)

                for i in range(len(ingredient_ids)):
                    ing_id = int(ingredient_ids[i])
                    change = int(changes[i])
                    note = notes[i].strip()

                    # Lấy thông tin nguyên liệu
                    ingredient = Ingredient.objects.get(id=ing_id)

                    log = InventoryLog(
                        ingredient_id=ing_id,
                        change=change,
                        type='import',
                        note=note or f"Nhập kho ngày {timezone.now().strftime('%d/%m/%Y')}",
                        user=request.user,
                        stock_before=ingredient.quantity_in_stock
                    )
                    log.save()

                return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        ingredients = Ingredient.objects.all().order_by('name')
        return render(request, 'apps/web_01/modal/content/content_import_ingredient.html', {
            'ingredients': ingredients,
            'modal_id': 'importIngredientModal'
        })


def export_ingredient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else request.POST

            if isinstance(data, dict) and 'items' in data:
                items = data['items']

                # Kiểm tra trùng nguyên liệu
                ingredient_ids = [item['ingredient_id'] for item in items]
                if len(ingredient_ids) != len(set(ingredient_ids)):
                    return JsonResponse({'error': 'Không được xuất trùng nguyên liệu!'}, status=400)

                errors = []

                # Xử lý từng mục xuất kho
                for item in items:
                    ing_id = int(item['ingredient_id'])
                    change = int(item['quantity'])
                    note = item.get('note', '').strip()

                    # Lấy thông tin nguyên liệu
                    ingredient = Ingredient.objects.get(id=ing_id)

                    # Kiểm tra số lượng tồn kho
                    if ingredient.quantity_in_stock < change:
                        errors.append(f"Nguyên liệu '{ingredient.name}' không đủ số lượng để xuất (hiện có: {ingredient.quantity_in_stock} {ingredient.get_unit_display()})")
                        continue

                    # Tạo log xuất kho
                    log = InventoryLog(
                        ingredient_id=ing_id,
                        change=-change,  # Số âm cho xuất kho
                        type='export',
                        note=note or f"Xuất kho ngày {timezone.now().strftime('%d/%m/%Y')}",
                        user=request.user,
                        stock_before=ingredient.quantity_in_stock
                    )
                    log.save()

                if errors:
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    }, status=400)

                return JsonResponse({
                    'success': True,
                    'message': 'Xuất kho thành công!'
                })
            else:
                # Xử lý form thông thường
                ingredient_ids = request.POST.getlist('ingredient[]')
                changes = request.POST.getlist('change[]')
                notes = request.POST.getlist('note[]')

                # Kiểm tra trùng nguyên liệu
                if len(ingredient_ids) != len(set(ingredient_ids)):
                    return JsonResponse({'error': 'Không được xuất trùng nguyên liệu!'}, status=400)

                errors = []

                for i in range(len(ingredient_ids)):
                    ing_id = int(ingredient_ids[i])
                    change = int(changes[i])
                    note = notes[i].strip()

                    # Lấy thông tin nguyên liệu
                    ingredient = Ingredient.objects.get(id=ing_id)

                    # Kiểm tra số lượng tồn kho
                    if ingredient.quantity_in_stock < change:
                        errors.append(f"Nguyên liệu '{ingredient.name}' không đủ số lượng để xuất (hiện có: {ingredient.quantity_in_stock} {ingredient.get_unit_display()})")
                        continue

                    log = InventoryLog(
                        ingredient_id=ing_id,
                        change=-change,  # Số âm cho xuất kho
                        type='export',
                        note=note or f"Xuất kho ngày {timezone.now().strftime('%d/%m/%Y')}",
                        user=request.user,
                        stock_before=ingredient.quantity_in_stock
                    )
                    log.save()

                if errors:
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    }, status=400)

                return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        ingredients = Ingredient.objects.all().order_by('name')
        return render(request, 'apps/web_01/modal/content/content_export_ingredient.html', {
            'ingredients': ingredients,
            'modal_id': 'exportIngredientModal'
        })


def add_ingredient(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name').strip()
            unit = request.POST.get('unit')
            quantity = int(request.POST.get('quantity', 0))
            category_id = request.POST.get('category')

            # Kiểm tra tên nguyên liệu đã tồn tại chưa
            if Ingredient.objects.filter(name=name).exists():
                return JsonResponse({'error': f"Nguyên liệu '{name}' đã tồn tại"}, status=400)

            # # Lấy danh mục nếu có
            # category = None
            # if category_id:
            #     category = Ingredient.objects.get(id=category_id)

            # Tạo nguyên liệu mới
            ingredient = Ingredient.objects.create(
                name=name,
                unit=unit,
                quantity_in_stock=0,
            )

            # Tạo log nhập kho ban đầu nếu có số lượng
            if quantity > 0:
                InventoryLog.objects.create(
                    ingredient=ingredient,
                    change=quantity,
                    type='import',
                    note=f"Nhập kho ban đầu",
                    user=request.user,
                    stock_before=0
                )

            return JsonResponse({
                'success': True,
                'message': f"Đã tạo nguyên liệu '{name}'"
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Danh sách đơn vị tính
        units = Ingredient.UNIT_CHOICES
        # Danh sách danh mục

        return render(request, 'apps/web_01/modal/content/content_add_ingredient.html', {
            'units': units,
            'modal_id': 'addIngredientModal'
        })


def inventory_dashboard(request):
    """Hiển thị tổng quan về tồn kho"""
    # Tổng số nguyên liệu
    total_ingredients = Ingredient.objects.count()

    # Số nguyên liệu sắp hết (tồn kho <= 10)
    low_stock_ingredients = Ingredient.objects.filter(quantity_in_stock__lte=10).count()

    # Số nguyên liệu đã hết (tồn kho = 0)
    out_of_stock_ingredients = Ingredient.objects.filter(quantity_in_stock=0).count()

    # Số lượng nhập kho trong tháng hiện tại
    current_month = timezone.now().month
    current_year = timezone.now().year

    import_logs_this_month = InventoryLog.objects.filter(
        type='import',
        last_updated__month=current_month,
        last_updated__year=current_year
    )

    export_logs_this_month = InventoryLog.objects.filter(
        type='export',
        last_updated__month=current_month,
        last_updated__year=current_year
    )

    # Tổng số lượng nhập/xuất trong tháng
    total_import_this_month = import_logs_this_month.aggregate(total=Sum('change'))['total'] or 0
    total_export_this_month = abs(export_logs_this_month.aggregate(total=Sum('change'))['total'] or 0)

    # Top 5 nguyên liệu nhập nhiều nhất trong tháng
    top_import_ingredients = import_logs_this_month.values(
        'ingredient__name'
    ).annotate(
        total=Sum('change')
    ).order_by('-total')[:5]

    # Top 5 nguyên liệu xuất nhiều nhất trong tháng
    top_export_ingredients = export_logs_this_month.values(
        'ingredient__name'
    ).annotate(
        total=Sum('change')
    ).order_by('-total')[:5]

    context = {
        'total_ingredients': total_ingredients,
        'low_stock_ingredients': low_stock_ingredients,
        'out_of_stock_ingredients': out_of_stock_ingredients,
        'total_import_this_month': total_import_this_month,
        'total_export_this_month': total_export_this_month,
        'top_import_ingredients': top_import_ingredients,
        'top_export_ingredients': top_export_ingredients,
    }

    return render(request, 'apps/web_01/inventory/inventory_dashboard.html', context)


def inventory_report(request):
    """Báo cáo tồn kho theo thời gian"""
    # Lấy tham số từ request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    ingredient_id = request.GET.get('ingredient_id')

    # Xây dựng query
    logs_query = InventoryLog.objects.all()

    if start_date:
        logs_query = logs_query.filter(last_updated__gte=start_date)

    if end_date:
        logs_query = logs_query.filter(last_updated__lte=end_date)

    if ingredient_id:
        logs_query = logs_query.filter(ingredient_id=ingredient_id)

    # Tổng hợp dữ liệu theo ngày
    daily_summary = logs_query.values(
        'last_updated__date'
    ).annotate(
        import_total=Sum(Case(
            When(type='import', then=F('change')),
            default=0,
            output_field=DecimalField()
        )),
        export_total=Sum(Case(
            When(type='export', then=F('change')),
            default=0,
            output_field=DecimalField()
        ))
    ).order_by('last_updated__date')

    # Danh sách nguyên liệu để lọc
    ingredients = Ingredient.objects.all().order_by('name')

    context = {
        'daily_summary': daily_summary,
        'ingredients': ingredients,
        'selected_ingredient_id': ingredient_id,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'apps/web_01/inventory/inventory_report.html', context)


def ingredient_request(request):
    """Xử lý yêu cầu thêm nguyên liệu từ nhân viên"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name').strip()
            unit = request.POST.get('unit')
            quantity = int(request.POST.get('quantity', 1))
            note = request.POST.get('note', '').strip()

            # Tạo thông báo cho quản lý

            Notification.objects.create(
                user_id=1,  # ID của admin hoặc manager
                message=f"Yêu cầu thêm nguyên liệu mới: {name} ({quantity} {unit})",
                type='ingredient_request',
                data={
                    'name': name,
                    'unit': unit,
                    'quantity': quantity,
                    'note': note,
                    'requested_by': request.user.id,
                    'requested_by_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                }
            )

            return JsonResponse({
                'success': True,
                'message': 'Yêu cầu đã được gửi đến quản lý!'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Danh sách đơn vị tính
        units = Ingredient.UNIT_CHOICES

        return render(request, 'apps/web_01/modal/content/content_request_ingredient.html', {
            'units': units,
            'modal_id': 'requestIngredientModal'
        })


@login_required
def inventory_dashboard_stats(request):
    """API trả về thống kê tổng quan về kho hàng cho dashboard"""
    try:
        # Thời gian hiện tại
        now = timezone.now()

        # Thời gian 30 ngày trước
        thirty_days_ago = now - timedelta(days=30)

        # Thời gian 7 ngày trước
        seven_days_ago = now - timedelta(days=7)

        # Tổng số nguyên liệu
        total_ingredients = Ingredient.objects.count()

        # Phân loại tồn kho
        stock_levels = {
            'out_of_stock': Ingredient.objects.filter(quantity_in_stock=0).count(),
            'low_stock': Ingredient.objects.filter(quantity_in_stock__gt=0, quantity_in_stock__lte=10).count(),
            'medium_stock': Ingredient.objects.filter(quantity_in_stock__gt=10, quantity_in_stock__lte=50).count(),
            'high_stock': Ingredient.objects.filter(quantity_in_stock__gt=50).count(),
        }

        # Thống kê nhập xuất trong 30 ngày qua
        import_logs_30d = InventoryLog.objects.filter(
            type='import',
            last_updated__gte=thirty_days_ago
        )

        export_logs_30d = InventoryLog.objects.filter(
            type='export',
            last_updated__gte=thirty_days_ago
        )

        # Tổng số lượng nhập/xuất trong 30 ngày
        total_import_30d = import_logs_30d.aggregate(total=Sum('change'))['total'] or 0
        total_export_30d = abs(export_logs_30d.aggregate(total=Sum('change'))['total'] or 0)

        # Thống kê nhập xuất trong 7 ngày qua
        import_logs_7d = import_logs_30d.filter(last_updated__gte=seven_days_ago)
        export_logs_7d = export_logs_30d.filter(last_updated__gte=seven_days_ago)

        total_import_7d = import_logs_7d.aggregate(total=Sum('change'))['total'] or 0
        total_export_7d = abs(export_logs_7d.aggregate(total=Sum('change'))['total'] or 0)

        # Top 5 nguyên liệu nhập nhiều nhất trong 30 ngày
        top_import_ingredients = list(import_logs_30d.values(
            'ingredient__id', 'ingredient__name'
        ).annotate(
            total=Sum('change')
        ).order_by('-total')[:5])

        # Top 5 nguyên liệu xuất nhiều nhất trong 30 ngày
        top_export_ingredients = list(export_logs_30d.values(
            'ingredient__id', 'ingredient__name'
        ).annotate(
            total=Sum('change')
        ).order_by('-total')[:5])

        # Thống kê theo ngày trong 30 ngày qua
        daily_stats = []

        for i in range(30):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Nhập kho trong ngày
            day_import = InventoryLog.objects.filter(
                type='import',
                last_updated__gte=day_start,
                last_updated__lte=day_end
            ).aggregate(total=Sum('change'))['total'] or 0

            # Xuất kho trong ngày
            day_export = abs(InventoryLog.objects.filter(
                type='export',
                last_updated__gte=day_start,
                last_updated__lte=day_end
            ).aggregate(total=Sum('change'))['total'] or 0)

            daily_stats.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'import': day_import,
                'export': day_export
            })

        # Thống kê hoạt động gần đây
        recent_activities = list(InventoryLog.objects.select_related('ingredient', 'user')
                                 .order_by('-last_updated')[:10]
                                 .values(
            'id', 'ingredient__name', 'change', 'type',
            'note', 'last_updated', 'stock_before', 'stock_after'
        ))

        # Format lại thời gian
        for activity in recent_activities:
            activity['last_updated'] = activity['last_updated'].strftime('%Y-%m-%d %H:%M:%S')

        # Thống kê theo danh mục
        category_stats = []

        if hasattr(Ingredient, 'category'):
            category_stats = list(Ingredient.objects.values(
                'category__name'
            ).annotate(
                count=Count('id'),
                total_stock=Sum('quantity_in_stock')
            ).order_by('-count'))

        # Thống kê nguyên liệu sắp hết
        low_stock_items = list(Ingredient.objects.filter(
            quantity_in_stock__gt=0,
            quantity_in_stock__lte=10
        ).values('id', 'name', 'quantity_in_stock', 'unit')[:10])

        # Thống kê nguyên liệu đã hết
        out_of_stock_items = list(Ingredient.objects.filter(
            quantity_in_stock=0
        ).values('id', 'name', 'unit')[:10])

        # Tổng hợp dữ liệu
        data = {
            'total_ingredients': total_ingredients,
            'stock_levels': stock_levels,
            'import_export': {
                'total_import_30d': total_import_30d,
                'total_export_30d': total_export_30d,
                'total_import_7d': total_import_7d,
                'total_export_7d': total_export_7d,
            },
            'top_import_ingredients': top_import_ingredients,
            'top_export_ingredients': top_export_ingredients,
            'daily_stats': daily_stats,
            'recent_activities': recent_activities,
            'category_stats': category_stats,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
