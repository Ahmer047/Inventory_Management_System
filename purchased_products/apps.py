from django.apps import AppConfig


class PurchasedProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchased_products'
    
    def ready(self):
        try:
            import purchased_products.signals
        except ImportError:
            pass

