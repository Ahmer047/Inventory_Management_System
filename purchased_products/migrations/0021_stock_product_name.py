# Generated by Django 5.1.4 on 2025-01-16 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0020_stock_category_id_stock_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='product_name',
            field=models.CharField(default=1, editable=False, max_length=255),
            preserve_default=False,
        ),
    ]