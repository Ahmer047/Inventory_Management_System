# Generated by Django 5.1.4 on 2025-01-14 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0008_productpricing'),
    ]

    operations = [
        migrations.AddField(
            model_name='productpricing',
            name='category',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
