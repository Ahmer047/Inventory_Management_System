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
            self.category_name = self.category.name  # Assuming `name` is the category field name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


#============================================== Purchased_Products Model ==============================================#

class PurchasedProducts(models.Model):
    purchased_invoice = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="purchased_products")
    product_name = models.CharField(max_length=255)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    piece_quantity = models.PositiveIntegerField()
    #profit_margin = models.PositiveIntegerField()
    category = models.ForeignKey(category, on_delete=models.CASCADE, related_name="purchased_products")
    supplier = models.ForeignKey(supplier, on_delete=models.CASCADE, related_name="purchased_products")

    def __str__(self):
        return self.product_name
    

#============================================== Product_Pricing Model ==============================================#

class ProductPricing(models.Model):
    product_ID = models.ForeignKey('Products', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)  # Comes from the Products table
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage profit margin
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)  # Calculated sell price

    def save(self, *args, **kwargs):
        # Automatically fetch product_name and calculate sell_price before saving
        if self.product_ID:
            self.product_name = self.product_ID.product_name
            price_per_unit = self.product_ID.purchased_products.first().price_per_unit
            self.sell_price = price_per_unit + (price_per_unit * (self.profit_margin / 100))
        super(ProductPricing, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - Sell Price: {self.sell_price}"
    
# class ProductPricing(models.Model):
#     product_ID = models.ForeignKey('Products', on_delete=models.CASCADE)
#     product_name = models.CharField(max_length=255)  # Comes from the Products table
#     category = models.CharField(max_length=255)  # Category field
#     profit_margin = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage profit margin
#     sell_price = models.DecimalField(max_digits=10, decimal_places=2)  # Calculated sell price

#     def save(self, *args, **kwargs):
#         # Automatically fetch product_name and category, then calculate sell_price
#         if self.product_ID:
#             self.product_name = self.product_ID.product_name
#             self.category = self.product_ID.category_id.name  # Assuming category_id is related to Category
#             price_per_unit = self.product_ID.purchased_products.first().price_per_unit
#             self.sell_price = price_per_unit + (price_per_unit * (self.profit_margin / 100))
#         super(ProductPricing, self).save(*args, **kwargs)












