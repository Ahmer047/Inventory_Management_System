# Generated by Django 5.1.4 on 2025-01-27 07:33

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0025_alter_sale_options_remove_sale_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
