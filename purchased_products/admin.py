from decimal import ROUND_HALF_UP, Decimal
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ProductPricing, Products, Stock, category, PurchasedProducts
from django.forms import ValidationError
from django import forms
from django.shortcuts import redirect


#============================================== Admin Category View Model ==============================================#

class categoryAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ['category_id', 'category_name']
    search_fields = ['category_id', 'category_name']
    #list_filter = ['category_name']
    list_editable = ['category_name']


admin.site.register(category, categoryAdmin)


#============================================== Admin Product View Model ==============================================#

# # Custom form for validation
# class ProductsForm(forms.ModelForm):
#     class Meta:
#         model = Products
#         fields = ['product_ID', 'product_name', 'category']

#     def clean_product_ID(self):
#         product_ID = self.cleaned_data.get('product_ID')
#         if Products.objects.filter(product_ID=product_ID).exists():
#             raise ValidationError("Product with this ID already exists.")
#         return product_ID


# # Custom admin for Products
# class adminProducts(admin.ModelAdmin):
#     list_display = ['product_ID', 'product_name', 'category']
#     list_display_links = ['product_name']  # Make 'product_name' the clickable link
#     search_fields = ['product_ID', 'category', 'product_name']
#     list_filter = ['product_name', 'category']
#     list_editable = ['category']  # Keep 'product_name' editable if desired
#     #readonly_fields = ('product_ID',)
#     list_per_page = 20

#     def save_model(self, request, obj, form, change):
#         # Ensure category_name is set before saving
#         if obj.category:
#             obj.category_name = obj.category.category_name  # Assuming `name` is the field for category name
#         super().save_model(request, obj, form, change)


# admin.site.register(Products, adminProducts)


# Custom form for validation
class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['product_ID', 'product_name', 'category']  # Use exact model field names

    def clean_product_ID(self):
        product_ID = self.cleaned_data.get('product_ID')
        if Products.objects.filter(product_ID=product_ID).exists():
            raise ValidationError("A product with this ID already exists.")
        return product_ID


# Custom admin for Products
class AdminProducts(admin.ModelAdmin):
    form = ProductsForm  # Use the custom form for validation
    list_display = ['product_ID', 'product_name', 'category']  # Fields to display in the list view
    list_display_links = ['product_name']  # Make 'product_name' a clickable link
    search_fields = ['product_ID', 'category_name', 'product_name']  # Enable search by related category name
    list_filter = ['category_name']  # Filter by category name
    list_editable = ['category']  # Make the category field editable in the list view
    list_per_page = 20  # Pagination for admin list view

    def save_model(self, request, obj, form, change):
        # Set any derived fields before saving
        if obj.category:
            obj.category_name = obj.category.category_name  # Assuming `name` is the field for category name
        super().save_model(request, obj, form, change)


# Register the Products model and custom admin
admin.site.register(Products, AdminProducts)


#============================================== Admin Purchased_Product View Model ==============================================#    

class PurchasedProductsForm(forms.ModelForm):
    profit_margin = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        min_value=Decimal('0'), 
        max_value=Decimal('100'),
        label='Profit Margin (%)',
        initial=Decimal('10.00')  # Default value
    )

    class Meta:
        model = PurchasedProducts
        fields = '__all__'

class PurchasedProductsAdmin(admin.ModelAdmin):
    form = PurchasedProductsForm
    list_display = ['purchased_invoice', 'product', 'product_name', 'price_per_unit', 
                    'piece_quantity', 'category', 'supplier']
    search_fields = ['purchased_invoice', 'product__product_name', 'product__category__category_name']
    list_filter = ['product__product_name', 'product__category__category_name', 'supplier']
    list_editable = ['product', 'price_per_unit', 'piece_quantity', 'supplier']
    readonly_fields = ('product_name', 'category')
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        # Populate product_name and category fields
        if obj.product:
            obj.product_name = obj.product.product_name
            obj.category = obj.product.category
        
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # Create ProductPricing with the provided profit margin
        profit_margin = form.cleaned_data.get('profit_margin')
        
        # Calculate sell price
        price_per_unit = obj.price_per_unit
        sell_price = price_per_unit + (price_per_unit * (profit_margin / 100))

        # Mark all previous entries as non-current
        ProductPricing.objects.filter(
            product_ID=obj.product
        ).update(is_current=False)

        # Create a new ProductPricing entry
        ProductPricing.objects.create(
            product_ID=obj.product,
            product_name=obj.product_name,
            category_id=obj.category.category_id,
            category_name=obj.category.category_name,
            profit_margin=profit_margin,
            sell_price=sell_price,
            is_current=True
        )

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST or "_addanother" in request.POST:
            return super().response_add(request, obj, post_url_continue)

        # Redirect to ProductPricing changelist page
        product_pricing_url = reverse('admin:purchased_products_productpricing_changelist')
        return redirect(product_pricing_url)

