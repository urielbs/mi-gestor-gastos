from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

class Transaction(models.Model):
    CURRENCY_CHOICES = [('MXN', 'Peso Mexicano'), ('USD', 'Dólar'), ('EUR', 'Euro')]
    TYPE_CHOICES = [('INCOME', 'Ingreso'), ('EXPENSE', 'Gasto')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='MXN')
    description = models.TextField(blank=True)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.amount} {self.currency} - {self.description}"