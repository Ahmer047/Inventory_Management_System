# Generated by Django 5.1.4 on 2025-01-14 12:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0005_productpricing'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductPricing',
        ),
    ]
