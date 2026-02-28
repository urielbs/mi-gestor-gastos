from django.shortcuts import render
from django.db.models import Sum
from .models import Category, Transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required

def dashboard(request):
    # Obtenemos el mes y año actual
    today = timezone.now()
    
    # Filtramos categorías del usuario logueado
    categories = Category.objects.filter(user=request.user)
    
    # Calculamos datos por cada categoría
    category_data = []
    total_expenses = 0
    
    for cat in categories:
        # Sumamos los gastos (EXPENSE) del mes actual para esta categoría
        spent = Transaction.objects.filter(
            user=request.user,
            category=cat,
            type='EXPENSE',
            date__month=today.month,
            date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Guardamos la info para el frontend
        category_data.append({
            'name': cat.name,
            'budget': cat.monthly_budget,
            'spent': spent,
            # Lógica para la alerta visual: ¿excedido?
            'over_budget': spent > cat.monthly_budget
        })
        total_expenses += spent

    return render(request, 'expenses/dashboard.html', {
        'category_data': category_data,
        'total_expenses': total_expenses,
        'month_name': today.strftime('%B')
    })