from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Event, Registration

admin.site.register(User, UserAdmin)
admin.site.register(Category)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'category', 'max_capacity', 'created_by')
    list_filter = ('category', 'date')
    search_fields = ('title', 'venue')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'registered_at')
    list_filter = ('status', 'event')
    search_fields = ('user__username', 'event__title')
