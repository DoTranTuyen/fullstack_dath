from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from web_01.models import Employee, WorkShift, ShiftRegistration
import datetime
import json


class WorkShiftManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/work_shifts/work_shifts_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Lấy danh sách nhân viên để hiển thị trong dropdown

        if hasattr(self.request.user, 'employee') and self.request.user.employee.role == 'staff':
            context['employees'] = Employee.objects.select_related('user').filter(user=self.request.user)
        else:
            context['employees'] = Employee.objects.select_related('user').all()

        # Lấy các loại ca làm việc
        context['shift_types'] = dict(WorkShift.SHIFT_TYPE_CHOICES)
        return context


@login_required
def work_shift_list(request):
    """API để lấy danh sách ca làm việc cho DataTable"""
    try:
        draw = int(request.POST.get("draw", 1))
        start = int(request.POST.get("start", 0))
        length = int(request.POST.get("length", 10))
        search_value = request.POST.get("search[value]", "").strip()

        # Lấy các tham số lọc
        filter_employee = request.POST.get("filter_employee", "").strip()
        filter_date_from = request.POST.get("filter_date_from", "").strip()
        filter_date_to = request.POST.get("filter_date_to", "").strip()
        filter_shift_type = request.POST.get("filter_shift_type", "").strip()
        filter_status = request.POST.get("filter_status", "").strip()

        # Xác định cột sắp xếp
        order_column_index = int(request.POST.get("order[0][column]", 0))
        order_dir = request.POST.get("order[0][dir]", "desc")

        column_mapping = {
            0: "id",
            1: "employee__user__username",
            2: "date",
            3: "shift_type",
            4: "time_start",
            5: "time_end",
            6: "notes",
        }
        order_column = column_mapping.get(order_column_index, "id")
        if order_dir == "desc":
            order_column = "-" + order_column

        # if hasattr(request.user,'employee') and request.user.employee.role == 'staff':
        #     work_shifts = WorkShift.objects.select_related('employee', 'employee__user').filter(employee=request.user.employee)
        # else:
        work_shifts = WorkShift.objects.select_related('employee', 'employee__user')
        # Query cơ bản

        # Áp dụng các bộ lọc
        if filter_employee:
            work_shifts = work_shifts.filter(employee_id=filter_employee)

        if filter_date_from:
            try:
                date_from = datetime.datetime.strptime(filter_date_from, '%Y-%m-%d').date()
                work_shifts = work_shifts.filter(date__gte=date_from)
            except ValueError:
                pass

        if filter_date_to:
            try:
                date_to = datetime.datetime.strptime(filter_date_to, '%Y-%m-%d').date()
                work_shifts = work_shifts.filter(date__lte=date_to)
            except ValueError:
                pass

        if filter_shift_type:
            work_shifts = work_shifts.filter(shift_type=filter_shift_type)

        if filter_status:
            if filter_status == 'checked_in':
                work_shifts = work_shifts.filter(time_start__isnull=False, time_end__isnull=True)
            elif filter_status == 'checked_out':
                work_shifts = work_shifts.filter(time_start__isnull=False, time_end__isnull=False)
            elif filter_status == 'not_checked':
                work_shifts = work_shifts.filter(time_start__isnull=True)

        # Tìm kiếm
        if search_value:
            work_shifts = work_shifts.filter(
                Q(employee__user__username__icontains=search_value) |
                Q(notes__icontains=search_value)
            )

        # Tổng số bản ghi trước khi phân trang
        total_count = work_shifts.count()

        # Sắp xếp và phân trang
        work_shifts = work_shifts.order_by("-created_at")[start:start + length]

        # Chuẩn bị dữ liệu cho response
        shift_types = dict(WorkShift.SHIFT_TYPE_CHOICES)

        work_shifts_data = []
        for index, shift in enumerate(work_shifts, start=start + 1):
            # Tính trạng thái chấm công
            status = "Chưa chấm công"
            status_class = "text-warning"
            if shift.time_start:
                if shift.time_end:
                    status = "Đã hoàn thành"
                    status_class = "text-success"
                else:
                    status = "Đang làm việc"
                    status_class = "text-primary"

            # Tính thời gian làm việc
            working_hours = ""
            if shift.time_start and shift.time_end:
                duration = shift.time_end - shift.time_start
                hours = duration.total_seconds() / 3600
                working_hours = f"{hours:.2f} giờ"

            work_shifts_data.append({
                "index": index,
                "id": shift.id,
                "employee_id": shift.employee_id,
                "employee_name": shift.employee.user.username,
                "date": shift.date.strftime('%d/%m/%Y'),
                "date_raw": shift.date.strftime('%Y-%m-%d'),
                "shift_type": shift.shift_type,
                "shift_type_display": shift_types.get(shift.shift_type, shift.shift_type),
                "time_start": shift.time_start.strftime('%H:%M:%S') if shift.time_start else None,
                "time_end": shift.time_end.strftime('%H:%M:%S') if shift.time_end else None,
                "working_hours": working_hours,
                "notes": shift.notes or "",
                "status": status,
                "status_class": status_class
            })

        return JsonResponse({
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": work_shifts_data
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def shift_registration_list(request):
    """API để lấy danh sách đăng ký ca làm việc cho DataTable"""
    try:
        draw = int(request.POST.get("draw", 1))
        start = int(request.POST.get("start", 0))
        length = int(request.POST.get("length", 10))
        search_value = request.POST.get("search[value]", "").strip()

        # Lấy các tham số lọc
        filter_employee = request.POST.get("filter_employee", "").strip()
        filter_date_from = request.POST.get("filter_date_from", "").strip()
        filter_date_to = request.POST.get("filter_date_to", "").strip()
        filter_shift_type = request.POST.get("filter_shift_type", "").strip()
        filter_status = request.POST.get("filter_status", "").strip()
        filter_is_off = request.POST.get("filter_is_off", "").strip()

        # Xác định cột sắp xếp
        order_column_index = int(request.POST.get("order[0][column]", 0))
        order_dir = request.POST.get("order[0][dir]", "desc")

        column_mapping = {
            0: "id",
            1: "employee__user__username",
            2: "date",
            3: "shift_type",
            4: "is_off",
            5: "status",
            6: "created_at",
        }
        order_column = column_mapping.get(order_column_index, "id")
        if order_dir == "desc":
            order_column = "-" + order_column

        # Query cơ bản

        if request.user.employee.role == 'staff':
            registrations = ShiftRegistration.objects.select_related('employee', 'employee__user').filter(employee=request.user.employee)
        else:
            registrations = ShiftRegistration.objects.select_related('employee', 'employee__user')

        print('registrations', registrations)
        # Áp dụng các bộ lọc
        # if filter_employee:
        #     registrations = registrations.filter(employee_id=filter_employee)

        # if filter_date_from:
        #     try:
        #         date_from = datetime.datetime.strptime(filter_date_from, '%Y-%m-%d').date()
        #         registrations = registrations.filter(date__gte=date_from)
        #     except ValueError:
        #         pass

        # if filter_date_to:
        #     try:
        #         date_to = datetime.datetime.strptime(filter_date_to, '%Y-%m-%d').date()
        #         registrations = registrations.filter(date__lte=date_to)
        #     except ValueError:
        #         pass

        # if filter_shift_type:
        #     registrations = registrations.filter(shift_type=filter_shift_type)

        # if filter_status:
        #     registrations = registrations.filter(status=filter_status)

        # if filter_is_off:
        #     is_off_value = filter_is_off == 'true'
        #     registrations = registrations.filter(is_off=is_off_value)

        # # Tìm kiếm
        # if search_value:
        #     registrations = registrations.filter(
        #         Q(employee__user__username__icontains=search_value) |
        #         Q(reason__icontains=search_value)
        #     )

        # Tổng số bản ghi trước khi phân trang
        total_count = registrations.count()

        # Sắp xếp và phân trang
        registrations = registrations.order_by("-created_at")[start:start + length]

        # Chuẩn bị dữ liệu cho response
        shift_types = dict(WorkShift.SHIFT_TYPE_CHOICES)
        status_types = dict(ShiftRegistration.STATUS_CHOICES)

        registrations_data = []
        for index, reg in enumerate(registrations, start=start + 1):
            registrations_data.append({
                "index": index,
                "id": reg.id,
                "employee_id": reg.employee_id,
                "employee_name": reg.employee.user.username,
                "date": reg.date.strftime('%d/%m/%Y'),
                "date_raw": reg.date.strftime('%Y-%m-%d'),
                "shift_type": reg.shift_type,
                "shift_type_display": shift_types.get(reg.shift_type, reg.shift_type),
                "is_off": reg.is_off,
                "is_off_display": "Nghỉ phép" if reg.is_off else "Đăng ký làm",
                "reason": reg.reason or "",
                "status": reg.status,
                "status_display": status_types.get(reg.status, reg.status),
                "created_at": reg.created_at.strftime('%d/%m/%Y %H:%M:%S')
            })

        return JsonResponse({
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": registrations_data
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def register_shift(request):
    """API để đăng ký ca làm việc hoặc đăng ký nghỉ"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        employee_id = request.POST.get('employee_id')
        date = request.POST.get('date')
        shift_type = request.POST.get('shift_type')
        is_off = request.POST.get('is_off') == 'true'
        reason = request.POST.get('reason', '')

        # Validate input
        if not all([employee_id, date, shift_type]):
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng điền đầy đủ thông tin'
            })

        # Chuyển đổi date string sang date object
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            })

        # Kiểm tra xem đã có đăng ký nào cho nhân viên, ngày và ca này chưa
        existing_registration = ShiftRegistration.objects.filter(
            employee_id=employee_id,
            date=date_obj,
            shift_type=shift_type
        ).first()

        if existing_registration:
            return JsonResponse({
                'success': False,
                'message': 'Đã có đăng ký cho ca làm việc này'
            })

        # Tạo đăng ký mới
        registration = ShiftRegistration.objects.create(
            employee_id=employee_id,
            date=date_obj,
            shift_type=shift_type,
            is_off=is_off,
            reason=reason,
            status='pending'  # Mặc định là chờ duyệt
        )

        return JsonResponse({
            'success': True,
            'message': 'Đăng ký thành công, đang chờ duyệt'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })


@login_required
def approve_registration(request):
    """API để duyệt hoặc từ chối đăng ký ca làm việc"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        user = request.user

        # if not (user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager']).exists()):
        #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền duyệt đăng ký ca làm việc'}, status=403)

        registration_id = request.POST.get('registration_id')
        status = request.POST.get('status')  # 'approved' hoặc 'rejected'

        # Validate input
        if not all([registration_id, status]) or status not in ['approved', 'rejected']:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            })

        # Lấy đăng ký
        registration = ShiftRegistration.objects.filter(id=registration_id).first()
        if not registration:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy đăng ký'
            })

        # Cập nhật trạng thái
        registration.status = status
        registration.save()

        # Nếu duyệt và không phải đăng ký nghỉ, tạo ca làm việc mới
        if status == 'approved' and not registration.is_off:
            # Kiểm tra xem đã có ca làm việc nào cho nhân viên, ngày và ca này chưa
            existing_shift = WorkShift.objects.filter(
                employee_id=registration.employee_id,
                date=registration.date,
                shift_type=registration.shift_type
            ).first()

            if not existing_shift:
                # Tạo ca làm việc mới
                WorkShift.objects.create(
                    employee_id=registration.employee_id,
                    date=registration.date,
                    shift_type=registration.shift_type,
                    notes=f"Tạo từ đăng ký #{registration.id}"
                )

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật trạng thái thành công'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })


