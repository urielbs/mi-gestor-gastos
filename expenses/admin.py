from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Columnas que verás en la lista
    list_display = ('name', 'user', 'monthly_budget')
    # Filtros laterales
    list_filter = ('user',)
    # Buscador
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'currency', 'type', 'category', 'date', 'user')
    list_filter = ('type', 'currency', 'date', 'user')
    search_fields = ('description',)