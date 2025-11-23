
from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from web_01.models import Table
from django import forms
from django.contrib.auth.decorators import login_required
from web_01.decorator import manager_required, staff_required


@method_decorator(staff_required, name='dispatch')
class TableManagementView(LoginRequiredMixin, TemplateView):

    template_name = 'apps/web_01/table/table_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_list'] = Table.objects.all()
        return context

    # def post(self, request, **kwargs):
    #     try:

    #     except json.JSONDecodeError:
    #         return HttpResponse(0)


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['status']  # Danh sách các trường cần nhập
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số bàn', 'disabled': 'disabled'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'qr_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


@login_required
def edit_table(request, id):
    """Xử lý chỉnh sửa bàn bằng AJAX"""
    table = get_object_or_404(Table, id=id)

    if request.method == "POST":
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "Cập nhật thành công!"}, status=200)
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # Nếu không phải POST request, render form như bình thường
    form = TableForm(instance=table)
    return render(request, 'apps/web_01/modal/content/content_edit_table.html', {'form': form, 'table_id': id})


def add_table(request):
    last_table_obj = Table.objects.last()
    Table.objects.create(table_number=last_table_obj.table_number + 1)
    return JsonResponse({"success": True, "message": "Thêm mới bàn thành công!"})


def table_qr(request, table_id):
    """Hiển thị mã QR của bàn"""
    table = get_object_or_404(Table, id=table_id)

    # Cập nhật QR nếu cần
    if request.method == 'POST':
        table.save(force_update_qr=True)
        messages.success(request, f"Đã cập nhật mã QR cho bàn số {table.table_number}")
        return JsonResponse({"success": True, "message": "Cập nhật má QR thành công!"}, status=200)

    # Kiểm tra nếu là AJAX request để hiển thị popup
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, '/apps/web_01/table/table_qr_popup.html', {'table': table})


def reset_all_qr(request):
    """Reset all QR code of tables"""
    for table in Table.objects.all():
        table.save(force_update_qr=True)
    # Table.objects.all().update(force_update_qr=True)
    messages.success(request, "Reset all QR code of tables successfully!")
    return redirect('web_01:table_list')


def table_create(request):
    """Tạo bàn mới"""
    # Kiểm tra nếu là AJAX request để hiển thị popup

    if request.method == 'POST':
        print('table_number11', 11)
        table_number = request.POST.get('table_number')
        capacity = request.POST.get('capacity', 4)  # Thêm trường capacity
        print('table_number', table_number)
        try:
            # Kiểm tra số bàn đã tồn tại chưa
            if Table.objects.filter(table_number=table_number).exists():
                messages.error(request, f"Bàn số {table_number} đã tồn tại")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Bàn số {table_number} đã tồn tại"
                    }, status=400)
                return redirect('web_01:manager_table_create')

            print('table_number2233')
            # Tạo bàn mới
            table = Table.objects.create(
                table_number=int(table_number),
                capacity=int(capacity),
                status='available'
            )

            messages.success(request, f"Đã tạo bàn số {table_number}")

            # Nếu là AJAX request, trả về JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f"Đã tạo bàn số {table_number}",
                    'table_id': table.id,
                    'table_number': table.table_number
                })

            return redirect('web_01:table_list')

        except Exception as e:
            messages.error(request, f"Lỗi khi tạo bàn: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': f"Lỗi khi tạo bàn: {str(e)}"
                }, status=500)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, '/apps/web_01/table/table_create_popup.html')
