from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .CustomTokenAuthentication import CustomTokenAuthentication


class AuthenticationPermissionMixin:
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]
