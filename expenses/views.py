from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Category, Transaction
from .forms import TransactionForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # 1. REFERENCIA DE TIEMPO
    today = timezone.now()
    
    # 2. CAPTURAR SELECCIÓN DEL USUARIO (Viene de los selectores del HTML)
    # Si no hay selección, por defecto usamos el mes y año actuales
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    # 3. LÓGICA DEL FORMULARIO DE REGISTRO
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            print("✅ ¡Datos guardados con éxito!")
            # Redirigimos manteniendo el mes/año que el usuario estaba viendo
            return redirect(f'/dashboard/?month={selected_month}&year={selected_year}')
        else:
            print("❌ Errores en el formulario:", form.errors)
    else:
        form = TransactionForm(user=request.user)
    
    # 4. CÁLCULOS FILTRADOS POR LA SELECCIÓN
    # Sumamos todos los gastos (EXPENSE) del mes y año elegidos
    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE',
        date__month=selected_month, # <-- Usamos la selección
        date__year=selected_year    # <-- Usamos la selección
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 5. DATOS POR CATEGORÍA PARA LAS TARJETAS
    categories = Category.objects.filter(user=request.user)
    category_data = []
    for cat in categories:
        spent = Transaction.objects.filter(
            user=request.user, 
            category=cat, 
            type='EXPENSE',
            date__month=selected_month,
            date__year=selected_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        category_data.append({
            'name': cat.name,
            'budget': cat.monthly_budget,
            'spent': spent,
            'over_budget': spent > cat.monthly_budget
        })

    # 6. HISTORIAL Y DATOS PARA LOS SELECTORES DEL HTML
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Lista de meses para el menú desplegable
    months_list = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    # Rango de años (este año y los dos anteriores)
    years_list = range(today.year - 2, today.year + 1)

    return render(request, 'expenses/dashboard.html', {
        'category_data': category_data,
        'total_expenses': total_expenses,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months_list,
        'years': years_list,
        'form': form,
        'recent_transactions': recent_transactions,
    })