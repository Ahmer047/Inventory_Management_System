from django.db import models



class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=15)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.username
    
    