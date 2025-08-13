from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import OpeningBalance
from django import forms
from supplier.models import Supplier
from customer.models import Customer
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class OpeningBalanceForm(forms.ModelForm):
    account_name = forms.ChoiceField(choices=[('Customer', 'Customer'), ('Supplier', 'Supplier')])  # Limited to two options
    sub_type = forms.ChoiceField(choices=[])  # Will be populated dynamically via JavaScript

    class Meta:
        model = OpeningBalance
        fields = ['financial_year', 'date', 'account_name', 'sub_type', 'debit', 'credit', 'action']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['financial_year'].label = "Financial Year"
        # No need to populate account_name choices here since it's set in the class
        self.fields['sub_type'].choices = []  # Keep empty for dynamic population

class OpeningBalanceListView(ListView):
    model = OpeningBalance
    template_name = 'opening_balance_list.html'
    context_object_name = 'opening_balances'

class OpeningBalanceCreateView(CreateView):
    model = OpeningBalance
    template_name = 'opening_balance_form.html'
    form_class = OpeningBalanceForm
    success_url = reverse_lazy('accounts:opening_balance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = None  # We'll handle rows via JavaScript
        context['customers'] = [c.customer_name for c in Customer.objects.all()]  # Pass customer names
        context['suppliers'] = [s.supplier_name for s in Supplier.objects.all()]  # Pass supplier names
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f"Opening Balance {self.object.account_name} - {self.object.financial_year} added successfully.")
        return redirect(self.success_url)