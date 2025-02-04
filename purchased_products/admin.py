from datetime import timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import DashboardAnalytics, ProductPricing, Products, Stock, category, PurchasedProducts, Sale, ReturnSale
from django.forms import ValidationError
from django import forms
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.db.models import Count, Sum


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


#============================================== Admin Sales View Model ==============================================#

class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_id', 'product_ID', 'product_name', 'quantity', 'current_sell_price', 'total', 'payment_method', 'created_at', 'category_id', 'category_name')
    list_filter = ('sale_id', 'payment_method', 'created_at')
    search_fields = ('sale_id', 'product_name')
    readonly_fields = ('product_name', 'category_id', 'category_name', 'current_sell_price', 'total')
    list_per_page = 20

    def actions_button(self, obj):
        return format_html(
            '<a class="button" href="{}">New Sale</a>',
            '/sales/create/'
        )
    actions_button.short_description = "Actions"

    def changelist_view(self, request, extra_context=None):
        # Calculate total sales
        total_sales = Sale.objects.aggregate(
            total_amount=Sum('total')
        )['total_amount'] or 0

        extra_context = extra_context or {}
        extra_context['total_sales'] = total_sales
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False  # Prevent manual addition through admin

admin.site.register(Sale, SaleAdmin)


#============================================== Admin Return Sales View Model ==============================================#


@admin.register(ReturnSale)
class ReturnSaleAdmin(admin.ModelAdmin):
    list_display = ('return_sale_id', 'sale', 'product_name', 'category_name', 
                   'return_quantity', 'total_return_amount', 'return_reason', 'created_at')
    list_filter = ('return_reason', 'category_name', 'created_at')
    search_fields = ('return_sale_id', 'sale__sale_id', 'product_name', 'reason_description')
    readonly_fields = ('return_sale_id', 'product_name', 'category_id', 
                      'category_name', 'unit_price', 'total_return_amount')
    
    fieldsets = (
        ('Return Information', {
            'fields': ('return_sale_id','sale')
        }),
        ('Product Details', {
            'fields': ('product_ID','product_name','category_id','category_name','unit_price')
        }),
        ('Return Details', {
            'fields': ('return_quantity','total_return_amount','return_reason','reason_description')
        })
    )

    def get_readonly_fields(self, request, obj=None):
        # Make all fields readonly if this is an existing object
        if obj:  # editing an existing object
            return self.readonly_fields + ('sale', 'product_ID', 'return_quantity', 
                                         'return_reason', 'reason_description')
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of returns older than 24 hours
        if obj and (timezone.now() - obj.created_at).days >= 1:
            return False
        return True

    def save_model(self, request, obj, form, change):
        try:
            if not change:  # New return sale
                # Validate return quantity against original sale
                if obj.return_quantity > obj.sale.quantity:
                    raise ValidationError(
                        f"Return quantity ({obj.return_quantity}) cannot be greater than "
                        f"original sale quantity ({obj.sale.quantity})"
                    )
                
                # Save the return sale - this will trigger our signal
                super().save_model(request, obj, form, change)
                
                # Add success message
                messages.success(
                    request, 
                    f'Return sale {obj.return_sale_id} created successfully. '
                    f'Stock updated with {obj.return_quantity} units.'
                )
            
            else:  # Existing return sale
                if (timezone.now() - obj.created_at).days < 1:
                    original_obj = ReturnSale.objects.get(pk=obj.pk)
                    
                    # Check if return quantity was modified
                    if original_obj.return_quantity != obj.return_quantity:
                        # Validate new return quantity
                        if obj.return_quantity > obj.sale.quantity:
                            raise ValidationError(
                                f"Return quantity ({obj.return_quantity}) cannot be greater than "
                                f"original sale quantity ({obj.sale.quantity})"
                            )
                    
                    super().save_model(request, obj, form, change)
                    messages.success(request, f'Return sale {obj.return_sale_id} updated successfully.')
                else:
                    messages.error(
                        request, 
                        'Cannot modify return sale after 24 hours of creation.'
                    )

        except ValidationError as e:
            messages.error(request, str(e))
            raise
        except Exception as e:
            messages.error(request, f'Error processing return sale: {str(e)}')
            raise

    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }


#============================================== Dashboard Analytics View Model ==============================================#


class DashboardAnalyticsAdmin(admin.ModelAdmin):
    """Admin class for analytics dashboard"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.dashboard_redirect_view, name='analytics-dashboard-redirect'),
            path('dashboard/', self.admin_dashboard_view, name='analytics-dashboard'),
            path('api/stock-data/', self.get_stock_data, name='stock-data'),
            path('api/category-data/', self.get_category_data, name='category-data'),
            path('api/sales-data/', self.get_sales_data, name='sales-data'),  # New endpoint
            path('api/sales-by-product/', self.get_sales_by_product, name='sales-by-product'),  # New endpoint
        ]
        return custom_urls + urls
    
    def dashboard_redirect_view(self, request):
        """Redirect from base URL to dashboard URL"""
        from django.shortcuts import redirect
        return redirect('admin:analytics-dashboard')


    def admin_dashboard_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Analytics Dashboard'
        }
        return TemplateResponse(request, 'admin/analytics_dashboard.html', context)
    
    def get_stock_data(self, request):
        # Get stock data for pie chart
        from .models import Stock
        stock_data = Stock.objects.values(
            'product_name'
        ).annotate(
            quantity=Sum('available_stock')
        ).filter(quantity__gt=0)
        
        return JsonResponse({
            'labels': [item['product_name'] for item in stock_data],
            'datasets': [{
                'data': [float(item['quantity']) for item in stock_data],
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
                ]
            }]
        })
    
    def get_category_data(self, request):
        # Get category-wise stock data for bar chart
        from .models import Stock
        category_data = Stock.objects.values(
            'category_name'
        ).annotate(
            total_items=Count('id'),
            total_quantity=Sum('available_stock')
        )
        
        return JsonResponse({
            'labels': [item['category_name'] for item in category_data],
            'datasets': [{
                'label': 'Total Quantity',
                'data': [float(item['total_quantity']) for item in category_data],
                'backgroundColor': '#36A2EB'
            }]
        })
    

    def get_sales_data(self, request):
        # Get sales data for the last 30 days
        from .models import Sale
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        sales_data = Sale.objects.filter(
            created_at__range=(start_date, end_date)
        ).values('created_at__date').annotate(
            total_sales=Sum('total')
        ).order_by('created_at__date')
        
        return JsonResponse({
            'labels': [item['created_at__date'].strftime('%Y-%m-%d') for item in sales_data],
            'datasets': [{
                'label': 'Total Sales',
                'data': [float(item['total_sales']) for item in sales_data],
                'backgroundColor': '#4BC0C0',
                'borderColor': '#4BC0C0',
                'fill': False
            }]
        })
    
    def get_sales_by_product(self, request):
        # Get sales data by product
        from .models import Sale
        sales_by_product = Sale.objects.values(
            'product_name'
        ).annotate(
            total_sales=Sum('total'),
            total_quantity=Sum('quantity')
        ).order_by('-total_sales')  # Sort by highest selling product

        return JsonResponse({
            'labels': [item['product_name'] for item in sales_by_product],
            'datasets': [{
                'label': 'Total Sales',
                'data': [float(item['total_sales']) for item in sales_by_product],
                'backgroundColor': '#FF6384',
                'borderColor': '#FF6384',
                'fill': False
            }]
        })
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition through admin
    
admin.site.register(DashboardAnalytics, DashboardAnalyticsAdmin)


#============================================== ****************************** ==============================================#

