from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),                 # The new "Super" role (Manage All)
        ('CONSULTANT', 'Travel Consultant'), # Rebranded from your old Admin
        ('OPERATOR', 'Operator'),
        ('CLIENT', 'Client'),
    )
    # Increased max_length to 15 to fit 'CONSULTANT'
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CLIENT')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    groups = models.ManyToManyField('auth.Group', related_name='api_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='api_user_permissions', blank=True)

class Destination(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_popular = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.country}"

class Flight(models.Model):
    airline = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    seat_availability = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False) 
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
    # If flight_number is None, it returns 'Unnamed Flight'
        return self.flight_number or f"Flight ID: {self.pk}"

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    description = models.TextField()
    room_type = models.CharField(max_length=100)
    room_availability = models.PositiveIntegerField()
    rate_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class TourPackage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    itinerary = models.TextField()
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_slots = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()
    image_url = models.URLField(max_length=500, blank=True, null=True)
    inclusion = models.TextField(null=True, blank=True)
    exclusion = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'), 
        ('APPROVED', 'Approved'), 
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected')
    )
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    tour = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    item_name = models.CharField(max_length=255, blank=True)
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    nights = models.IntegerField(default=1, null=True, blank=True)
    adult_count = models.IntegerField(default=1)
    children_count = models.IntegerField(default=0)
    infant_count = models.IntegerField(default=0)
    total_pax = models.IntegerField(default=1)
    travel_class = models.CharField(max_length=50, default='Economy', blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking {self.id} - {self.item_name}"

    def save(self, *args, **kwargs):
        # Check for previous status before saving
        old_instance = Booking.objects.filter(pk=self.pk).first()
        old_status = old_instance.status if old_instance else None

        super(Booking, self).save(*args, **kwargs)

        # TOTAL PAX to subtract/add
        pax_to_move = self.adult_count + self.children_count

        # Case 1: Just became APPROVED (Subtract from Inventory)
        if old_status != 'APPROVED' and self.status == 'APPROVED':
            if self.flight:
                self.flight.seat_availability -= pax_to_move
                self.flight.save()
            if self.hotel:
                self.hotel.room_availability -= 1
                self.hotel.save()
            if self.tour:
                self.tour.available_slots -= pax_to_move
                self.tour.save()

        # Case 2: Was APPROVED but now CANCELLED/REJECTED (Restore to Inventory)
        elif old_status == 'APPROVED' and self.status in ['CANCELLED', 'REJECTED']:
            if self.flight:
                self.flight.seat_availability += pax_to_move
                self.flight.save()
            if self.hotel:
                self.hotel.room_availability += 1
                self.hotel.save()
            if self.tour:
                self.tour.available_slots += pax_to_move
                self.tour.save()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)