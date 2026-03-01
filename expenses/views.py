from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Category, Transaction
from .forms import TransactionForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required

def dashboard(request):
    # Obtenemos el mes y año actual
    today = timezone.now()

    # LÓGICA DEL FORMULARIO
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user # Asignamos el gasto al usuario actual
            transaction.save()
            print("✅ ¡Datos guardados con éxito!") # Esto saldrá en tu terminal
            return redirect('dashboard') # Recargamos para ver el cambio
        else:
            print("❌ Errores en el formulario:", form.errors)
    else:
        form = TransactionForm(user=request.user)
    
    # 1. Calculamos el Total de forma independiente (Gasto real del mes)
    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE',
        date__month=today.month,
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 2. Datos por categoría para las tarjetas
    categories = Category.objects.filter(user=request.user)
    category_data = []
    for cat in categories:
        spent = Transaction.objects.filter(
            user=request.user, category=cat, type='EXPENSE',
            date__month=today.month, date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        category_data.append({
            'name': cat.name,
            'budget': cat.monthly_budget,
            'spent': spent,
            'over_budget': spent > cat.monthly_budget
        })

    # 3. Traemos los últimos 5 movimientos (SIN importar el mes)
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    return render(request, 'expenses/dashboard.html', {
        'category_data': category_data,
        'total_expenses': total_expenses,
        'month_name': today.strftime('%B'),
        'form': form,
        'recent_transactions': recent_transactions, # <-- Esto es nuevo
    })