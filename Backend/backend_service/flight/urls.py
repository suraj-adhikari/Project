from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FlightViewSet, RegisterView, LoginView, LogoutView, NotificationViewSet, index

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'flights', FlightViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', index, name="index"),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('flights/real-time/<str:flight_number>/', FlightViewSet.as_view({'get': 'get_real_time_flight_data'}), name='real_time_flight_data'),
]
