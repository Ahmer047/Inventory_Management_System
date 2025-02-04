from decimal import Decimal
import logging
from django.db.models.signals import post_save
from django.contrib.admin import ModelAdmin
from django.dispatch import receiver
from django.shortcuts import redirect
from .models import PurchasedProducts, ProductPricing, ReturnSale, Stock, Sale
from django.db.models import Max
from django.db import transaction


logger = logging.getLogger(__name__)

########################################  Purchase item Signal #############################################

@receiver(post_save, sender=PurchasedProducts)
def create_or_update_product_pricing(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
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
                logger.info(f"Price per unit: {price_per_unit}")
                
                # Calculate sell price based on latest existing pricing's profit margin if exists
                profit_margin = latest_existing_pricing.profit_margin if latest_existing_pricing else Decimal('00.00')
                sell_price = price_per_unit + (price_per_unit * (profit_margin / 100))
                logger.info(f"Sell price calculated: {sell_price}")

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

                logger.info("New Product Pricing entry created successfully")

                # Add stock creation/update
                create_or_update_stock(
                    product=instance.product, 
                    piece_quantity=instance.piece_quantity
                )
    except Exception as e:
        logger.error(f"Error in Product Pricing signal: {e}")


def create_or_update_stock(product, piece_quantity):
    try:
        with transaction.atomic():
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
            logger.info(f"Stock updated for {product.product_name} with quantity {piece_quantity}")
            return stock
    except Exception as e:
        logger.error(f"Error in create_or_update_stock: {e}")



########################################  New Sale Signal #############################################



@receiver(post_save, sender=Sale)
def update_stock_on_sale(sender, instance, created, **kwargs):
    """
    Signal to update the stock quantity when a sale is made.
    """
    if created:  # Only trigger when a new Sale is created
        try:
            with transaction.atomic():
                stock = Stock.objects.select_for_update().get(product_ID=instance.product_ID)
                stock.available_stock -= instance.quantity
                stock.save()
        except Stock.DoesNotExist:
            logger.error(f"Stock not found for product {instance.product_ID}")
        except Exception as e:
            logger.error(f"Error updating stock on sale: {e}")


# @receiver(post_save, sender=Sale)
# def update_stock_on_sale(sender, instance, created, **kwargs):
#     """
#     Signal to update the stock quantity when a sale is made.
#     """
#     if created:  # Only trigger when a new Sale is created
#         product = instance.product_ID  # Get the product from the sale
#         stock = Stock.objects.filter(product_ID=product).first()  # Get the corresponding stock

#         if stock:
#             # Subtract the sold quantity from the available stock
#             stock.available_stock -= instance.quantity
#             stock.save()
        

########################################  Return Sale Signal #############################################


@receiver(post_save, sender=ReturnSale)
def update_stock_on_return(sender, instance, created, **kwargs):
    """
    Signal to update stock quantity when a return sale is created
    """
    if created:  # Only run on new return sale creation
        try:
            with transaction.atomic():
                # Get or create stock record for the product
                stock, created = Stock.objects.get_or_create(
                    product_ID=instance.product_ID,
                    defaults={
                        'available_stock': 0,
                        'product_name': instance.product_name,
                        'category_id': instance.category_id,
                        'category_name': instance.category_name,
                        'current_sell_price': instance.unit_price
                    }
                )
                
                # Update the available stock
                stock.available_stock += instance.return_quantity
                stock.save()
                
        except Exception as e:
            # Log the error - you might want to add proper logging here
            print(f"Error updating stock on return: {str(e)}")
            raise

