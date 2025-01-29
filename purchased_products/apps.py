from django.apps import AppConfig


class PurchasedProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchased_products'


    def ready(self):
        import purchased_products.signals



class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchased_products'

    def ready(self):
        pass
        # # Import and connect the signal
        # import purchased_products.signals  # Replace 'sales' with your app name