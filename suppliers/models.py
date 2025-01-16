from django.db import models

# Create your models here.


class supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15)
    location = models.CharField(max_length=255)


    def __str__(self):
        return self.supplier_name
    

