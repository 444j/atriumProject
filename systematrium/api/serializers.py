from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Flight, Hotel, TourPackage, Booking, Destination, Notification

from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create user using create_user to ensure password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'client')
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role.lower() if self.user.role else 'client'
        data['username'] = self.user.username
        return data

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class TourPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPackage
        fields = [
            'id', 'title', 'description', 'itinerary', 'duration_days', 
            'price', 'max_slots', 'available_slots', 'image_url', 
            'inclusion', 'exclusion', 'start_date', 'end_date'
        ]

class BookingSerializer(serializers.ModelSerializer):
    # Idineklara itong mga ito...
    flight_details = FlightSerializer(source='flight', read_only=True)
    hotel_details = HotelSerializer(source='hotel', read_only=True)
    tour_details = TourPackageSerializer(source='tour', read_only=True)
    client_name = serializers.ReadOnlyField(source='client.username')

    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'client_name', 
            'hotel', 'hotel_details', 
            'flight', 'flight_details',  # 👈 Idinagdag para mawala ang error
            'tour', 'tour_details',      # 👈 Idinagdag para mawala ang error
            'item_name', 'status', 'booking_date', 
            'total_price', 'receipt_image', 'reference_number',
            'check_in', 'check_out', 'nights',
            'adult_count', 'children_count', 'infant_count', 
            'total_pax', 'travel_class',
            'rejection_reason'
        ]
        extra_kwargs = {
            'client': {'read_only': True},
            'status': {'read_only': True},
        }

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # We include 'role' so the frontend can filter by role type
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']