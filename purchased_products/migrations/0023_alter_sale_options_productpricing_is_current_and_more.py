# Generated by Django 5.1.4 on 2025-01-27 06:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0022_sale'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='productpricing',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sale',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sale',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
