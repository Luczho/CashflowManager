from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.forms.fields import DateField
from .models import Company, Address, BankAccount, Invoice, ExchangeRate, Cost


class CostForm(forms.ModelForm):

    class Meta:
        model = Cost
        fields = ['category', 'customer', 'supplier', 'cost_description', 'estimated_cost', 'payment_date', 'asap', 'urgent']
        widgets = {
            'payment_date': forms.widgets.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)

        self.fields['payment_date'].required = False
        self.fields['asap'].required = False
        self.fields['urgent'].required = False
        self.fields['customer'].queryset = Company.objects.filter(is_contractor=False)
        self.fields['supplier'].queryset = Company.objects.filter(is_contractor=True)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['company']


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = '__all__'


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = "__all__"
        widgets = {
            'date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'due_date': forms.widgets.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = False
