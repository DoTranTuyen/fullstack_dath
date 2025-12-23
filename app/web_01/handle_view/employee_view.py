from core.__Include_Library import *
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F, ExpressionWrapper, DurationField, Case, When, FloatField, Value
from web_01.models import Employee, WorkShift, User
from django.utils import timezone
import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from web_01.management.commands.create_admins import upload_avatar_and_update_employee


class EmployeeManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/employee/employee_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 📌 Lấy danh sách nhân viên không bị xóa
        context['employee_list'] = Employee.objects.filter(is_deleted=False).select_related('user')
        return context

    def post(self, request, *args, **kwargs):
        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()

            filter_name = request.POST.get("filter_name", "").strip()
            filter_role = request.POST.get("filter_role", "").strip()
            filter_year = request.POST.get("filter_year")
            filter_month = request.POST.get("filter_month")

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "desc")

            column_mapping = {
                0: "user_id",
                1: "user__username",
                2: "email",
                3: "full_name",
                4: "role",
                5: "salary",
                6: "total_shifts",
                7: "total_hours",
                8: "actual_salary",
                9: "created_at"
            }
            order_column = column_mapping.get(order_column_index, "user_id")
            if order_dir == "desc":
                order_column = "-" + order_column

            now = timezone.now()
            year = int(filter_year) if filter_year else now.year
            month = int(filter_month) if filter_month else now.month

            start_date = datetime.date(year, month, 1)
            if month == 12:
                end_date = datetime.date(year + 1, 1, 1)
            else:
                end_date = datetime.date(year, month + 1, 1)

            employees = Employee.objects.select_related('user').filter(~Q(role__iexact='chef'), is_deleted=False)

            if filter_name:
                employees = employees.filter(user__username=filter_name)  # filter theo username chính xác

            if filter_role:
                employees = employees.filter(role=filter_role)

            if search_value:
                employees = employees.filter(
                    Q(user__username__icontains=search_value) |
                    Q(user__first_name__icontains=search_value) |
                    Q(user__last_name__icontains=search_value) |
                    Q(email__icontains=search_value) |
                    Q(full_name__icontains=search_value)
                )

            total_count = employees.count()
            employees = employees.order_by("-created_at")[start:start + length]

            from django.db.models import ExpressionWrapper, F, DurationField, FloatField

            employees_data = []
            for index, employee in enumerate(employees, start=start + 1):
                workshifts = employee.workshifts.filter(
                    date__gte=start_date,
                    date__lt=end_date,
                    time_start__isnull=False,
                    time_end__isnull=False
                ).annotate(
                    duration=ExpressionWrapper(
                        F('time_end') - F('time_start'),
                        output_field=DurationField()
                    )
                )

                total_hours = 0
                for ws in workshifts:
                    duration_seconds = ws.duration.total_seconds()
                    hours = duration_seconds / 3600
                    total_hours += hours

                total_shifts = 0
                if total_hours >= 8:
                    total_shifts = total_hours // 8
                    remainder = total_hours % 8
                    if remainder >= 4:
                        total_shifts += 0.5
                elif total_hours >= 4:
                    total_shifts = 0.5
                elif total_hours > 0:
                    total_shifts = 0.25

                hourly_rate = employee.salary / 176 if employee.salary else 0
                actual_salary = total_hours * hourly_rate

                employees_data.append({
                    "index": index,
                    "id": employee.user_id,
                    "username": employee.user.username,
                    "email": employee.email,
                    "full_name": employee.full_name,
                    "role": employee.role,
                    "salary": f"{employee.salary:,} VND",
                    "total_shifts": f"{total_shifts:.2f}",
                    "total_hours": f"{total_hours:.2f} giờ",
                    "actual_salary": f"{actual_salary:,.0f} VND",
                    "created_at": employee.user.date_joined.strftime('%d/%m/%Y') if hasattr(employee.user, 'date_joined') else ""
                })

            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": employees_data
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@login_required
def employee_add(request):
    """Thêm nhân viên mới"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        salary = request.POST.get('salary')
        role = request.POST.get('role', 'staff')  # Default to 'staff' if not provided
        total_shifts = request.POST.get('total_shifts', '0')
        total_hours = request.POST.get('total_hours', '0')

        # Validate input
        if not all([username, salary]):
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng điền đầy đủ thông tin'
            })

        # Convert salary to integer (remove commas)
        try:
            salary = int(salary.replace(',', ''))
            total_shifts = int(total_shifts)
            total_hours = float(total_hours.replace(' giờ', '').strip())
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            })

        # Check if user exists
        user = User.objects.filter(username=username, email=email).first()

        if user:
            return JsonResponse({
                'success': False,
                'message': 'Tên đăng nhập đã tồn tại'
            })

        if not user:
            # Create new user if not exists
            user = User.objects.create_user(
                username=username,
                first_name=username,
                email=email,
                password='123456',
                is_active=True
            )

        # Create employee
        employee = Employee.objects.create(
            full_name=full_name,
            email=email,
            user=user,
            salary=salary,
            role=role
        )
        upload_avatar_and_update_employee(user, '')

        # Create initial work shift with current date
        if total_shifts > 0:
            current_date = timezone.now().date()

            # Create shifts for the employee
            for i in range(total_shifts):
                shift_date = current_date - datetime.timedelta(days=i)
                WorkShift.objects.create(
                    employee=employee,
                    date=shift_date
                )

        return JsonResponse({
            'success': True,
            'message': 'Thêm nhân viên thành công'
        })

    except Exception as e:
        raw_message = str(e)
        clean_message = raw_message.split(":")[0]

        return JsonResponse({
            'success': False,
            'message': clean_message
        })


@login_required
def employee_update(request):
    """Cập nhật thông tin nhân viên"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        employee_id = request.POST.get('employee_id')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        salary = request.POST.get('salary')
        role = request.POST.get('role')  # Get role from form

        # Validate input
        if not all([employee_id, username, salary]):
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng điền đầy đủ thông tin'
            })

        # Convert salary to integer (remove commas)
        try:
            salary = int(salary.replace(',', ''))
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Lương không hợp lệ'
            })

        # Get employee
        employee = Employee.objects.filter(user_id=employee_id, is_deleted=False).first()
        if not employee:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhân viên'
            })

        # Update employee
        employee.salary = salary
        employee.email = email
        employee.full_name = full_name
        if role:
            employee.role = role  # Update role if provided
        employee.save()

        # Update user
        user = employee.user
        if user:
            user.username = username
            user.save()

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật nhân viên thành công'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })


@login_required
def employee_delete(request):
    """Xóa nhân viên (soft delete)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        employee_id = request.POST.get('employee_id')

        # Validate input
        if not employee_id:
            return JsonResponse({
                'success': False,
                'message': 'ID nhân viên không hợp lệ'
            })

        # Get employee
        employee = Employee.objects.filter(user_id=employee_id, is_deleted=False).first()
        if not employee:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhân viên'
            })

        # Soft delete employee
        employee.is_deleted = True
        employee.save()

        return JsonResponse({
            'success': True,
            'message': 'Xóa nhân viên thành công'
        })

    except Exception as e:
        print("🔥 Exception:", str(e))
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })
