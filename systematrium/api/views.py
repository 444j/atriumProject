from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser 
from django.contrib.auth import get_user_model
from rest_framework import generics

from .models import Flight, Hotel, TourPackage, Booking, Destination, Notification
from .serializers import (
    FlightSerializer, 
    HotelSerializer, 
    TourPackageSerializer, 
    BookingSerializer, 
    DestinationSerializer,
    NotificationSerializer,
    MyTokenObtainPairSerializer,
    UserSerializer,
    RegisterSerializer
)
# Siguraduhin na ang permissions.py mo ay may IsAdminOnly at IsOperatorOnly
from .permissions import IsAdminOnly, IsOperatorOnly

User = get_user_model()

# --- HELPER LOGIC ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# --- INVENTORY VIEWSETS (Strictly for Operator) ---

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all().order_by('-id')
    serializer_class = DestinationSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']: return [permissions.AllowAny()]
        # REMOVED ADMIN: Tanging Operator na lang ang pwedeng mag-Add/Edit/Delete
        return [IsOperatorOnly()]

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().order_by('-id')
    serializer_class = FlightSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']: return [permissions.AllowAny()]
        # REMOVED ADMIN: CRUD is now exclusive to Operator
        return [IsOperatorOnly()]

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all().order_by('-id')
    serializer_class = HotelSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']: return [permissions.AllowAny()]
        # REMOVED ADMIN: CRUD is now exclusive to Operator
        return [IsOperatorOnly()]

class TourPackageViewSet(viewsets.ModelViewSet):
    queryset = TourPackage.objects.all().order_by('-id')
    serializer_class = TourPackageSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']: return [permissions.AllowAny()]
        # REMOVED ADMIN: CRUD is now exclusive to Operator
        return [IsOperatorOnly()]

# --- BOOKING VIEWSET (Strictly for Admin Management) ---

# ... (existing imports)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_permissions(self):
        # FIX: Allow BOTH Admin and Consultant to validate and see reports
        if self.action in ['validate_booking', 'report']: 
            from .permissions import IsConsultantOnly # Import here to avoid circularity if needed
            return [IsConsultantOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        booking = serializer.save(client=self.request.user)
        # Notify both Admins and Consultants about new bookings
        staff = User.objects.filter(role__in=['ADMIN', 'CONSULTANT'])
        for member in staff:
            Notification.objects.create(user=member, message=f"New booking from {self.request.user.username}!")

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Booking.objects.none()
            

        role = getattr(user, 'role', '')
        role = role.upper() if role else ''

        # FIX: Added 'CONSULTANT' here so the backend actually sends the data
        if role in ['ADMIN', 'CONSULTANT', 'OPERATOR']: 
            return Booking.objects.all().order_by('-booking_date')
    
        return Booking.objects.filter(client=user).order_by('-booking_date')

    @action(detail=True, methods=['patch'], url_path='validate')
    def validate_booking(self, request, pk=None):
        booking = self.get_object()
        # Ensure status is uppercase to match your filter logic
        new_status = request.data.get('status', '').upper()
        reason = request.data.get('rejection_reason', '')
        
        if new_status in ['APPROVED', 'REJECTED', 'CANCELLED', 'PENDING']:
            booking.status = new_status
            if new_status == 'REJECTED':
                booking.rejection_reason = reason
            
            booking.save()
            Notification.objects.create(user=booking.client, message=f"Booking {new_status}!")
            return Response({'message': f'Status updated to {new_status}'})
        return Response({'error': 'Invalid status'}, status=400)

    @action(detail=False, methods=['get'])
    def report(self, request):
        # FIX: Ensure we check for 'APPROVED' (uppercase) to match the database
        revenue_data = Booking.objects.filter(status__in=['APPROVED', 'CONFIRMED']).aggregate(total=Sum('total_price'))
        serializer = self.get_serializer(Booking.objects.all().order_by('-booking_date'), many=True)
        return Response({"revenue": revenue_data['total'] or 0, "all_data": serializer.data})
# --- NOTIFICATIONS ---

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        # This is the line that actually saves to the database
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'status': 'marked as read'}, status=200)
    
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # DEBUG: Check your terminal/console where Django is running
        print(f"DEBUG: User {user.username} has role: {user.role}")

        # Use .strip() and .upper() to avoid issues with spaces or casing
        if hasattr(user, 'role') and str(user.role).strip().upper() == 'ADMIN':
            return User.objects.all().order_by('-id')
        
        # If the check above fails, it returns this empty list (hence the '0' in UI)
        return User.objects.none()
    

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer