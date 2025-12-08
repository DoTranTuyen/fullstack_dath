
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication import views
from authentication.ai_view import FoodSuggestionView
app_name = "api"
# primary path: /api/

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'table', views.TableViewSet, basename='table')
router.register(r'tables/reservations', views.TableReservationViewSet, basename='table_reservation')
router.register(r'book/tables/reservations', views.BookaTableViewSet, basename='book_table_reservation')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'invoices', views.InvoiceViewSet, basename='invoices')  # Thêm dòng này
router.register(r'categories', views.CategoryViewSet, basename='category')
urlpatterns = [
    path("auth/login/",  views.LoginView.as_view(), name='login'),
    path("auth/session/",  views.SessionView.as_view(), name='current_session'),
    path("end-session/",  views.EndSessionView.as_view(), name='end_session'),
    path("suggestion/",  FoodSuggestionView.as_view(), name='food_suggestion'),
    path("", include(router.urls)),
]
