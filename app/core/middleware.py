from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    EXCLUDED_PATHS = ['/accounts', '/admin', '/static', '/media', '/api', '/swagger']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Bỏ qua kiểm tra nếu đường dẫn nằm trong danh sách ngoại lệ
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            return self.get_response(request)

        # Nếu chưa đăng nhập => redirect về login
        if not request.user.is_authenticated:
            return redirect(reverse('web_01:login'))

        
        # if path.startswith('accounts/login/'):
             # bạn có thể đổi sang route phù hợp
        # Nếu là nhân viên và có role là 'chef' nhưng không ở trong trang chef => redirect
        # if hasattr(request.user, 'employee'):
        #     role = request.user.employee.role
        #     if role == 'chef' and not path.startswith('/chef'):
        #         # Tránh redirect loop nếu đã ở trang chef dashboard
        #         if path != reverse('web_01:chef_dashboard'):
        #             return redirect(reverse('web_01:chef_dashboard'))

        # Cho phép tiếp tục nếu hợp lệ
        return self.get_response(request)