admin.site.register(PurchasedProducts, PurchasedProductsAdmin)

# class PurchasedProductsAdmin(admin.ModelAdmin):
#     list_display = ['purchased_invoice', 'product', 'product_name', 'price_per_unit', 
#                     'piece_quantity', 'category', 'supplier']
#     search_fields = ['purchased_invoice', 'product__product_name', 'product__category__category_name']
#     list_filter = ['product__product_name', 'product__category__category_name', 'supplier']
#     list_editable = ['product', 'price_per_unit', 'piece_quantity', 'supplier']
#     readonly_fields = ('product_name', 'category')
#     list_per_page = 20

#     def get_form(self, request, obj=None, **kwargs):
#             form = super().get_form(request, obj, **kwargs)
#             # If you need any form customization, add it here
#             return form

#     def save_model(self, request, obj, form, change):
#         """
#         Override save_model to redirect to Product Pricing admin page
#         after saving a new PurchasedProducts entry.
#         """
#         # Populate product_name and category fields
#         if obj.product:
#             obj.product_name = obj.product.product_name
#             obj.category = obj.product.category
#         super().save_model(request, obj, form, change)


#     def response_add(self, request, obj, post_url_continue=None):
#         """
#         Redirect to ProductPricing admin page after adding a new PurchasedProducts entry.
#         """
#         if "_continue" in request.POST or "_addanother" in request.POST:
#             # If user chose to "Save and continue editing" or "Save and add another"
#             return super().response_add(request, obj, post_url_continue)

#         # Redirect to ProductPricing changelist page
#         product_pricing_url = reverse('admin:purchased_products_productpricing_changelist')
#         return redirect(product_pricing_url)


# admin.site.register(PurchasedProducts, PurchasedProductsAdmin)



#============================================== Admin Product_Pricing View Model ==============================================

class AdminProductPricing(admin.ModelAdmin):
    list_display = ['product_ID', 'product_name', 'category_id', 'category_name', 'profit_margin', 'sell_price']
    #search_fields = ['product_ID', 'product_name', 'category_name']
    search_fields = ['product_ID__product_name', 'product_ID__category__category_name']
    list_filter = ['category_name', 'profit_margin']
    list_editable = ['profit_margin', 'sell_price']
    readonly_fields = ('product_name', 'category_id', 'category_name', 'sell_price')  # Allow editing of other fields only
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        """
        Fetch product_name, category_id, category_name, and calculate sell_price before saving.
        Use the latest price_per_unit for calculations.
        """
        if obj.product_ID:
            obj.product_name = obj.product_ID.product_name  # Fetch product_name
            obj.category_id = obj.product_ID.category.category_id  # Fetch category_id
            obj.category_name = obj.product_ID.category.category_name  # Fetch category_name

            # Fetch the latest PurchasedProducts entry for the product
            #latest_purchased_product = obj.product_ID.purchased_products.first()
            latest_purchased_product = obj.product_ID.purchased_products.order_by('-purchased_invoice').first()
            print("=========================== >>>",latest_purchased_product)
            print(f"Profit Margin ======= >>>>> {obj.profit_margin}")
            if latest_purchased_product:
                price_per_unit = latest_purchased_product.price_per_unit
                print("=========================== >>>",price_per_unit)
                #print("=========================== >>>",price_per_unit)
                obj.sell_price = price_per_unit + (price_per_unit * (obj.profit_margin / 100))
                print(f"Sell Price ======= >>>>> {obj.sell_price}")
                sell_price = obj.sell_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                print(f"Calculated Sell Price: {sell_price}")
                obj.sell_price = sell_price
                print(f"Final sell_price type: {type(obj.sell_price)}")
                print(f"Final sell_price value: {obj.sell_price}")
                
        super().save_model(request, obj, form, change)


