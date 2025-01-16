from django.db import models
from suppliers.models import supplier


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

    def save(self, *args, **kwargs):
        # Automatically fetch product_name, category_id, category_name and calculate sell_price before saving
        if self.product_ID:
            self.product_name = self.product_ID.product_name
            self.category_id = self.product_ID.category.category_id  # Fetch category_id
            self.category_name = self.product_ID.category.category_name  # Fetch category_name
            price_per_unit = self.product_ID.purchased_products.first().price_per_unit
            self.sell_price = price_per_unit + (price_per_unit * (self.profit_margin / 100))
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


#============================================== Stock Model ==============================================#
    

