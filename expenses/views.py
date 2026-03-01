from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Category, Transaction, FixedIncome
from .forms import TransactionForm, CategoryForm, EmailRegisterForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm

def index(request):
    # Si el usuario ya inició sesión, lo mandamos directo al Dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'expenses/index.html')

@login_required
def dashboard(request):
    # 1. REFERENCIA DE TIEMPO
    today = timezone.now()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    # 2. PROCESAR FORMULARIO (Si se guarda algo, redirigimos de inmediato)
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            # Redirigimos al mismo mes para ver el cambio reflejado
            return redirect(f'/dashboard/?month={selected_month}&year={selected_year}')
    else:
        form = TransactionForm(user=request.user)

    # 3. CÁLCULOS (Solo se ejecutan si NO hubo un POST, ahorrando energía del servidor)
    # Gastos del mes seleccionado
    total_expenses = Transaction.objects.filter(
        user=request.user, type='EXPENSE',
        date__month=selected_month, date__year=selected_year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Ingresos (Fijos + Variables del mes seleccionado)
    fixed_income_total = FixedIncome.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    variable_income_total = Transaction.objects.filter(
        user=request.user, type='INCOME',
        date__month=selected_month, date__year=selected_year
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = fixed_income_total + variable_income_total
    balance_neto = total_income - total_expenses

    # 4. DATOS POR CATEGORÍA
    categories = Category.objects.filter(user=request.user)
    category_data = []
    for cat in categories:
        spent = Transaction.objects.filter(
            user=request.user, category=cat, type='EXPENSE',
            date__month=selected_month, date__year=selected_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        category_data.append({
            'id': cat.id,
            'name': cat.name,
            'budget': cat.monthly_budget,
            'spent': spent,
            'over_budget': spent > cat.monthly_budget
        })

    # 5. HISTORIAL (Filtrado por el mismo mes para que coincida con los totales)
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        date__month=selected_month,
        date__year=selected_year
    ).order_by('-date')

    # Listas para selectores
    months_list = [(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')]
    years_list = range(today.year - 2, today.year + 1)
    selected_month_name = dict(months_list).get(selected_month)

    return render(request, 'expenses/dashboard.html', {
        'categories': categories,
        'category_data': category_data,
        'total_expenses': total_expenses,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_month_name': selected_month_name,
        'months': months_list,
        'years': years_list,
        'form': form,
        'recent_transactions': recent_transactions,
        'total_income': total_income,
        'fixed_income_total': fixed_income_total,
        'variable_income_total': variable_income_total,
        'balance_neto': balance_neto,
    })

@login_required
def delete_transaction(request, pk):
    # Buscamos la transacción por su ID (pk)
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    # Guardamos el mes y año antes de borrar para regresar a la misma vista
    month = transaction.date.month
    year = transaction.date.year
    
    if request.method == 'POST':
        transaction.delete()
        print(f"🗑️ Transacción {pk} eliminada con éxito")
        return redirect(f'/dashboard/?month={month}&year={year}')
    
    # Si alguien intenta entrar por accidente (GET), lo regresamos al dashboard
    return redirect('dashboard')


@login_required
def manage_categories(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'expenses/categories.html', {
        'categories': categories,
        'form': form
    })

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'expenses/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('manage_categories')
    return redirect('manage_categories')

def register(request):
    if request.method == 'POST':
        form = EmailRegisterForm(request.POST) 
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = EmailRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def manage_fixed_income(request):
    incomes = FixedIncome.objects.filter(user=request.user)
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        FixedIncome.objects.create(user=request.user, description=description, amount=amount)
        return redirect('manage_fixed_income')
    
    return render(request, 'expenses/fixed_income.html', {'incomes': incomes})

@login_required
def delete_fixed_income(request, pk):
    income = get_object_or_404(FixedIncome, pk=pk, user=request.user)
    income.delete()
    return redirect('manage_fixed_income')