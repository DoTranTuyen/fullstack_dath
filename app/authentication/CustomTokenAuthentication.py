from core.__Include_Library import *


class CustomTokenAuthentication(BaseAuthentication):
    """
    Xác thực người dùng bằng JWT token được lưu trong cookie `f1web_access_token`.
    """

    def authenticate(self, request):
        # Lấy token từ cookies
        token = request.COOKIES.get('rms_access_token', None)
        if not token:
            raise exceptions.AuthenticationFailed("Token không tồn tại trong cookie!")

        try:
            # Giải mã token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            res = Response()
            res.delete_cookie("rms_access_token")
            raise exceptions.AuthenticationFailed("Token đã hết hạn!")
        except jwt.DecodeError:
            res = Response()
            res.delete_cookie("rms_access_token")
            raise exceptions.AuthenticationFailed("Token không hợp lệ!")
        except Exception as e:
            res = Response()
            res.delete_cookie("rms_access_token")
            raise exceptions.AuthenticationFailed(f"Lỗi không xác định: {str(e)}")

        # Lấy người dùng dựa trên ID trong payload
        user = User.objects.filter(id=payload.get('id')).first()
        if user is None:
            raise exceptions.AuthenticationFailed("Người dùng không tồn tại!")

        return (user, None)

    def authenticate_header(self, request):
        """
        Tùy chọn thêm thông báo WWW-Authenticate vào header nếu cần.
        """
        return 'Bearer'
