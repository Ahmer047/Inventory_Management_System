from decimal import Decimal
from django.db.models.signals import post_save
from django.contrib.admin import ModelAdmin
from django.dispatch import receiver
from django.shortcuts import redirect
from .models import PurchasedProducts, ProductPricing, Stock
from django.db.models import Max


@receiver(post_save, sender=PurchasedProducts)
def create_or_update_product_pricing(sender, instance, created, **kwargs):
    try:
        # Find the latest ProductPricing entry for this product
        latest_existing_pricing = ProductPricing.objects.filter(
            product_ID=instance.product
        ).order_by('-id').first()

        # Fetch the latest PurchasedProducts entry for the product
        latest_purchased_product = PurchasedProducts.objects.filter(
            product=instance.product
        ).order_by('-purchased_invoice').first()

        if latest_purchased_product:
            price_per_unit = latest_purchased_product.price_per_unit
            print("++++++++++++++ ",price_per_unit)
            # Calculate sell price based on latest existing pricing's profit margin if exists
            profit_margin = latest_existing_pricing.profit_margin if latest_existing_pricing else Decimal('00.00')
            sell_price = price_per_unit + (price_per_unit * (profit_margin / 100))
            print("++++++++++++++ ",sell_price)

            # Mark all previous entries as non-current
            ProductPricing.objects.filter(
                product_ID=instance.product
            ).update(is_current=False)

            # Create a new ProductPricing entry
            ProductPricing.objects.create(
                product_ID=instance.product,
                product_name=instance.product_name,
                category_id=instance.category.category_id,
                category_name=instance.category.category_name,
                profit_margin=profit_margin,
                sell_price=sell_price,
                is_current=True
            )

            print("New Product Pricing entry created successfully")
            print("stored sell price ============= ",sell_price)

            # Add stock creation/update
        create_or_update_stock(
            product=instance.product, 
            piece_quantity=instance.piece_quantity
        )
    except Exception as e:
        print(f"Error in Product Pricing signal: {e}")



def create_or_update_stock(product, piece_quantity):
    # Find or create stock entry for the product
    stock, created = Stock.objects.get_or_create(
        product_ID=product,
        defaults={
            'product_name': product.product_name,
            'available_stock': piece_quantity
        }
    )
    
    # If not created, update existing stock
    if not created:
        stock.available_stock += piece_quantity
    
    # Get latest pricing
    latest_pricing = ProductPricing.objects.filter(
        product_ID=product, 
        is_current=True
    ).first()
    
    if latest_pricing:
        stock.current_sell_price = latest_pricing.sell_price
        stock.category_id = latest_pricing.category_id
        stock.category_name = latest_pricing.category_name
    
    stock.save()
    return stock

