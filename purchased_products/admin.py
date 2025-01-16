from django.contrib import admin
from .models import ProductPricing, Products, Stock, category, PurchasedProducts
from django.forms import ValidationError
from django import forms


#============================================== Admin Category View Model ==============================================#

class categoryAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ['category_id', 'category_name']
    search_fields = ['category_id', 'category_name']
    #list_filter = ['category_name']
    list_editable = ['category_name']


admin.site.register(category, categoryAdmin)


#============================================== Admin Product View Model ==============================================#

# Custom form for validation
class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['product_ID', 'product_name', 'category']

    def clean_product_ID(self):
        product_ID = self.cleaned_data.get('product_ID')
        if Products.objects.filter(product_ID=product_ID).exists():
            raise ValidationError("Product with this ID already exists.")
        return product_ID


# Custom admin for Products
class adminProducts(admin.ModelAdmin):
    list_display = ['product_ID', 'product_name', 'category']
    list_display_links = ['product_name']  # Make 'product_name' the clickable link
    search_fields = ['product_ID', 'category', 'product_name']
    list_filter = ['product_name', 'category']
    list_editable = ['category']  # Keep 'product_name' editable if desired
    #readonly_fields = ('product_ID',)
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        # Ensure category_name is set before saving
        if obj.category:
            obj.category_name = obj.category.category_name  # Assuming `name` is the field for category name
        super().save_model(request, obj, form, change)


admin.site.register(Products, adminProducts)


#============================================== Admin Purchased_Product View Model ==============================================#

class PurchasedProductsAdmin(admin.ModelAdmin):
    list_display = ['purchased_invoice', 'product', 'product_name', 'price_per_unit', 
                    'piece_quantity', 'category', 'supplier']
    search_fields = ['purchased_invoice', 'product_name', 'category']
    list_filter = ['product__product_name', 'category', 'supplier']
    list_editable = ['product', 'price_per_unit', 'piece_quantity', 'supplier']
    readonly_fields = ('product_name', 'category')
    list_per_page = 20

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # If you need any form customization, add it here
        return form

    def save_model(self, request, obj, form, change):
        # Ensure fields are populated before saving
        if obj.product:
            obj.product_name = obj.product.product_name
            obj.category = obj.product.category
        super().save_model(request, obj, form, change)

admin.site.register(PurchasedProducts, PurchasedProductsAdmin)


#============================================== Admin Product_Pricing View Model ==============================================

class AdminProductPricing(admin.ModelAdmin):
    list_display = ['product_ID', 'product_name', 'category_id', 'category_name', 'profit_margin', 'sell_price']
    search_fields = ['product_ID', 'product_name', 'category_name']
    list_filter = ['category_name', 'profit_margin']
    list_editable = ['profit_margin', 'sell_price']
    readonly_fields = ('product_name', 'category_id', 'category_name', 'sell_price')  # Allow editing of other fields only
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        # Fetch product_name, category_id, category_name, and calculate sell_price before saving
        if obj.product_ID:
            obj.product_name = obj.product_ID.product_name  # Fetch product_name
            obj.category_id = obj.product_ID.category.category_id  # Fetch category_id
            obj.category_name = obj.product_ID.category.category_name  # Fetch category_name
            purchased_product = obj.product_ID.purchased_products.first()
            if purchased_product:
                price_per_unit = purchased_product.price_per_unit
                obj.sell_price = price_per_unit + (price_per_unit * (obj.profit_margin / 100))
        super().save_model(request, obj, form, change)

admin.site.register(ProductPricing, AdminProductPricing)



#============================================== Admin Stock View Model ==============================================#

from django.contrib import admin
from .models import Stock, ProductPricing

class StockAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'product_name', 'category_id', 'category_name', 'current_sell_price', 'available_stock')
    search_fields = ('product_ID__product_name', 'category_name')
    
    # Custom methods to fetch product_name, category_id, and category_name
    def product_name(self, obj):
        return obj.product_ID.product_name
    
    def current_sell_price(self, obj):
        # Get the latest sell price from ProductPricing
        latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
        if latest_pricing:
            return latest_pricing.sell_price
        return "N/A"

    def category_id(self, obj):
        # Get the category ID from ProductPricing
        latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
        if latest_pricing:
            return latest_pricing.category_id
        return "N/A"

    def category_name(self, obj):
        # Get the category name from ProductPricing
        latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
        if latest_pricing:
            return latest_pricing.category_name
        return "N/A"

    # Exclude fields that should not be manually edited
    exclude = ('current_sell_price', 'category_id', 'category_name')
    
    def save_model(self, request, obj, form, change):
        # Check if a Stock entry for the product_ID already exists
        existing_stock = Stock.objects.filter(product_ID=obj.product_ID).first()
        if existing_stock:
            # Update the existing stock entry
            existing_stock.available_stock += obj.available_stock  # Increment available stock
            latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
            if latest_pricing:
                existing_stock.current_sell_price = latest_pricing.sell_price
                existing_stock.category_id = latest_pricing.category_id
                existing_stock.category_name = latest_pricing.category_name
            existing_stock.save()
        else:
            # No existing entry, create a new one
            latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
            if latest_pricing:
                obj.current_sell_price = latest_pricing.sell_price
                obj.category_id = latest_pricing.category_id
                obj.category_name = latest_pricing.category_name
            super().save_model(request, obj, form, change)

# Register the Stock model in the admin
admin.site.register(Stock, StockAdmin)



# class StockAdmin(admin.ModelAdmin):
#     list_display = ('product_ID', 'product_name', 'current_sell_price', 'available_stock')
#     search_fields = ('product_ID__product_name',)
    
#     # Customize the form to show the dropdown and automatically fill the product_name and sell price
#     def product_name(self, obj):
#         return obj.product_ID.product_name
    
#     def current_sell_price(self, obj):
#         # Get the latest sell price from ProductPricing
#         latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#         if latest_pricing:
#             return latest_pricing.sell_price
#         return "N/A"
    
#     # Exclude the current_sell_price from the form to prevent asking for it
#     exclude = ('current_sell_price',)
    
#     def save_model(self, request, obj, form, change):
#         # Automatically set the current_sell_price before saving the model
#         latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#         if latest_pricing:
#             obj.current_sell_price = latest_pricing.sell_price
#         super().save_model(request, obj, form, change)

# admin.site.register(Stock, StockAdmin)
