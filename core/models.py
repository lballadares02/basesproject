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
    

class Category(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    provider_name = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    due_day = models.IntegerField()
    typical_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service_name


class Movement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    destination_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_movements'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    amount = models.BigIntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    movement_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
        return f"{self.amount} - {self.account}"
    
    class Meta:
        indexes = [
        models.Index(fields=['account']),
        models.Index(fields=['movement_date']),
        ]


