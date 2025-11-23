# context_processors.py


def cloudinary_settings(request):
    from django.conf import settings
    return {
        "cloud_name": settings.CLOUDINARY_STORAGE["CLOUD_NAME"],
    }



def role_flags(request):
    if request.user.is_authenticated and hasattr(request.user, 'employee'):
        role = request.user.employee.role
    else:
        role = None

    return {
        'is_superuser': request.user.is_authenticated and request.user.is_superuser,
        'is_manager': role == 'manager' or request.user.is_superuser,
        'is_staff': role in ['manager', 'staff'] or request.user.is_superuser,
        'is_chef': role == 'chef' or request.user.is_superuser,
    }
    
