from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.forms.fields import DateField
from .models import Company, Address, BankAccount, Invoice, ExchangeRate, Cost


class CostForm(forms.ModelForm):
    payment_date = forms.DateField(widget=DatePickerInput(), required=False)

    class Meta:
        model = Cost
        fields = ['customer', 'supplier', 'cost_description', 'estimated_cost', 'payment_date']
        # widgets = {
        #     'payment_date': DatePickerInput(),
        # }

    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)

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
    date = forms.DateField(widget=DatePickerInput(), required=False)
    due_date = forms.DateField(widget=forms.SelectDateWidget, required=False)

    class Meta:
        model = Invoice
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = False

    # def save(self, commit=True):
    #
    #     if any(field for field in self.fields if field is not None):
    #         self.instance.save()
    #
    #     super(InvoiceForm, self).save()

            #
            # any(for field in forms.fields if fields is not None):
            #     ... form.save()
