from core.__Include_Library import *
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from authentication.serializers import CategorySerializer
from web_01.models import Category


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(status='active')
    serializer_class = CategorySerializer

    # 📌 API danh mục con theo ID danh mục cha
    @action(detail=True, methods=['get'], url_path='subcategories')
    def subcategories(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk, status='active')
        subcategories = Category.objects.filter(parent=category, status='active')
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
