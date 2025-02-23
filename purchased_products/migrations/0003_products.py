# Generated by Django 5.1.4 on 2025-01-14 10:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0002_purchasedproducts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('product_ID', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=255)),
                ('available_pieces', models.PositiveIntegerField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='purchased_products.category')),
            ],
        ),
    ]
