from django.contrib import admin
from .models import User

admin.site.site_header = "Inventory Managment System"
admin.site.site_title = "IMS"

class UserAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ['user_id', 'username', 'name', 'email', 'role', 'phone_no', 'status']
    # Fields to search in the admin interface
    search_fields = ['user_id', 'username', 'name']
    # Fields to filter by in the admin interface
    list_filter = ['status', 'role']
    # Fields to edit directly in the list view
    list_editable = ['name', 'email', 'role', 'phone_no', 'status']
    # Fields to show in the detail view and forms
    fields = ('username', 'name', 'email', 'role', 'phone_no', 'status')
    # Makes certain fields read-only (useful for auto-generated or immutable fields)
    readonly_fields = ('user_id',)
    # Enable pagination
    list_per_page = 20

    # Customize actions (e.g., bulk activate/deactivate users)
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(status='Active')
        self.message_user(request, "Selected users have been activated.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(status='Inactive')
        self.message_user(request, "Selected users have been deactivated.")
    deactivate_users.short_description = "Deactivate selected users"


# Register the customized admin interface
admin.site.register(User, UserAdmin)
