from django.contrib import admin
from .models import supplier


class supplieradmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ['supplier_id', 'supplier_name', 'email', 'phone_no', 'location']
    # Fields to search in the admin interface
    search_fields = ['supplier_id', 'supplier_name']
    # Fields to filter by in the admin interface
    #list_filter = ['status', 'role']
    # Fields to edit directly in the list view
    list_editable = ['supplier_name', 'email', 'phone_no', 'location']
    # Fields to show in the detail view and forms
    #fields = ('username', 'name', 'email', 'role', 'phone_no', 'status')
    # Makes certain fields read-only (useful for auto-generated or immutable fields)
    readonly_fields = ('supplier_id',)
    # Enable pagination
    list_per_page = 20



admin.site.register(supplier, supplieradmin)
