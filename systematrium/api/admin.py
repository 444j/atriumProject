from django.contrib import admin # This was the missing line!
from django.contrib.auth.admin import UserAdmin
from .models import User, Flight, Hotel, TourPackage, Booking, Destination

# This makes your custom User manageable in the Admin panel
class CustomUserAdmin(UserAdmin):
    model = User
    # This adds 'role' to the list view so you can see who is an Admin/Operator/Client
    list_display = ['username', 'email', 'role', 'is_staff']
    
    # This adds the 'role' field to the edit page in Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone_number')}),
    )

# Registering your models so they show up in the dashboard
admin.site.register(User, CustomUserAdmin)
admin.site.register(Flight)
admin.site.register(Hotel)
admin.site.register(TourPackage)
admin.site.register(Booking)
admin.site.register(Destination)