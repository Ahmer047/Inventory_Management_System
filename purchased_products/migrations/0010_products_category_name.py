# Generated by Django 5.1.4 on 2025-01-14 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0009_productpricing_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='category_name',
            field=models.CharField(default=1, editable=False, max_length=255),
            preserve_default=False,
        ),
    ]