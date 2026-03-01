from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        # REVISA QUE ESTÉN ESTOS 6 NOMBRES EXACTOS:
        fields = ['description', 'amount', 'currency', 'type', 'category', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border p-2 rounded w-full'}),
            'description': forms.TextInput(attrs={'class': 'border p-2 rounded w-full'}),
            'amount': forms.NumberInput(attrs={'class': 'border p-2 rounded w-full'}),
            'currency': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),
            'type': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),
            'category': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)