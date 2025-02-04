from django.db import models
from suppliers.models import supplier
import random
import string

# Create your models here.

#============================================== category Model ==============================================#

class category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name
    
#============================================== Products Model ==============================================#

class Products(models.Model):
    product_ID = models.IntegerField(primary_key=True)  # Change from AutoField to IntegerField for user input
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(category, on_delete=models.CASCADE, related_name="products")
    category_name = models.CharField(max_length=255, editable=False)  # Store category name

    def save(self, *args, **kwargs):
        # Automatically update category_name before saving
        if self.category:
            self.category_name = self.category.category_name  # Assuming `name` is the category field name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_ID}"  # Using f-string to properly convert to string


#============================================== Purchased_Products Model ==============================================#

class PurchasedProducts(models.Model):
    purchased_invoice = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="purchased_products")
    product_name = models.CharField(max_length=255, editable=False)  # Made read-only
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    piece_quantity = models.PositiveIntegerField()
    category = models.ForeignKey(category, on_delete=models.CASCADE, related_name="purchased_products", editable=False)  # Made read-only
    supplier = models.ForeignKey(supplier, on_delete=models.CASCADE, related_name="purchased_products")

    def save(self, *args, **kwargs):
        # Auto-populate fields from Product
        if self.product:
            self.product_name = self.product.product_name
            self.category = self.product.category
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


#============================================== Product_Pricing Model ==============================================#

class ProductPricing(models.Model):
    product_ID = models.ForeignKey('Products', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)  # Comes from the Products table
    category_id = models.IntegerField(editable=False)  # New field for category ID
    category_name = models.CharField(max_length=255, editable=False)  # New field for category name
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage profit margin
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)  # Calculated sell price
    is_current = models.BooleanField(default=False)  # Add this line

    def save(self, *args, **kwargs):
        # Automatically fetch product_name, category_id, category_name and calculate sell_price before saving
        if self.product_ID:
            self.product_name = self.product_ID.product_name
            self.category_id = self.product_ID.category.category_id  # Fetch category_id
            self.category_name = self.product_ID.category.category_name  # Fetch category_name
            price_per_unit = self.product_ID.purchased_products.order_by('-purchased_invoice').first().price_per_unit
            self.sell_price = price_per_unit + (price_per_unit * (self.profit_margin / 100))
            # print(price_per_unit)
            # print(self.profit_margin)            
            # print(self.sell_price)
        super(ProductPricing, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - Sell Price: {self.sell_price}"
    


#============================================== Stock Model ==============================================#

class Stock(models.Model):
    product_ID = models.ForeignKey('Products', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, editable=False)  # Save product name
    category_id = models.IntegerField(editable=False)  # Category ID
    category_name = models.CharField(max_length=255, editable=False)  # Category Name
    available_stock = models.PositiveIntegerField()  # Available pieces in stock
    current_sell_price = models.DecimalField(max_digits=10, decimal_places=2)  # Latest sell price

    def save(self, *args, **kwargs):
        # Automatically set product_name, current_sell_price, and category details
        if self.product_ID:
            self.product_name = self.product_ID.product_name
            latest_pricing = ProductPricing.objects.filter(product_ID=self.product_ID).order_by('-id').first()
            if latest_pricing:
                self.current_sell_price = latest_pricing.sell_price
                self.category_id = latest_pricing.category_id
                self.category_name = latest_pricing.category_name
        super(Stock, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - Available Stock: {self.available_stock} - Sell Price: {self.current_sell_price} - Category: {self.category_name}"


#============================================== Sales Model ==============================================#

class Sale(models.Model):
    SALE_ID_LENGTH = 16
    
    sale_id = models.CharField(max_length=SALE_ID_LENGTH)
    product_ID = models.ForeignKey('Products', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, editable=False)
    category_id = models.IntegerField(editable=False)
    category_name = models.CharField(max_length=255, editable=False)
    current_sell_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ) 
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Cash')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        stock_entry = Stock.objects.filter(product_ID=self.product_ID).first()
        if stock_entry:
            self.product_name = stock_entry.product_name
            self.category_id = stock_entry.category_id
            self.category_name = stock_entry.category_name
            self.current_sell_price = stock_entry.current_sell_price
            self.total = self.quantity * self.current_sell_price
        super(Sale, self).save(*args, **kwargs)

    def __str__(self):
        return f"Sale ID: {self.sale_id} - Product: {self.product_name} - Total: {self.total}"
    

#============================================== Return Sales Model ==============================================#


class ReturnSale(models.Model):
    RETURN_ID_LENGTH = 16
    return_sale_id = models.CharField(max_length=RETURN_ID_LENGTH, unique=True, editable=False)
    sale = models.ForeignKey('Sale', on_delete=models.PROTECT)
    product_ID = models.ForeignKey('Products', on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255, editable=False)
    category_id = models.IntegerField(editable=False)
    category_name = models.CharField(max_length=255, editable=False)
    return_quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_return_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    RETURN_REASONS = (
        ('Defective', 'Defective Product'),
        ('WrongItem', 'Wrong Item Received'),
        ('NotNeeded', 'Item Not Needed'),
        ('SizeMismatch', 'Size/Fit Issue'),
        ('QualityIssue', 'Quality Not As Expected'),
        ('Other', 'Other Reason'),
    )
    return_reason = models.CharField(max_length=20, choices=RETURN_REASONS)
    reason_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_return_id(self):
        chars = string.ascii_uppercase + string.digits
        while True:
            return_id = 'RET' + ''.join(random.choice(chars) for _ in range(self.RETURN_ID_LENGTH - 3))
            if not ReturnSale.objects.filter(return_sale_id=return_id).exists():
                return return_id
    
    
    def save(self, *args, **kwargs):
        # Generate return_sale_id if it doesn't exist
        if not self.return_sale_id:
            self.return_sale_id = self.generate_return_id()

        # Get original sale details
        try:
            # Find the sale with matching product
            if self.sale and self.product_ID:
                # Get the sale data directly from the sale object
                self.product_name = self.sale.product_name
                self.category_id = self.sale.category_id
                self.category_name = self.sale.category_name
                self.unit_price = self.sale.current_sell_price
                self.total_return_amount = self.return_quantity * self.unit_price
                
                # Validate return quantity against original sale
                if self.return_quantity > self.sale.quantity:
                    raise ValueError("Return quantity cannot be greater than original sale quantity")
            else:
                raise ValueError("Sale and Product information is required")
                
        except Exception as e:
            raise ValueError(f"Error processing return: {str(e)}")
            
        super(ReturnSale, self).save(*args, **kwargs)

    def __str__(self):
        return f"Return ID: {self.return_sale_id} - Product: {self.product_name} - Qty: {self.return_quantity}"
    


#============================================== Dummy Model for Analytics ==============================================#

class DashboardAnalytics(models.Model):
    """Dummy model for analytics dashboard"""
    title = models.CharField(max_length=200, default="Dashboard")
    
    class Meta:
        verbose_name_plural = "Dashboard Analytics"
        
    def __str__(self):
        return self.title
