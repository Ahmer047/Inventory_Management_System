import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchased_products', '0033_auto_20250212_0631'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_sale_id', models.CharField(max_length=16, unique=True, editable=False)),
                ('product_name', models.CharField(editable=False, max_length=255)),
                ('category_id', models.IntegerField(editable=False)),
                ('category_name', models.CharField(editable=False, max_length=255)),
                ('return_quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('total_return_amount', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('return_reason', models.CharField(choices=[('Defective', 'Defective Product'), ('WrongItem', 'Wrong Item Received'), ('NotNeeded', 'Item Not Needed'), ('SizeMismatch', 'Size/Fit Issue'), ('QualityIssue', 'Quality Not As Expected'), ('Other', 'Other Reason')], max_length=20)),
                ('reason_description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product_ID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchased_products.products')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchased_products.sale')),
            ],
        ),
    ]
