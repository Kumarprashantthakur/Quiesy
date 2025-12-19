from django.contrib import admin
from .models import User , Quiz , Question
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)
admin.site.register(Quiz)
admin.site.register(Question)