from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name_1 = models.CharField(max_length=100)
    last_name_2 = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
    

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('ACTIVO', 'Activo'),
        ('PASIVO', 'Pasivo'),
        ('CAPITAL', 'Capital'),
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    currency = models.CharField(max_length=3)
    creation_date = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.account_name