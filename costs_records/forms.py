from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from .models import Company, Address, BankAccount, Invoice, ExchangeRate, Cost


class CostForm(forms.ModelForm):

    payment_date = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Cost
        fields = ['customer', 'supplier', 'cost_description', 'payment_date']

    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)

        self.fields['payment_date'].required = False
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


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = '__all__'


class InvoiceForm(forms.ModelForm):

    date = forms.DateField(widget=forms.SelectDateWidget)
    due_date = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Invoice
        fields = ['date', 'number', 'proforma', 'due_date', 'currency', 'gross_amount', 'net_amount', 'vat_rate',
                  'file', 'printed', 'in_optima']

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = False


            #
            # any(for field in forms.fields if fields is not None):
            #     ... form.save()
