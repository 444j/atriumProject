from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FlightViewSet, 
    BookingViewSet, 
    HotelViewSet, 
    TourPackageViewSet, 
    DestinationViewSet,
    NotificationViewSet, # ✅ 1. Add this import
    MyTokenObtainPairView,
    UserViewSet,
    RegisterView,
)

router = DefaultRouter()
router.register(r'flights', FlightViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'tours', TourPackageViewSet)
router.register(r'destinations', DestinationViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # JWT Login Route
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    # API Routes
    path('', include(router.urls)),

]
#python -m venv venv
#venv\Scripts\activate