admin.site.register(ProductPricing, AdminProductPricing)



#============================================== Admin Stock View Model ==============================================#

class StockAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'product_name', 'category_id', 'category_name', 'current_sell_price', 'available_stock')
    search_fields = ('product_ID__product_name', 'category_name')
    
    # Exclude fields that should not be manually edited
    exclude = ('current_sell_price', 'category_id', 'category_name', 'product_name')
    
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
                existing_stock.product_name = obj.product_ID.product_name
            existing_stock.save()
        else:
            # No existing entry, create a new one
            obj.product_name = obj.product_ID.product_name
            latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
            if latest_pricing:
                obj.current_sell_price = latest_pricing.sell_price
                obj.category_id = latest_pricing.category_id
                obj.category_name = latest_pricing.category_name
            super().save_model(request, obj, form, change)

# Register the Stock model in the admin
admin.site.register(Stock, StockAdmin)


# class StockAdmin(admin.ModelAdmin):
#     list_display = ('product_ID', 'product_name', 'category_id', 'category_name', 'current_sell_price', 'available_stock')
#     search_fields = ('product_ID__product_name', 'category_name')
    
#     # Custom methods to fetch product_name, category_id, and category_name
#     def product_name(self, obj):
#         return obj.product_ID.product_name
    
#     def current_sell_price(self, obj):
#         # Get the latest sell price from ProductPricing
#         latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#         if latest_pricing:
#             return latest_pricing.sell_price
#         return "N/A"

#     def category_id(self, obj):
#         # Get the category ID from ProductPricing
#         latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#         if latest_pricing:
#             return latest_pricing.category_id
#         return "N/A"

#     def category_name(self, obj):
#         # Get the category name from ProductPricing
#         latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#         if latest_pricing:
#             return latest_pricing.category_name
#         return "N/A"

#     # Exclude fields that should not be manually edited
#     exclude = ('current_sell_price', 'category_id', 'category_name')
    
#     def save_model(self, request, obj, form, change):
#         # Check if a Stock entry for the product_ID already exists
#         existing_stock = Stock.objects.filter(product_ID=obj.product_ID).first()
#         if existing_stock:
#             # Update the existing stock entry
#             existing_stock.available_stock += obj.available_stock  # Increment available stock
#             latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#             if latest_pricing:
#                 existing_stock.current_sell_price = latest_pricing.sell_price
#                 existing_stock.category_id = latest_pricing.category_id
#                 existing_stock.category_name = latest_pricing.category_name
#             existing_stock.save()
#         else:
#             # No existing entry, create a new one
#             latest_pricing = ProductPricing.objects.filter(product_ID=obj.product_ID).order_by('-id').first()
#             if latest_pricing:
#                 obj.current_sell_price = latest_pricing.sell_price
#                 obj.category_id = latest_pricing.category_id
#                 obj.category_name = latest_pricing.category_name
#             super().save_model(request, obj, form, change)

# # Register the Stock model in the admin
# admin.site.register(Stock, StockAdmin)


#============================================== Admin Sales View Model ==============================================#


from django.contrib import admin
from .models import Sale

class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_id', 'product_ID', 'product_name', 'category_name', 'current_sell_price', 'quantity', 'total', 'payment_method')
    search_fields = ('sale_id', 'product_name', 'category_name')

    # Exclude fields that should not be manually edited
    exclude = ('product_name', 'category_id', 'category_name', 'current_sell_price', 'total')

    def save_model(self, request, obj, form, change):
        # Auto-populate fields from Stock before saving
        stock_entry = Stock.objects.filter(product_ID=obj.product_ID).first()
        if stock_entry:
            obj.product_name = stock_entry.product_name
            obj.category_id = stock_entry.category_id
            obj.category_name = stock_entry.category_name
            obj.current_sell_price = stock_entry.current_sell_price
            obj.total = obj.quantity * obj.current_sell_price
        super().save_model(request, obj, form, change)

# Register the Sale model in the admin
admin.site.register(Sale, SaleAdmin)
