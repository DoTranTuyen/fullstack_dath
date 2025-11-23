from django.shortcuts import redirect
from functools import wraps
from django.core.exceptions import PermissionDenied


def admin_required(function):
    """Decorator để kiểm tra người dùng có quyền admin không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return function(request, *args, **kwargs)
        
        print('123123')
        return redirect('web_01:service_list')
    return wrap


def manager_required(function):
    """Decorator để kiểm tra người dùng có quyền quản lý không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (hasattr(request.user, 'employee') and request.user.employee.role in ['manager'] or request.user.is_superuser):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def staff_required(function):
    """Decorator để kiểm tra người dùng có quyền nhân viên không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (hasattr(request.user, 'employee') and request.user.employee.role in ['manager', 'staff'] or request.user.is_superuser):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def chef_required(function):
    """Decorator để kiểm tra người dùng có quyền đầu bếp không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (hasattr(request.user, 'employee') and request.user.employee.role in ['chef'] or request.user.is_superuser):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap
