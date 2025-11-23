from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


def admin_required(function):
    """Decorator để kiểm tra người dùng có quyền admin không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def manager_required(function):
    """Decorator để kiểm tra người dùng có quyền quản lý không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.employee.role in ['manager']):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def staff_required(function):
    """Decorator để kiểm tra người dùng có quyền nhân viên không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.employee.role in ['manager', 'staff']):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def chef_required(function):
    """Decorator để kiểm tra người dùng có quyền đầu bếp không"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.employee.role in ['chef', 'manager']):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap
