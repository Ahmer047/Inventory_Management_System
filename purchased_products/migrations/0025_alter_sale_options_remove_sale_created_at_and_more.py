# Generated by Django 5.1.4 on 2025-01-27 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0024_merge_20250127_0651'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={},
        ),
        migrations.RemoveField(
            model_name='sale',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='sale',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
