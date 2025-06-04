from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Airline, Airport, Flight, CrewMember, CrewTeam, Ticket # Імпортуємо всі моделі

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')

    list_filter = ('role', 'is_staff', 'is_active')

admin.site.register(Airline)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(CrewMember)
admin.site.register(CrewTeam)
admin.site.register(Ticket)

# Register your models here.