from django.contrib import admin
from .models import ProductPricing, Products, category, PurchasedProducts
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
            obj.category_name = obj.category.name  # Assuming `name` is the field for category name
        super().save_model(request, obj, form, change)


admin.site.register(Products, adminProducts)


#============================================== Admin Purchased_Product View Model ==============================================#



class adminPurchasedProducts(admin.ModelAdmin):
    list_display=['purchased_invoice', 'product_id', 'product_name', 'price_per_unit', 'piece_quantity', 'category', 'supplier']
    search_fields = ['purchased_invoice','product_id', 'product_name',]
    list_filter = ['product_name', 'category', 'supplier']
    list_editable = ['product_name', 'price_per_unit', 'piece_quantity', 'category', 'supplier']
    readonly_fields = ('product_id',)
    list_per_page = 20


admin.site.register(PurchasedProducts, adminPurchasedProducts)





#============================================== Admin Product_Pricing View Model ==============================================#

class AdminProductPricing(admin.ModelAdmin):
    list_display = ['product_ID', 'product_name', 'profit_margin', 'sell_price']
    search_fields = ['product_ID', 'product_name', 'product_name']
    list_filter = ['product_name', 'profit_margin']
    list_editable = ['profit_margin', 'sell_price']
    readonly_fields = ('product_name', 'sell_price')  # Allow editing of product_ID
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        # Fetch product_name and calculate sell_price before saving
        if obj.product_ID:
            obj.product_name = obj.product_ID.product_name  # Fetch product_name
            purchased_product = obj.product_ID.purchased_products.first()
            if purchased_product:
                price_per_unit = purchased_product.price_per_unit
                obj.sell_price = price_per_unit + (price_per_unit * (obj.profit_margin / 100))
        super().save_model(request, obj, form, change)

admin.site.register(ProductPricing, AdminProductPricing)


# class AdminProductPricing(admin.ModelAdmin):
#     list_display = ['product_ID', 'product_name', 'category', 'profit_margin', 'sell_price']
#     search_fields = ['product_ID', 'product_name']
#     list_filter = ['product_name', 'category']
#     list_editable = ['profit_margin']
#     readonly_fields = ('product_name', 'sell_price')  # Allow editing of product_ID
#     list_per_page = 20

#     def save_model(self, request, obj, form, change):
#         # Fetch product_name and calculate sell_price before saving
#         if obj.product_ID:
#             obj.product_name = obj.product_ID.product_name  # Fetch product_name
#             purchased_product = obj.product_ID.purchased_products.first()
#             if purchased_product:
#                 price_per_unit = purchased_product.price_per_unit
#                 obj.sell_price = price_per_unit + (price_per_unit * (obj.profit_margin / 100))
#         super().save_model(request, obj, form, change)

# admin.site.register(ProductPricing, AdminProductPricing)