@login_required
def check_in(request):
    """API để chấm công vào ca làm việc"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        shift_id = request.POST.get('shift_id')

        # Validate input
        if not shift_id:
            return JsonResponse({
                'success': False,
                'message': 'ID ca làm việc không hợp lệ'
            })

        # Lấy ca làm việc
        shift = WorkShift.objects.filter(id=shift_id).first()
        if not shift:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy ca làm việc'
            })

        # Kiểm tra xem đã chấm công vào chưa
        if shift.time_start:
            return JsonResponse({
                'success': False,
                'message': 'Đã chấm công vào ca làm việc này'
            })

        # Cập nhật thời gian bắt đầu
        shift.time_start = timezone.now()
        shift.save()

        return JsonResponse({
            'success': True,
            'message': 'Chấm công vào thành công',
            'time_start': shift.time_start.strftime('%H:%M:%S')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })


@login_required
def check_out(request):
    """API để chấm công ra ca làm việc"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})

    try:
        shift_id = request.POST.get('shift_id')

        # Validate input
        if not shift_id:
            return JsonResponse({
                'success': False,
                'message': 'ID ca làm việc không hợp lệ'
            })

        # Lấy ca làm việc
        shift = WorkShift.objects.filter(id=shift_id).first()
        if not shift:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy ca làm việc'
            })

        # Kiểm tra xem đã chấm công vào chưa
        if not shift.time_start:
            return JsonResponse({
                'success': False,
                'message': 'Chưa chấm công vào ca làm việc này'
            })

        # Kiểm tra xem đã chấm công ra chưa
        if shift.time_end:
            return JsonResponse({
                'success': False,
                'message': 'Đã chấm công ra ca làm việc này'
            })

        # Cập nhật thời gian kết thúc
        shift.time_end = timezone.now()
        shift.save()

        # Tính thời gian làm việc
        duration = shift.time_end - shift.time_start
        hours = duration.total_seconds() / 3600

        return JsonResponse({
            'success': True,
            'message': 'Chấm công ra thành công',
            'time_end': shift.time_end.strftime('%H:%M:%S'),
            'working_hours': f"{hours:.2f} giờ"
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })
